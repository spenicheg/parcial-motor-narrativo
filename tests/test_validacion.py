"""U4: los errores de contenido obligatorios producen rechazo con diagnóstico. Incluye CA03."""
import json

import pytest

from conftest import datos_transmision, escena, opcion
from motor_narrativo import ErrorContenido, cargar_historia, construir_historia, errores as E


def _quitar(d, campo):
    del d[campo]


# Cada caso: (descripción, mutación sobre los datos válidos, código esperado, texto que debe aparecer en la ubicación)
CASOS = [
    ("falta_titulo", lambda d: _quitar(d, "titulo"), E.CAMPO_AUSENTE, "historia"),
    ("falta_escenas", lambda d: _quitar(d, "escenas"), E.CAMPO_AUSENTE, "historia"),
    ("falta_texto_escena", lambda d: _quitar(escena(d, "E2"), "texto"), E.CAMPO_AUSENTE, "escena 'E2'"),
    ("falta_destino_opcion", lambda d: _quitar(opcion(d, "E1", "revisar"), "destino"), E.CAMPO_AUSENTE, "opción 'revisar'"),
    ("final_no_booleano", lambda d: escena(d, "E4").update(final="sí"), E.TIPO_INVALIDO, "escena 'E4' › final"),
    ("escenas_no_es_lista", lambda d: d.update(escenas={}), E.TIPO_INVALIDO, "historia › escenas"),
    ("inicio_inexistente", lambda d: d.update(inicio="E0"), E.INICIO_INEXISTENTE, "historia › inicio"),
    ("escena_duplicada", lambda d: escena(d, "E5").update(id="E4"), E.ESCENA_DUPLICADA, "escena 'E4'"),
    ("opcion_duplicada", lambda d: opcion(d, "E2", "continuar").update(id="investigar"), E.OPCION_DUPLICADA, "escena 'E2' › opción 'investigar'"),
    ("destino_inexistente", lambda d: opcion(d, "E3", "cortar").update(destino="E99"), E.DESTINO_INEXISTENTE, "opción 'cortar' › destino"),
    ("condicion_variable_no_declarada", lambda d: opcion(d, "E3", "cortar").update(condiciones={"tiene_radio": True}), E.VARIABLE_NO_DECLARADA, "condiciones › tiene_radio"),
    ("efecto_variable_no_declarada", lambda d: opcion(d, "E2", "investigar").update(efectos={"conoce_orgen": True}), E.VARIABLE_NO_DECLARADA, "efectos › conoce_orgen"),
    ("condicion_valor_no_booleano", lambda d: opcion(d, "E3", "activar_codigo").update(condiciones={"conoce_origen": "true"}), E.VALOR_NO_BOOLEANO, "condiciones › conoce_origen"),
    ("efecto_valor_no_booleano", lambda d: opcion(d, "E2", "investigar").update(efectos={"conoce_origen": 1}), E.VALOR_NO_BOOLEANO, "efectos › conoce_origen"),
    ("variable_inicial_no_booleana", lambda d: d["variables"].update(conoce_origen=0), E.VALOR_NO_BOOLEANO, "variables › conoce_origen"),
    ("final_con_opciones", lambda d: escena(d, "E4")["opciones"].append(dict(opcion(d, "E1", "revisar"))), E.FINAL_CON_OPCIONES, "escena 'E4'"),
    ("no_final_sin_opciones", lambda d: escena(d, "E1").update(opciones=[]), E.ESCENA_SIN_OPCIONES, "escena 'E1'"),
    ("opcion_no_es_objeto", lambda d: escena(d, "E1").update(opciones=["revisar"]), E.ESTRUCTURA_INVALIDA, "escena 'E1' › opciones[0]"),
]


@pytest.mark.parametrize("nombre, mutar, codigo, ubicacion", CASOS, ids=[c[0] for c in CASOS])
def test_U4_error_de_contenido_se_rechaza_con_diagnostico(nombre, mutar, codigo, ubicacion):
    datos = datos_transmision()
    mutar(datos)
    with pytest.raises(ErrorContenido) as exc:
        construir_historia(datos)
    problemas = [p for p in exc.value.problemas if p.codigo == codigo]
    assert problemas, f"se esperaba {codigo}, se obtuvo {exc.value.codigos}"
    assert any(ubicacion in p.ubicacion for p in problemas), [str(p) for p in problemas]
    assert all(p.mensaje for p in exc.value.problemas)


@pytest.mark.parametrize("contenido", ["[1, 2, 3]", "\"texto\"", "42"], ids=["lista", "cadena", "numero"])
def test_U4_raiz_con_estructura_incorrecta(tmp_path, contenido):
    f = tmp_path / "h.json"
    f.write_text(contenido, encoding="utf-8")
    with pytest.raises(ErrorContenido) as exc:
        cargar_historia(f)
    assert exc.value.codigos == {E.ESTRUCTURA_INVALIDA}


@pytest.mark.parametrize(
    "contenido, fragmento",
    [
        ('{"titulo": "x", ', "línea 1"),          # JSON truncado
        ("{'titulo': 'x'}", "JSON mal formado"),   # comillas simples
        (b"\xff\xfe\x00basura", "UTF-8"),          # bytes no UTF-8
        (None, "no existe"),                       # archivo ausente
    ],
    ids=["truncado", "comillas_simples", "no_utf8", "inexistente"],
)
def test_U4_archivo_ilegible(tmp_path, contenido, fragmento):
    f = tmp_path / "h.json"
    if isinstance(contenido, bytes):
        f.write_bytes(contenido)
    elif contenido is not None:
        f.write_text(contenido, encoding="utf-8")
    with pytest.raises(ErrorContenido) as exc:
        cargar_historia(f)
    [p] = exc.value.problemas
    assert p.codigo == E.ARCHIVO_ILEGIBLE and fragmento in p.mensaje and "h.json" in p.ubicacion


def test_CA03_destino_E99_rechaza_la_carga_sin_sesion(tmp_path):
    datos = datos_transmision()
    opcion(datos, "E3", "activar_codigo")["destino"] = "E99"
    f = tmp_path / "copia.json"
    f.write_text(json.dumps(datos, ensure_ascii=False), encoding="utf-8")
    historia = None
    with pytest.raises(ErrorContenido) as exc:
        historia = cargar_historia(f)
    assert historia is None  # no hay historia, por tanto no puede abrirse sesión
    [p] = exc.value.problemas
    assert p.codigo == E.DESTINO_INEXISTENTE
    assert "E99" in p.mensaje and "E3" in p.ubicacion and "activar_codigo" in p.ubicacion


def test_historia_de_referencia_es_valida():
    assert construir_historia(datos_transmision()).inicio == "E1"
