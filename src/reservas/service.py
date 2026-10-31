"""Casos de uso: reservar, cancelar y consultar disponibilidad.

Este módulo NO duplica reglas: la validación de datos y el cálculo de
superposición delega en `reservas.rules` (única fuente). Lo que agrega es
el control de estado sobre el repositorio —contra qué reservas activas se
compara el nuevo intervalo— y los rechazos propios de los casos de uso.
"""

from datetime import datetime

from reservas import rules
from reservas.models import ACTIVE, CANCELLED, Reservation
from reservas.rules import RuleValidationError
from reservas.repository import Repository


class OverlapNotAllowedError(RuleValidationError):
    """Ya existe una reserva activa de la misma unidad en ese intervalo."""


class ReservationNotFoundError(RuleValidationError):
    """No existe una reserva con el identificador indicado."""


class AlreadyCancelledError(RuleValidationError):
    """La reserva ya estaba cancelada: no se puede cancelar dos veces."""


class ReservationService:
    """Orquesta reservas sobre un `Repository` con el reloj inyectado (D3).

    `clock` es un callable que devuelve la hora local naive (D2): ningún
    método llama a `datetime.now()` por adentro.
    """

    def __init__(self, repo: Repository, known_units: set[str], clock) -> None:
        self.repo = repo
        self._known_units = known_units
        self._clock = clock

    def reserve(self, unit: str, requester: str, start: str, end: str) -> Reservation:
        """Valida, verifica disponibilidad y persiste una reserva activa."""
        start_dt, end_dt = rules.validate_reservation(
            self._clock(), self._known_units, unit, requester, start, end
        )
        self._ensure_slot_free(unit, start_dt, end_dt)
        reservation = Reservation(
            id=None, unit=unit, requester=requester, start=start, end=end,
            status=ACTIVE,
        )
        reservation.id = self.repo.add(reservation)
        return reservation

    def cancel(self, reservation_id: int) -> Reservation:
        """Cancela conservando el registro (RG-03): solo cambia el estado."""
        reservation = self.repo.get(reservation_id)
        if reservation is None:
            raise ReservationNotFoundError(
                f"No existe una reserva con el id {reservation_id}."
            )
        if reservation.status == CANCELLED:
            raise AlreadyCancelledError(
                f"La reserva {reservation_id} ya estaba cancelada."
            )
        reservation.status = CANCELLED
        self.repo.update(reservation)
        return reservation

    def is_available(self, unit: str, start: str, end: str) -> bool:
        """Disponibilidad con las mismas reglas que `reserve` (RG-02)."""
        start_dt, end_dt = self._validated_interval(unit, start, end)
        return self._slot_is_free(unit, start_dt, end_dt)

    def _validated_interval(self, unit: str, start: str,
                            end: str) -> tuple[datetime, datetime]:
        """Valida unidad + ventana temporal con las funciones de `rules`."""
        rules.validate_unit(unit, self._known_units)
        return rules.validate_time_window(self._clock(), start, end)

    def _ensure_slot_free(self, unit: str, start_dt: datetime,
                          end_dt: datetime) -> None:
        if not self._slot_is_free(unit, start_dt, end_dt):
            raise OverlapNotAllowedError(
                f"La unidad {unit} ya tiene una reserva activa que se superpone "
                f"con el intervalo pedido "
                f"({start_dt.strftime(rules.DATE_FORMAT)} - "
                f"{end_dt.strftime(rules.DATE_FORMAT)})."
            )

    def _slot_is_free(self, unit: str, start_dt: datetime,
                      end_dt: datetime) -> bool:
        """Consulta con las mismas reglas que la creación (una sola verdad)."""
        for existing in self.repo.list_by_unit(unit):
            if not existing.is_active():
                continue
            existing_start = datetime.strptime(existing.start, rules.DATE_FORMAT)
            existing_end = datetime.strptime(existing.end, rules.DATE_FORMAT)
            if rules.intervals_overlap(start_dt, end_dt,
                                       existing_start, existing_end):
                return False
        return True
