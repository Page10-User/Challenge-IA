"""Interfaz de consola: subcomandos en español (D1) sobre `service`.

Capa fina: acá no hay reglas de negocio; solo parseo de argumentos,
mensajes al usuario y el ensamblado del service con la DB real y el reloj
del sistema (única capa que puede llamar a `datetime.now()`, D3).

Sin argumentos muestra la bienvenida con la lista de comandos disponibles
(menú estático), para no exigir memorización.
"""

import argparse
import json
import sys
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from reservas import rules
from reservas.repository import SqliteRepository
from reservas.service import ReservationService

_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DB = _ROOT / "data" / "reservas.db"
_INVENTORY = _ROOT / "data" / "inventory.json"

_MENU = [
    ("disponibilidad", "consulta si un intervalo está libre para una unidad"),
    ("reservar", "registra una nueva reserva"),
    ("cancelar", "cancela una reserva por id (no borra: libera el horario)"),
    ("listar", "muestra todas las reservas, incluidas las canceladas"),
]


def _print_welcome() -> None:
    """Menú estático: sin subcomando se muestra la lista de disponibles."""
    print("Bienvenido al sistema de reservas de equipos de laboratorio.")
    print("Uso: python -m reservas <comando> ... o '-h' para la ayuda de cada comando.")
    print("\nComandos disponibles:")
    for name, description in _MENU:
        print(f"  {name}  ->  {description}")


def _load_known_units() -> set[str]:
    """Unidades conocidas desde inventario (data/inventory.json)."""
    with _INVENTORY.open(encoding="utf-8") as source:
        data = json.load(source)
    return {unit["id"] for unit in data["unidades"]}


def _build_service(db_path: str | Path, clock) -> ReservationService:
    """Ensambla service con la DB real y el inventario cargado."""
    return ReservationService(
        repo=SqliteRepository(db_path),
        known_units=_load_known_units(),
        clock=clock,
    )


def main(argv: list[str] | None = None,
         db_path: str | Path = _DEFAULT_DB,
         clock: Callable[[], datetime] = datetime.now) -> int:
    """Entry point de la CLI. Devuelve código de salida: 0 ok, 1 rechazo."""
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        _print_welcome()
        return 0

    parser = argparse.ArgumentParser(
        prog="reservas",
        description="Sistema de reservas de equipos de laboratorio.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_disponibilidad = subparsers.add_parser(
        "disponibilidad", help="consulta si un intervalo está libre")
    parser_disponibilidad.add_argument("--unidad", required=True)
    parser_disponibilidad.add_argument("--inicio", required=True)
    parser_disponibilidad.add_argument("--fin", required=True)

    parser_reservar = subparsers.add_parser(
        "reservar", help="registra una nueva reserva")
    parser_reservar.add_argument("--unidad", required=True)
    parser_reservar.add_argument("--solicitante", required=True)
    parser_reservar.add_argument("--inicio", required=True)
    parser_reservar.add_argument("--fin", required=True)

    parser_cancelar = subparsers.add_parser(
        "cancelar", help="cancela una reserva por id")
    parser_cancelar.add_argument("--id", type=int, required=True)

    subparsers.add_parser("listar", help="lista todas las reservas")

    arguments = parser.parse_args(argv)
    service = _build_service(db_path, clock)

    try:
        if arguments.command == "disponibilidad":
            free = service.is_available(arguments.unidad,
                                        arguments.inicio, arguments.fin)
            estado = "DISPONIBLE" if free else "OCUPADA"
            print(f"{estado}: {arguments.unidad} {arguments.inicio} - {arguments.fin}")
            return 0

        if arguments.command == "reservar":
            reservation = service.reserve(arguments.unidad, arguments.solicitante,
                                          arguments.inicio, arguments.fin)
            print(f"Reserva registrada con el id {reservation.id} "
                  f"({reservation.unit} {reservation.start} - {reservation.end}).")
            return 0

        if arguments.command == "cancelar":
            cancelled = service.cancel(arguments.id)
            print(f"Reserva {cancelled.id} cancelada (conserva el historial).")
            return 0

        if arguments.command == "listar":
            reservations = service.repo.all()
            if not reservations:
                print("Sin reservas registradas.")
                return 0
            for reservation in reservations:
                print(f"{reservation.id}: {reservation.unit} "
                      f"{reservation.start} - {reservation.end} | "
                      f"{reservation.requester} [{reservation.status}]")
            return 0

    except rules.RuleValidationError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    parser.error(f"Comando no reconocido: {arguments.command}")  # inaccesible
    return 1
