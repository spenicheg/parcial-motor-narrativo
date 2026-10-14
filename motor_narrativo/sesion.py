"""Reglas de juego: estado de una partida y aplicación de elecciones.

Es genérico: evalúa condiciones y efectos leídos de los datos. No hay ninguna
referencia a escenas, opciones o variables de una historia concreta.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .modelo import Escena, Historia, Opcion


class EstadoSesion(Enum):
    EN_CURSO = "en_curso"
    FINAL = "final"          # escena final alcanzada
    BLOQUEADA = "bloqueada"  # escena no final sin opciones habilitadas


@dataclass(frozen=True)
class ResultadoEleccion:
    aceptada: bool
    mensaje: str


class Sesion:
    """Una partida. El estado solo cambia mediante elegir() o reiniciar()."""

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
            return ResultadoEleccion(False, "La partida terminó. Reinicie para jugar otra vez.")
        if estado is EstadoSesion.BLOQUEADA:
            return ResultadoEleccion(False, "No hay opciones disponibles en esta escena. Reinicie la partida.")

        opcion = next((o for o in self.opciones_disponibles() if o.id == opcion_id), None)
        if opcion is None:
            existe = isinstance(opcion_id, str) and self.escena.opcion(opcion_id) is not None
            motivo = "no está disponible con la información actual" if existe else "no existe en esta escena"
            return ResultadoEleccion(False, f"La opción {opcion_id!r} {motivo}.")

        # Las condiciones ya se evaluaron con el estado previo; ahora se aplican efectos.
        nuevas = dict(self._variables)
        nuevas.update(opcion.efectos)
        self._variables = nuevas
        self._escena_id = opcion.destino
        self._recorrido.append(opcion.destino)
        return ResultadoEleccion(True, f"Elegido: {opcion.texto}")

    def reiniciar(self) -> None:
        """Nueva partida: escena inicial y variables iniciales, sin rastro de la anterior."""
        self._escena_id = self._historia.inicio
        self._variables = dict(self._historia.variables_iniciales)
        self._recorrido = [self._historia.inicio]
