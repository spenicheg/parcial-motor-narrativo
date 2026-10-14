"""U6 (solicitud de cambio, hora 6): deshacer restaura escena y variables y consume el retroceso."""
import pytest

from conftest import ids
from motor_narrativo import EstadoSesion

INICIALES = {"conoce_origen": False, "confia_en_la_voz": False}


def estado(s):
    return (s.escena.id, s.variables, s.recorrido, s.puede_deshacer)


def test_U6_ejemplo_del_anexo(sesion):
    sesion.elegir("revisar")
    assert sesion.elegir("investigar").aceptada
    assert sesion.escena.id == "E3" and sesion.variables["conoce_origen"] is True

    r = sesion.deshacer()
    assert r.aceptada
    assert sesion.escena.id == "E2"
    assert sesion.variables == INICIALES          # conoce_origen vuelve a falso
    assert sesion.recorrido == ["E1", "E2"]
    assert sesion.puede_deshacer is False          # se consumió

    antes = estado(sesion)
    r2 = sesion.deshacer()                         # segundo intento: no cambia nada
    assert r2.aceptada is False and r2.mensaje
    assert estado(sesion) == antes

    assert sesion.elegir("continuar").aceptada
    assert ids(sesion.opciones_disponibles()) == ["activar_sin_verificar", "cortar"]


def test_U6_al_comenzar_no_hay_retroceso(sesion):
    antes = estado(sesion)
    assert sesion.puede_deshacer is False
    assert sesion.deshacer().aceptada is False
    assert estado(sesion) == antes


@pytest.mark.parametrize("invalida", ["activar_codigo", "no_existe", "", None, 42])
def test_U6_entrada_invalida_preserva_el_historial(sesion, invalida):
    sesion.elegir("revisar")
    sesion.elegir("continuar")                     # E3, conoce_origen=false
    assert sesion.elegir(invalida).aceptada is False
    assert sesion.puede_deshacer
    assert sesion.deshacer().aceptada
    # Se vuelve al estado previo a la última elección VÁLIDA ('continuar'), no a otro.
    assert sesion.escena.id == "E2" and sesion.variables == INICIALES


@pytest.mark.parametrize("invalida", ["activar_codigo", "no_existe"])
def test_U6_entrada_invalida_despues_de_deshacer_no_rehabilita_retroceso(sesion, invalida):
    sesion.elegir("revisar")
    sesion.deshacer()
    sesion.elegir(invalida)
    assert sesion.puede_deshacer is False


def test_U6_nueva_eleccion_valida_vuelve_a_habilitar_el_retroceso(sesion):
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    sesion.deshacer()
    assert sesion.puede_deshacer is False
    assert sesion.elegir("continuar").aceptada
    assert sesion.puede_deshacer is True
    assert sesion.deshacer().aceptada
    assert sesion.escena.id == "E2"


def test_U6_un_solo_nivel(sesion):
    sesion.elegir("revisar")
    sesion.elegir("investigar")
    sesion.elegir("activar_codigo")                # E4
    sesion.deshacer()                              # -> E3
    assert sesion.escena.id == "E3"
    assert sesion.variables == {"conoce_origen": True, "confia_en_la_voz": False}
    assert sesion.deshacer().aceptada is False     # no retrocede a E2
    assert sesion.escena.id == "E3"


@pytest.mark.parametrize(
    "investigar, eleccion, final, previas",
    [
        (True, "activar_codigo", "E4", {"conoce_origen": True, "confia_en_la_voz": False}),
        (False, "activar_sin_verificar", "E5", {"conoce_origen": False, "confia_en_la_voz": False}),
        (True, "cortar", "E6", {"conoce_origen": True, "confia_en_la_voz": False}),
    ],
)
def test_U6_deshacer_desde_un_final_vuelve_a_E3(sesion, investigar, eleccion, final, previas):
    sesion.elegir("revisar")
    sesion.elegir("investigar" if investigar else "continuar")
    sesion.elegir(eleccion)
    assert sesion.escena.id == final and sesion.estado is EstadoSesion.FINAL
    assert sesion.deshacer().aceptada
    assert sesion.escena.id == "E3"
    assert sesion.variables == previas
    assert sesion.estado is EstadoSesion.EN_CURSO
