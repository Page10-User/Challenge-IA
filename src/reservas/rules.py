"""Reglas de negocio de reservas (única fuente de verdad, SPEC v1.0).

Este módulo no conoce la persistencia ni la consola: solo validación y la
convención de intervalos. La hora actual siempre llega por parámetro (D3),
para que los tests y cualquier llamador controlen el tiempo.

Las funciones públicas `validate_unit`, `validate_time_window` y
`validate_reservation` se componen entre sí: disponibilidad (service) y
creación usan EXACTAMENTE las mismas reglas (RG-02).
"""

from datetime import datetime, timedelta
from typing import Optional

import re

# Formato estricto de D2: "YYYY-MM-DD HH:MM" con ceros a la izquierda.
# strptime es tolerante a "2026-1-1 10:00"; el regex es el que garantiza
# el formato exacto y luego strptime valida plausibilidad (p. ej. 02-30).
_DATETIME_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3]):[0-5]\d$")
DATE_FORMAT = "%Y-%m-%d %H:%M"

_MIN_DURATION = 30          # minutos; D4 (RG-08)
_MAX_ANTICIPATION_DAYS = 15  # días; D4 (RG-07)


class RuleValidationError(Exception):
    """Base de todos los rechazos de negocio, con mensaje claro."""


class UnknownUnitError(RuleValidationError):
    """La unidad no está en el inventario conocido."""


class EmptyRequesterError(RuleValidationError):
    """El solicitante está vacío o compuesto solo por espacios."""


class InvalidDatetimeError(RuleValidationError):
    """La fecha/hora no cumple el formato estricto 'YYYY-MM-DD HH:MM' o es imposible."""


class InvalidIntervalError(RuleValidationError):
    """El inicio no es estrictamente anterior al fin."""


class PastStartError(RuleValidationError):
    """El inicio es anterior al momento actual (D3)."""


class TooShortDurationError(RuleValidationError):
    """La duración es inferior al mínimo de 30 minutos (D4)."""


class TooFarAheadError(RuleValidationError):
    """El inicio excede la anticipación máxima de 15 días (D4)."""


def intervals_overlap(
    a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime
) -> bool:
    """Única función de superposición (D0: intervalos semiabiertos [inicio, fin)).

    Dos intervalos se superponen si y solo si aI < bF y bI < aF.
    Por eso 10:00-11:00 y 11:00-12:00 NO se superponen (límites consecutivos).
    """
    return a_start < b_end and b_start < a_end


def parse_local_datetime(raw: str, field_name: str) -> datetime:
    """Convierte 'YYYY-MM-DD HH:MM' en datetime naive local, o rechaza."""
    if not isinstance(raw, str) or not _DATETIME_RE.match(raw.strip()):
        raise InvalidDatetimeError(
            f"La fecha/hora de {field_name} no cumple el formato estricto "
            f"'YYYY-MM-DD HH:MM' (recibido: {raw!r})."
        )
    try:
        return datetime.strptime(raw.strip(), DATE_FORMAT)
    except ValueError as exc:
        raise InvalidDatetimeError(
            f"La fecha/hora de {field_name} es imposible o mal formada "
            f"(recibido: {raw!r}): {exc}"
        ) from exc


def validate_unit(unit: str, known_units: set[str]) -> None:
    """Valida que la unidad exista en el inventario (RG-01)."""
    if not isinstance(unit, str) or unit not in known_units:
        raise UnknownUnitError(
            f"La unidad {unit!r} no existe en el inventario conocido."
        )


def validate_time_window(
    now: datetime, start: str, end: str
) -> tuple[datetime, datetime]:
    """Valida fechas, intervalo, pasado, duración y anticipación (RG-02 a RG-08).

    Es el bloque temporal exacto que usa `validate_reservation`; la
    disponibilidad lo reutiliza para no duplicar ninguna regla.
    """
    start_dt = parse_local_datetime(start, "inicio")
    end_dt = parse_local_datetime(end, "fin")

    if start_dt >= end_dt:
        raise InvalidIntervalError(
            f"El inicio ({start}) debe ser estrictamente anterior al fin ({end})."
        )

    if start_dt < now:
        raise PastStartError(
            f"El inicio ({start}) es anterior al momento actual "
            f"({now.strftime(DATE_FORMAT)})."
        )

    duration = end_dt - start_dt
    if duration.total_seconds() < _MIN_DURATION * 60:
        raise TooShortDurationError(
            f"La duración ({duration}) es menor al mínimo de {_MIN_DURATION} minutos."
        )

    anticipation_limit = now + timedelta(days=_MAX_ANTICIPATION_DAYS)
    if start_dt > anticipation_limit:
        raise TooFarAheadError(
            f"El inicio ({start}) supera la anticipación máxima de "
            f"{_MAX_ANTICIPATION_DAYS} días."
        )

    return start_dt, end_dt


def validate_reservation(
    now: datetime,
    known_units: set[str],
    unit: str,
    requester: str,
    start: str,
    end: str,
) -> tuple[datetime, datetime]:
    """Valida una reserva completa y devuelve el intervalo parseado.

    `known_units` proviene de data/inventory.json; `now` es el reloj
    inyectado en hora local naive (D2/D3). El orden de validación es
    estable: unidad, solicitante, fechas, intervalo, pasado, duración y
    anticipación.
    """
    validate_unit(unit, known_units)

    if not isinstance(requester, str) or not requester.strip():
        raise EmptyRequesterError(
            "El solicitante no puede ser vacío ni compuesto solo por espacios."
        )

    return validate_time_window(now, start, end)
