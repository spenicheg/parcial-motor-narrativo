"""Motor de ficción interactiva: carga historias desde archivos y las ejecuta."""
from .cargador import cargar_historia, construir_historia, validar
from .errores import ErrorContenido, Problema
from .modelo import Escena, Historia, Opcion
from .sesion import EstadoSesion, ResultadoEleccion, Sesion

__all__ = [
    "cargar_historia", "construir_historia", "validar",
    "ErrorContenido", "Problema", "Escena", "Historia", "Opcion",
    "EstadoSesion", "ResultadoEleccion", "Sesion",
]
__version__ = "1.0.0"
