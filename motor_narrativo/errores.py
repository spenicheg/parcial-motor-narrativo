"""Errores de contenido con código, ubicación y mensaje legible para escritores."""
from __future__ import annotations

from dataclasses import dataclass

# Códigos de error de contenido (ver README, sección "Errores de contenido").
ARCHIVO_ILEGIBLE = "ARCHIVO_ILEGIBLE"
ESTRUCTURA_INVALIDA = "ESTRUCTURA_INVALIDA"
CAMPO_AUSENTE = "CAMPO_AUSENTE"
TIPO_INVALIDO = "TIPO_INVALIDO"
INICIO_INEXISTENTE = "INICIO_INEXISTENTE"
ESCENA_DUPLICADA = "ESCENA_DUPLICADA"
OPCION_DUPLICADA = "OPCION_DUPLICADA"
DESTINO_INEXISTENTE = "DESTINO_INEXISTENTE"
VARIABLE_NO_DECLARADA = "VARIABLE_NO_DECLARADA"
VALOR_NO_BOOLEANO = "VALOR_NO_BOOLEANO"
FINAL_CON_OPCIONES = "FINAL_CON_OPCIONES"
ESCENA_SIN_OPCIONES = "ESCENA_SIN_OPCIONES"


@dataclass(frozen=True)
class Problema:
    codigo: str
    ubicacion: str
    mensaje: str

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.ubicacion}: {self.mensaje}"


class ErrorContenido(Exception):
    """La historia no es válida. Contiene TODOS los problemas encontrados."""

    def __init__(self, problemas: list[Problema]):
        self.problemas = list(problemas)
        super().__init__(self.resumen())

    @property
    def codigos(self) -> set[str]:
        return {p.codigo for p in self.problemas}

    def resumen(self) -> str:
        n = len(self.problemas)
        lineas = [f"La historia tiene {n} problema(s) y no se puede jugar:"]
        lineas += [f"  {i}. {p}" for i, p in enumerate(self.problemas, start=1)]
        return "\n".join(lineas)
