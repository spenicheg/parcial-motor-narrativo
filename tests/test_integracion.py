"""I1: lectura de archivos reales + motor + interfaz, hasta alcanzar un final."""
import subprocess
import sys

import pytest

from conftest import FARO, RAIZ, TRANSMISION, ids
from motor_narrativo import EstadoSesion, Sesion, cargar_historia
from motor_narrativo.cli import jugar

RUTAS_FINALES = [
    (["revisar", "investigar", "activar_codigo"], "E4"),
    (["revisar", "continuar", "activar_sin_verificar"], "E5"),
    (["revisar", "investigar", "cortar"], "E6"),
    (["revisar", "continuar", "cortar"], "E6"),
]


@pytest.mark.parametrize("ruta, final", RUTAS_FINALES, ids=["->".join(r) for r, _ in RUTAS_FINALES])
def test_I1_archivo_real_hasta_cada_final(ruta, final):
    sesion = Sesion(cargar_historia(TRANSMISION))
    for opcion_id in ruta:
        assert opcion_id in ids(sesion.opciones_disponibles())
        assert sesion.elegir(opcion_id).aceptada
    assert sesion.escena.id == final
    assert sesion.estado is EstadoSesion.FINAL
    assert sesion.opciones_disponibles() == []


@pytest.mark.parametrize(
    "ruta, final, opciones_F2",
    [(["recoger", "abrir"], "F3", ["abrir", "gritar"]),
     (["subir", "gritar"], "F4", ["gritar"])],
)
def test_I1_segunda_historia_con_el_mismo_motor(ruta, final, opciones_F2):
    sesion = Sesion(cargar_historia(FARO))
    sesion.elegir(ruta[0])
    assert ids(sesion.opciones_disponibles()) == opciones_F2  # la condición cambia las opciones
    sesion.elegir(ruta[1])
    assert sesion.escena.id == final and sesion.estado is EstadoSesion.FINAL


def test_I1_interfaz_consola_recorre_un_final_y_reinicia():
    entradas = iter(["1", "9", "x", "1", "2", "r", "s"])
    salida: list[str] = []
    jugar(cargar_historia(TRANSMISION), entrada=lambda _: next(entradas), salida=salida.append)
    texto = "\n".join(salida)
    assert "Entrada no válida" in texto
    assert "FINAL ALCANZADO (E6)" in texto
    assert "Nueva partida" in texto


@pytest.mark.parametrize("archivo, codigo_salida", [(TRANSMISION, 0), (FARO, 0)])
def test_I1_comando_validar_desde_terminal(archivo, codigo_salida):
    r = subprocess.run([sys.executable, "-m", "motor_narrativo", "validar", str(archivo)],
                       cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == codigo_salida
    assert "Historia válida" in r.stdout
