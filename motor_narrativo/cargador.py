"""Carga y validación de historias desde archivos JSON.

Responsabilidad única: convertir un archivo en un objeto Historia válido
o rechazarlo con la lista completa de problemas. No contiene reglas de juego
ni referencias a escenas o variables de ninguna historia concreta.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType
from typing import Any

from . import errores as E
from .errores import ErrorContenido, Problema
from .modelo import Escena, Historia, Opcion

CAMPOS_HISTORIA = {"titulo": str, "inicio": str, "variables": dict, "escenas": list}
CAMPOS_ESCENA = {"id": str, "texto": str, "final": bool, "opciones": list}
CAMPOS_OPCION = {"id": str, "texto": str, "destino": str, "condiciones": dict, "efectos": dict}

_NOMBRES_TIPO = {str: "texto", dict: "objeto {…}", list: "lista […]", bool: "booleano (true/false)"}
SEP = " › "


def cargar_historia(ruta: str | Path) -> Historia:
    """Lee, valida y construye la historia. Lanza ErrorContenido si no es válida."""
    return construir_historia(leer_json(ruta))


def leer_json(ruta: str | Path) -> Any:
    ruta = Path(ruta)
    try:
        with ruta.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        motivo = "el archivo no existe"
    except IsADirectoryError:
        motivo = "la ruta es una carpeta, no un archivo"
    except json.JSONDecodeError as e:
        motivo = f"JSON mal formado en línea {e.lineno}, columna {e.colno}: {e.msg}"
    except UnicodeDecodeError:
        motivo = "el archivo no está codificado en UTF-8"
    except OSError as e:
        motivo = f"no se pudo leer el archivo ({e.strerror})"
    raise ErrorContenido([Problema(E.ARCHIVO_ILEGIBLE, str(ruta), motivo)])


def construir_historia(datos: Any) -> Historia:
    problemas = validar(datos)
    if problemas:
        raise ErrorContenido(problemas)
    escenas = {}
    for esc in datos["escenas"]:
        opciones = tuple(
            Opcion(
                id=o["id"],
                texto=o["texto"],
                destino=o["destino"],
                condiciones=MappingProxyType(dict(o["condiciones"])),
                efectos=MappingProxyType(dict(o["efectos"])),
            )
            for o in esc["opciones"]
        )
        escenas[esc["id"]] = Escena(esc["id"], esc["texto"], esc["final"], opciones)
    return Historia(
        titulo=datos["titulo"],
        inicio=datos["inicio"],
        variables_iniciales=MappingProxyType(dict(datos["variables"])),
        escenas=MappingProxyType(escenas),
    )


def validar(datos: Any) -> list[Problema]:
    """Devuelve todos los problemas encontrados (lista vacía = historia válida)."""
    p: list[Problema] = []
    if not isinstance(datos, dict):
        return [Problema(E.ESTRUCTURA_INVALIDA, "(raíz del archivo)",
                         "debe ser un objeto JSON con los campos titulo, inicio, variables y escenas")]

    _revisar_campos(datos, CAMPOS_HISTORIA, "historia", p)

    variables = datos.get("variables") if isinstance(datos.get("variables"), dict) else {}
    for nombre, valor in variables.items():
        if type(valor) is not bool:
            p.append(Problema(E.VALOR_NO_BOOLEANO, f"variables{SEP}{nombre}",
                              f"el valor inicial debe ser true o false, se encontró {_mostrar(valor)}"))

    escenas = datos.get("escenas") if isinstance(datos.get("escenas"), list) else []
    ids_escena: set[str] = set()
    revisables: list[tuple[str, dict]] = []
    for i, esc in enumerate(escenas):
        ub = f"escenas[{i}]"
        if not isinstance(esc, dict):
            p.append(Problema(E.ESTRUCTURA_INVALIDA, ub, "cada escena debe ser un objeto {…}"))
            continue
        if isinstance(esc.get("id"), str):
            ub = f"escena '{esc['id']}'"
        _revisar_campos(esc, CAMPOS_ESCENA, ub, p)
        eid = esc.get("id")
        if isinstance(eid, str):
            if eid in ids_escena:
                p.append(Problema(E.ESCENA_DUPLICADA, ub, f"el id '{eid}' ya lo usa otra escena; los id de escena deben ser únicos"))
            ids_escena.add(eid)
        revisables.append((ub, esc))

    inicio = datos.get("inicio")
    if isinstance(inicio, str) and inicio not in ids_escena:
        p.append(Problema(E.INICIO_INEXISTENTE, f"historia{SEP}inicio", f"la escena inicial '{inicio}' no existe"))

    for ub, esc in revisables:
        _validar_opciones(ub, esc, ids_escena, variables, p)
    return p


def _validar_opciones(ub: str, esc: dict, ids_escena: set[str], variables: dict, p: list[Problema]) -> None:
    opciones = esc.get("opciones")
    if not isinstance(opciones, list):
        return
    final = esc.get("final")
    if final is True and opciones:
        p.append(Problema(E.FINAL_CON_OPCIONES, ub,
                          f"está marcada como final pero tiene {len(opciones)} opción(es); un final debe tener 0"))
    if final is False and not opciones:
        p.append(Problema(E.ESCENA_SIN_OPCIONES, ub,
                          "no es final y no tiene opciones; agregue al menos una o márquela con \"final\": true"))

    ids_opcion: set[str] = set()
    for j, op in enumerate(opciones):
        uo = f"{ub}{SEP}opciones[{j}]"
        if not isinstance(op, dict):
            p.append(Problema(E.ESTRUCTURA_INVALIDA, uo, "cada opción debe ser un objeto {…}"))
            continue
        if isinstance(op.get("id"), str):
            uo = f"{ub}{SEP}opción '{op['id']}'"
        _revisar_campos(op, CAMPOS_OPCION, uo, p)

        oid = op.get("id")
        if isinstance(oid, str):
            if oid in ids_opcion:
                p.append(Problema(E.OPCION_DUPLICADA, uo, f"el id '{oid}' se repite dentro de esta escena"))
            ids_opcion.add(oid)

        destino = op.get("destino")
        if isinstance(destino, str) and destino not in ids_escena:
            p.append(Problema(E.DESTINO_INEXISTENTE, f"{uo}{SEP}destino", f"la escena destino '{destino}' no existe"))

        for campo in ("condiciones", "efectos"):
            mapa = op.get(campo)
            if not isinstance(mapa, dict):
                continue
            for nombre, valor in mapa.items():
                donde = f"{uo}{SEP}{campo}{SEP}{nombre}"
                if nombre not in variables:
                    p.append(Problema(E.VARIABLE_NO_DECLARADA, donde,
                                      f"la variable '{nombre}' no está declarada en \"variables\""))
                if type(valor) is not bool:
                    p.append(Problema(E.VALOR_NO_BOOLEANO, donde,
                                      f"el valor debe ser true o false, se encontró {_mostrar(valor)}"))


def _revisar_campos(obj: dict, esquema: dict, ubicacion: str, p: list[Problema]) -> None:
    for campo, tipo in esquema.items():
        if campo not in obj:
            p.append(Problema(E.CAMPO_AUSENTE, ubicacion, f"falta el campo obligatorio '{campo}'"))
        elif not _es_tipo(obj[campo], tipo):
            p.append(Problema(E.TIPO_INVALIDO, f"{ubicacion}{SEP}{campo}",
                              f"se esperaba {_NOMBRES_TIPO[tipo]}, se encontró {_mostrar(obj[campo])}"))


def _es_tipo(valor: Any, tipo: type) -> bool:
    # En Python bool es subclase de int; aquí se exige el tipo exacto.
    return type(valor) is bool if tipo is bool else isinstance(valor, tipo)


def _mostrar(valor: Any) -> str:
    try:
        return json.dumps(valor, ensure_ascii=False)
    except (TypeError, ValueError):
        return repr(valor)
