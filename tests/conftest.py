import copy
import json
from pathlib import Path

import pytest

from motor_narrativo import Sesion, construir_historia

RAIZ = Path(__file__).resolve().parent.parent
HISTORIAS = RAIZ / "historias"
TRANSMISION = HISTORIAS / "la_ultima_transmision.json"
FARO = HISTORIAS / "el_faro.json"


def datos_transmision() -> dict:
    """Copia fresca de los datos crudos de la historia de referencia."""
    with TRANSMISION.open(encoding="utf-8") as f:
        return json.load(f)


def escena(datos: dict, escena_id: str) -> dict:
    return next(e for e in datos["escenas"] if e["id"] == escena_id)


def opcion(datos: dict, escena_id: str, opcion_id: str) -> dict:
    return next(o for o in escena(datos, escena_id)["opciones"] if o["id"] == opcion_id)


@pytest.fixture
def datos():
    return datos_transmision()


@pytest.fixture
def sesion():
    return Sesion(construir_historia(datos_transmision()))


def ids(opciones) -> list[str]:
    return [o.id for o in opciones]


__all__ = ["copy", "datos_transmision", "escena", "opcion", "ids", "TRANSMISION", "FARO", "HISTORIAS", "RAIZ"]
