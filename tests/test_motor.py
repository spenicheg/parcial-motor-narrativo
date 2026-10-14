"""Pruebas unitarias del motor (U1, U2, U3, U5 y bloqueo). Incluye CA01 y CA02."""
import pytest

from conftest import datos_transmision, escena, ids
from motor_narrativo import EstadoSesion, Sesion, construir_historia


def ir_a_E3(sesion, investigar: bool):
    assert sesion.elegir("revisar").aceptada
    assert sesion.elegir("investigar" if investigar else "continuar").aceptada


# ---------------------------------------------------------------- U1
@pytest.mark.parametrize(
    "investigar, esperadas",
    [
        (True, ["activar_codigo", "cortar"]),      # conoce_origen = true
        (False, ["activar_sin_verificar", "cortar"]),  # conoce_origen = false
    ],
    ids=["conoce_origen_verdadero", "conoce_origen_falso"],
)
def test_U1_condiciones_habilitan_solo_opciones_correspondientes(sesion, investigar, esperadas):
    ir_a_E3(sesion, investigar)
    assert sesion.escena.id == "E3"
    visibles = ids(sesion.opciones_disponibles())
    assert visibles == esperadas
    assert len(visibles) == 2  # regla: exactamente dos opciones en E3


def test_U1_condicion_multiple_exige_todas():
    datos = datos_transmision()
    op = escena(datos, "E3")["opciones"][0]
    op["condiciones"] = {"conoce_origen": True, "confia_en_la_voz": True}
    s = Sesion(construir_historia(datos))
    ir_a_E3(s, investigar=True)  # conoce_origen=true pero confia_en_la_voz=false
    assert op["id"] not in ids(s.opciones_disponibles())


# ---------------------------------------------------------------- U2 / CA01 / CA02
def test_U2_CA01_eleccion_valida_aplica_efectos_y_avanza(sesion):
    r1 = sesion.elegir("revisar")
    assert r1.aceptada and sesion.escena.id == "E2"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}

    r2 = sesion.elegir("investigar")
    assert r2.aceptada
    assert sesion.escena.id == "E3"
    assert sesion.variables["conoce_origen"] is True
    assert ids(sesion.opciones_disponibles()) == ["activar_codigo", "cortar"]


@pytest.mark.parametrize(
    "investigar, eleccion, destino, variables",
    [
        (True, "activar_codigo", "E4", {"conoce_origen": True, "confia_en_la_voz": True}),
        (False, "activar_sin_verificar", "E5", {"conoce_origen": False, "confia_en_la_voz": True}),
        (False, "cortar", "E6", {"conoce_origen": False, "confia_en_la_voz": False}),
    ],
)
def test_U2_efectos_y_destino_de_cada_opcion_de_E3(sesion, investigar, eleccion, destino, variables):
    ir_a_E3(sesion, investigar)
    assert sesion.elegir(eleccion).aceptada
    assert sesion.escena.id == destino
    assert sesion.variables == variables
    assert sesion.estado is EstadoSesion.FINAL


# ---------------------------------------------------------------- U3 / CA02
@pytest.mark.parametrize(
    "opcion_id",
    ["activar_codigo",   # existe pero no habilitada (CA02)
     "no_existe",            # inexistente
     "revisar",              # existe en otra escena, no en E3
     "", None, 3, "CORTAR"],  # basura / mayúsculas
)
def test_U3_opcion_inexistente_o_no_habilitada_no_altera_estado(sesion, opcion_id):
    ir_a_E3(sesion, investigar=False)
    antes = (sesion.escena.id, sesion.variables, sesion.recorrido)
    r = sesion.elegir(opcion_id)
    assert r.aceptada is False
    assert r.mensaje
    assert (sesion.escena.id, sesion.variables, sesion.recorrido) == antes


def test_CA02_sin_conocer_origen_activar_sin_verificar_lleva_a_E5(sesion):
    ir_a_E3(sesion, investigar=False)
    assert sesion.elegir("activar_codigo").aceptada is False
    assert sesion.escena.id == "E3"
    assert sesion.elegir("activar_sin_verificar").aceptada
    assert sesion.escena.id == "E5"


def test_U3_no_se_puede_elegir_en_un_final(sesion):
    ir_a_E3(sesion, investigar=False)
    sesion.elegir("cortar")
    antes = (sesion.escena.id, sesion.variables)
    assert sesion.elegir("cortar").aceptada is False
    assert (sesion.escena.id, sesion.variables) == antes


def test_U3_variables_expuestas_son_copia(sesion):
    sesion.variables["conoce_origen"] = True
    assert sesion.variables["conoce_origen"] is False


# ---------------------------------------------------------------- U5
def test_U5_reiniciar_restaura_escena_y_variables_iniciales(sesion):
    ir_a_E3(sesion, investigar=True)
    sesion.elegir("activar_codigo")
    assert sesion.escena.id == "E4" and sesion.variables["confia_en_la_voz"] is True

    sesion.reiniciar()
    assert sesion.escena.id == "E1"
    assert sesion.variables == {"conoce_origen": False, "confia_en_la_voz": False}
    assert sesion.recorrido == ["E1"]
    assert sesion.estado is EstadoSesion.EN_CURSO
    # No queda información de la partida anterior:
    ir_a_E3(sesion, investigar=False)
    assert ids(sesion.opciones_disponibles()) == ["activar_sin_verificar", "cortar"]


# ---------------------------------------------------------------- Bloqueo en partida
def test_escena_no_final_sin_opciones_habilitadas_queda_bloqueada():
    datos = datos_transmision()
    # Todas las opciones de E3 exigen algo imposible tras 'continuar'.
    for o in escena(datos, "E3")["opciones"]:
        o["condiciones"] = {"conoce_origen": True}
    s = Sesion(construir_historia(datos))  # el archivo es válido estructuralmente
    ir_a_E3(s, investigar=False)
    assert s.estado is EstadoSesion.BLOQUEADA
    antes = (s.escena.id, s.variables)
    r = s.elegir("cortar")
    assert r.aceptada is False and "Reinicie" in r.mensaje
    assert (s.escena.id, s.variables) == antes
    s.reiniciar()
    assert s.escena.id == "E1" and s.estado is EstadoSesion.EN_CURSO
