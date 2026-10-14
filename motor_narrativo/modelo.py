"""Modelo de dominio: Historia, Escena y Opcion.

Son objetos inmutables construidos solo a partir de datos ya validados.
No conocen el formato del archivo (JSON) ni la interfaz.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Opcion:
    id: str
    texto: str
    destino: str
    condiciones: Mapping[str, bool]
    efectos: Mapping[str, bool]

    def habilitada(self, variables: Mapping[str, bool]) -> bool:
        """Una opción está habilitada si TODAS sus condiciones se cumplen.

        Un mapa de condiciones vacío siempre habilita la opción.
        """
        return all(variables.get(nombre) == valor for nombre, valor in self.condiciones.items())


@dataclass(frozen=True)
class Escena:
    id: str
    texto: str
    final: bool
    opciones: tuple[Opcion, ...]

    def opcion(self, opcion_id: str) -> Opcion | None:
        return next((o for o in self.opciones if o.id == opcion_id), None)


@dataclass(frozen=True)
class Historia:
    titulo: str
    inicio: str
    variables_iniciales: Mapping[str, bool]
    escenas: Mapping[str, Escena]

    def escena(self, escena_id: str) -> Escena:
        return self.escenas[escena_id]

    @property
    def finales(self) -> list[Escena]:
        return [e for e in self.escenas.values() if e.final]
