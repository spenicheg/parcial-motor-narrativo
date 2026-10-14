"""Interfaz de consola. Solo traduce texto del lector a comandos de Sesion.

Uso:
    python -m motor_narrativo jugar historias/la_ultima_transmision.json
    python -m motor_narrativo validar historias/la_ultima_transmision.json
"""
from __future__ import annotations

import argparse
import sys
from typing import Callable

from .cargador import cargar_historia
from .errores import ErrorContenido
from .modelo import Historia
from .sesion import EstadoSesion, Sesion

AYUDA = "Escriba el número de una opción, 'd' para deshacer, 'r' para reiniciar o 's' para salir."


def jugar(historia: Historia, entrada: Callable[[str], str] = input,
          salida: Callable[[str], None] = print) -> None:
    sesion = Sesion(historia)
    salida(f"\n=== {historia.titulo} ===")
    while True:
        escena = sesion.escena
        salida(f"\n{escena.texto}\n")
        estado = sesion.estado
        opciones = sesion.opciones_disponibles()
        if estado is EstadoSesion.FINAL:
            salida(f"*** FINAL ALCANZADO ({escena.id}) ***")
            salida(_menu(sesion, "[r] Nueva partida"))
        elif estado is EstadoSesion.BLOQUEADA:
            salida("! No hay opciones disponibles en esta escena. "
                   "Es probable que la historia tenga un error; avise a quien la escribió.")
            salida(_menu(sesion, "[r] Reiniciar"))
        else:
            for i, o in enumerate(opciones, start=1):
                salida(f"  {i}. {o.texto}")
            salida(_menu(sesion, "[r] Reiniciar"))

        try:
            cmd = entrada("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            salida("\nHasta pronto.")
            return

        if cmd == "s":
            salida("Hasta pronto.")
            return
        if cmd == "d":
            resultado = sesion.deshacer()
            salida(("\n<<< " if resultado.aceptada else "") + resultado.mensaje)
            continue
        if cmd == "r":
            sesion.reiniciar()
            salida("\n--- Nueva partida ---")
            continue
        if estado is EstadoSesion.EN_CURSO and cmd.isdigit() and 1 <= int(cmd) <= len(opciones):
            resultado = sesion.elegir(opciones[int(cmd) - 1].id)
            if not resultado.aceptada:
                salida(resultado.mensaje)
            continue
        salida(f"Entrada no válida. {AYUDA}")


def _menu(sesion: Sesion, reiniciar: str) -> str:
    partes = (["[d] Deshacer"] if sesion.puede_deshacer else []) + [reiniciar, "[s] Salir"]
    return "   ".join(partes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="motor_narrativo",
                                     description="Motor de ficción interactiva basado en archivos JSON.")
    sub = parser.add_subparsers(dest="comando", required=True)
    for nombre, ayuda in (("jugar", "jugar una historia"), ("validar", "revisar una historia sin jugarla")):
        sp = sub.add_parser(nombre, help=ayuda)
        sp.add_argument("archivo", help="ruta del archivo .json de la historia")
    args = parser.parse_args(argv)

    try:
        historia = cargar_historia(args.archivo)
    except ErrorContenido as e:
        print(e.resumen(), file=sys.stderr)
        return 2

    if args.comando == "validar":
        print(f"Historia válida: «{historia.titulo}» — {len(historia.escenas)} escenas, "
              f"{len(historia.finales)} finales, {len(historia.variables_iniciales)} variables.")
        return 0
    jugar(historia)
    return 0
