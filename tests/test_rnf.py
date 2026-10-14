"""Verificación automatizada de los tres requisitos no funcionales (ver docs/requisitos.md).

RNF01 Modificabilidad del contenido
RNF02 Claridad de los errores de contenido
RNF03 Confiabilidad ante entradas incorrectas
Semilla fija => resultados reproducibles.
"""
import copy
import random
import re
from pathlib import Path

import pytest

from conftest import RAIZ, datos_transmision, escena, ids, opcion
from motor_narrativo import ErrorContenido, EstadoSesion, Sesion, construir_historia, errores as E
from motor_narrativo.cli import jugar

SEMILLA = 2026
MOTOR = RAIZ / "motor_narrativo"


# ---------------------------------------------------------------- RNF01
# Busca literales de código ("E3", 'conoce_origen'…) y nombres de variables de las historias.
IDENTIFICADORES_DE_HISTORIAS = re.compile(
    r"""["'](E\d+|F\d+|revisar|investigar|continuar|activar_codigo|activar_sin_verificar|cortar)["']"""
    r"|\b(conoce_origen|confia_en_la_voz|tiene_llave)\b")


def test_RNF01_motor_sin_identificadores_de_ninguna_historia():
    hallazgos = []
    for archivo in sorted(MOTOR.glob("*.py")):
        for n, linea in enumerate(archivo.read_text(encoding="utf-8").splitlines(), 1):
            if IDENTIFICADORES_DE_HISTORIAS.search(linea):
                hallazgos.append(f"{archivo.name}:{n}: {linea.strip()}")
    assert hallazgos == [], "El motor contiene identificadores de historias:\n" + "\n".join(hallazgos)


def test_RNF01_agregar_escena_y_cambiar_decision_solo_editando_datos():
    datos = datos_transmision()
    # La escritora agrega una escena intermedia y redirige una decisión.
    datos["escenas"].append({
        "id": "E2b", "texto": "Una segunda voz interrumpe la señal.", "final": False,
        "opciones": [{"id": "seguir", "texto": "Seguir escuchando", "destino": "E3",
                      "condiciones": {}, "efectos": {}}]})
    opcion(datos, "E2", "continuar")["destino"] = "E2b"
    s = Sesion(construir_historia(datos))
    for paso in ("revisar", "continuar", "seguir", "cortar"):
        assert s.elegir(paso).aceptada
    assert s.recorrido == ["E1", "E2", "E2b", "E3", "E6"]


# ---------------------------------------------------------------- RNF02
UN_ERROR_DE_CADA_TIPO = {
    E.CAMPO_AUSENTE: lambda d: escena(d, "E2").pop("texto"),
    E.TIPO_INVALIDO: lambda d: escena(d, "E4").update(final="no"),
    E.INICIO_INEXISTENTE: lambda d: d.update(inicio="E0"),
    E.ESCENA_DUPLICADA: lambda d: escena(d, "E5").update(id="E6"),
    E.OPCION_DUPLICADA: lambda d: opcion(d, "E2", "continuar").update(id="investigar"),
    E.DESTINO_INEXISTENTE: lambda d: opcion(d, "E1", "revisar").update(destino="E99"),
    E.VARIABLE_NO_DECLARADA: lambda d: opcion(d, "E3", "cortar").update(efectos={"radio": False}),
    E.VALOR_NO_BOOLEANO: lambda d: d["variables"].update(conoce_origen="falso"),
    E.FINAL_CON_OPCIONES: lambda d: escena(d, "E6")["opciones"].append(
        {"id": "x", "texto": "x", "destino": "E1", "condiciones": {}, "efectos": {}}),
    E.ESCENA_SIN_OPCIONES: lambda d: escena(d, "E1").update(opciones=[]),
}


def test_RNF02_todos_los_errores_se_reportan_en_una_sola_carga_con_codigo_y_ubicacion():
    datos = datos_transmision()
    for mutar in UN_ERROR_DE_CADA_TIPO.values():
        mutar(datos)
    with pytest.raises(ErrorContenido) as exc:
        construir_historia(datos)
    detectados = exc.value.codigos
    faltantes = set(UN_ERROR_DE_CADA_TIPO) - detectados
    assert not faltantes, f"no se reportaron en la misma carga: {faltantes}"
    for p in exc.value.problemas:
        texto = str(p)
        assert texto.startswith(f"[{p.codigo}] ")
        assert p.ubicacion and p.ubicacion != "?"
        assert len(p.mensaje) >= 15  # explica la causa, no solo un código


def test_RNF02_resumen_legible_para_escritores():
    datos = datos_transmision()
    opcion(datos, "E1", "revisar")["destino"] = "E99"
    with pytest.raises(ErrorContenido) as exc:
        construir_historia(datos)
    assert "Traceback" not in exc.value.resumen()
    assert exc.value.resumen().splitlines()[1].strip().startswith("1. [DESTINO_INEXISTENTE]")


# ---------------------------------------------------------------- RNF03
N_ENTRADAS = 2000
N_MUTACIONES = 500
BASURA = ["", " ", "0", "-1", "99", "abc", "1.5", "r", "s", None, 7, True, [], {}, "E3", "cortar", "\x00", "ñ" * 500]


def test_RNF03_entradas_aleatorias_del_lector_no_rompen_ni_alteran_el_estado():
    rnd = random.Random(SEMILLA)
    s = Sesion(construir_historia(datos_transmision()))
    rechazadas_que_alteraron = 0
    for _ in range(N_ENTRADAS):
        if s.estado is not EstadoSesion.EN_CURSO and rnd.random() < 0.5:
            s.reiniciar()
        candidatas = ids(s.opciones_disponibles()) + ["activar_codigo", "activar_sin_verificar"] + BASURA
        entrada = rnd.choice(candidatas + ["__deshacer__"] * 3)
        antes = (s.escena.id, s.variables, s.recorrido, s.puede_deshacer)
        # cualquier excepción aquí hace fallar la prueba
        r = s.deshacer() if entrada == "__deshacer__" else s.elegir(entrada)
        if not r.aceptada and (s.escena.id, s.variables, s.recorrido, s.puede_deshacer) != antes:
            rechazadas_que_alteraron += 1
    assert rechazadas_que_alteraron == 0


def test_RNF03_consola_no_se_cierra_ante_entradas_aleatorias():
    rnd = random.Random(SEMILLA)
    teclas = [rnd.choice(["1", "2", "3", "0", "", "x", "99", "-1", "r", " 1 ", "d", "D"]) for _ in range(N_ENTRADAS)]
    teclas[-1:] = ["s"]
    it = iter(teclas)
    salida: list[str] = []
    jugar(construir_historia(datos_transmision()), entrada=lambda _: next(it), salida=salida.append)
    assert salida[-1] == "Hasta pronto."


def _mutar_al_azar(datos, rnd):
    """Reemplaza o elimina un nodo aleatorio del JSON por un valor de tipo arbitrario."""
    nodos = []

    def recorrer(x):
        if isinstance(x, dict):
            for k in list(x):
                nodos.append((x, k)); recorrer(x[k])
        elif isinstance(x, list):
            for i in range(len(x)):
                nodos.append((x, i)); recorrer(x[i])
    recorrer(datos)
    contenedor, clave = rnd.choice(nodos)
    valor = rnd.choice([None, 0, 1, "x", "E99", True, [], {}, [1], {"a": 1}, "__borrar__"])
    if valor == "__borrar__":
        del contenedor[clave]
    else:
        contenedor[clave] = valor


def test_RNF03_contenido_corrupto_aleatorio_siempre_da_rechazo_controlado():
    rnd = random.Random(SEMILLA)
    base = datos_transmision()
    otras_excepciones = []
    rechazadas = 0
    for i in range(N_MUTACIONES):
        datos = copy.deepcopy(base)
        for _ in range(rnd.randint(1, 3)):
            _mutar_al_azar(datos, rnd)
        try:
            construir_historia(datos)
        except ErrorContenido:
            rechazadas += 1
        except Exception as e:  # noqa: BLE001 - justamente lo que se mide
            otras_excepciones.append(f"mutación {i}: {type(e).__name__}: {e}")
    assert otras_excepciones == []
    assert rechazadas > N_MUTACIONES * 0.8  # la mayoría de mutaciones deben detectarse
