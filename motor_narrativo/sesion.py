"""Reglas de juego: estado de una partida y aplicación de elecciones.

Es genérico: evalúa condiciones y efectos leídos de los datos. No hay ninguna
referencia a escenas, opciones o variables de una historia concreta.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping

from .modelo import Escena, Historia, Opcion


class EstadoSesion(Enum):
    EN_CURSO = "en_curso"
    FINAL = "final"          # escena final alcanzada
    BLOQUEADA = "bloqueada"  # escena no final sin opciones habilitadas


@dataclass(frozen=True)
class ResultadoEleccion:
    aceptada: bool
    mensaje: str


@dataclass(frozen=True)
class Instantanea:
    """Estado completo de la partida en un momento dado (inmutable)."""
    escena_id: str
    variables: Mapping[str, bool]
    recorrido: tuple[str, ...]


class Sesion:
    """Una partida. El estado solo cambia mediante elegir(), deshacer() o reiniciar().

    Retroceso de un solo nivel (solicitud de cambio, hora 6): antes de aplicar una
    elección válida se guarda una instantánea del estado; deshacer() la restaura y
    la consume. Las entradas inválidas no tocan la instantánea.
    """

    def __init__(self, historia: Historia):
        self._historia = historia
        self.reiniciar()

    # --- consulta -------------------------------------------------------
    @property
    def historia(self) -> Historia:
        return self._historia

    @property
    def escena(self) -> Escena:
        return self._historia.escena(self._escena_id)

    @property
    def variables(self) -> dict[str, bool]:
        """Copia del estado; modificarla no altera la partida."""
        return dict(self._variables)

    @property
    def recorrido(self) -> list[str]:
        """IDs de escenas visitadas en esta partida, en orden."""
        return list(self._recorrido)

    @property
    def puede_deshacer(self) -> bool:
        return self._anterior is not None

    def opciones_disponibles(self) -> list[Opcion]:
        return [o for o in self.escena.opciones if o.habilitada(self._variables)]

    @property
    def estado(self) -> EstadoSesion:
        if self.escena.final:
            return EstadoSesion.FINAL
        if not self.opciones_disponibles():
            return EstadoSesion.BLOQUEADA
        return EstadoSesion.EN_CURSO

    # --- comandos -------------------------------------------------------
    def elegir(self, opcion_id: object) -> ResultadoEleccion:
        estado = self.estado
        if estado is EstadoSesion.FINAL:
            return ResultadoEleccion(False, "La partida terminó. Reinicie o deshaga la última decisión.")
        if estado is EstadoSesion.BLOQUEADA:
            return ResultadoEleccion(False, "No hay opciones disponibles en esta escena. Reinicie o deshaga la última decisión.")

        opcion = next((o for o in self.opciones_disponibles() if o.id == opcion_id), None)
        if opcion is None:
            existe = isinstance(opcion_id, str) and self.escena.opcion(opcion_id) is not None
            motivo = "no está disponible con la información actual" if existe else "no existe en esta escena"
            return ResultadoEleccion(False, f"La opción {opcion_id!r} {motivo}.")

        # Las condiciones ya se evaluaron con el estado previo; ahora se aplican efectos.
        nuevas = dict(self._variables)
        nuevas.update(opcion.efectos)
        anterior = self._instantanea()
        self._variables = nuevas
        self._escena_id = opcion.destino
        self._recorrido = self._recorrido + (opcion.destino,)
        self._anterior = anterior  # solo una elección válida reemplaza el historial
        return ResultadoEleccion(True, f"Elegido: {opcion.texto}")

    def deshacer(self) -> ResultadoEleccion:
        """Revierte la última elección válida (escena, variables y recorrido). Un solo nivel."""
        if self._anterior is None:
            return ResultadoEleccion(False, "No hay una decisión para deshacer.")
        self._restaurar(self._anterior)
        self._anterior = None
        return ResultadoEleccion(True, "Se deshizo la última decisión.")

    def reiniciar(self) -> None:
        """Nueva partida: escena y variables iniciales, sin historial de la anterior."""
        self._escena_id = self._historia.inicio
        self._variables = dict(self._historia.variables_iniciales)
        self._recorrido: tuple[str, ...] = (self._historia.inicio,)
        self._anterior: Instantanea | None = None

    # --- internos -------------------------------------------------------
    def _instantanea(self) -> Instantanea:
        return Instantanea(self._escena_id, MappingProxyType(dict(self._variables)), self._recorrido)

    def _restaurar(self, i: Instantanea) -> None:
        self._escena_id = i.escena_id
        self._variables = dict(i.variables)
        self._recorrido = i.recorrido
