"""Tests de casos de uso (service): consigna §3.3, pruebas 1, 2, 3, 4 y 6.

El service delega TODA validación en `reservas.rules` (única fuente, D0–D4).
El reloj se inyecta (D3) y el repositorio es de memoria, para aislar la
lógica de la persistencia real (que vive en test_persistence.py).
"""

from datetime import datetime

import pytest

from reservas.models import Reservation
from reservas.repository import InMemoryRepository
from reservas.rules import EmptyRequesterError, UnknownUnitError
from reservas.service import (
    AlreadyCancelledError,
    OverlapNotAllowedError,
    ReservationNotFoundError,
    ReservationService,
)

# "Ahora" fijo: martes 2026-11-10 08:00 (reloj inyectado, D3).
NOW = datetime(2026, 11, 10, 8, 0)

UNITS = {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"}


def make_service() -> tuple[ReservationService, InMemoryRepository]:
    repo = InMemoryRepository()
    service = ReservationService(repo=repo, known_units=UNITS, clock=lambda: NOW)
    return service, repo


class TestReservaValida:
    def test_reserva_valida_se_guarda_activa_con_id(self):
        service, repo = make_service()
        reservation = service.reserve(unit="MIC-01", requester="Ana Prueba",
                                      start="2026-11-10 10:00", end="2026-11-10 11:00")
        assert reservation.id is not None
        assert reservation.status == "activa"
        stored = repo.get(reservation.id)
        assert stored is not None
        assert stored.requester == "Ana Prueba"


class TestSuperposicion:
    def test_solapamiento_del_mismo_equipo_rechaza(self):
        # Consigna prueba 2: MIC-01 10:00-11:00 ocupado -> rechazar 10:30-11:30.
        service, _ = make_service()
        service.reserve(unit="MIC-01", requester="Ana Prueba",
                        start="2026-11-10 10:00", end="2026-11-10 11:00")
        with pytest.raises(OverlapNotAllowedError) as exc:
            service.reserve(unit="MIC-01", requester="Beto Prueba",
                            start="2026-11-10 10:30", end="2026-11-10 11:30")
        assert "MIC-01" in str(exc.value)

    def test_limites_consecutivos_permitidos(self):
        # Consigna prueba 3: 10:00-11:00 ocupado -> 11:00-12:00 SÍ se permite (D0).
        service, _ = make_service()
        service.reserve(unit="MIC-01", requester="Ana Prueba",
                        start="2026-11-10 10:00", end="2026-11-10 11:00")
        reservation = service.reserve(unit="MIC-01", requester="Beto Prueba",
                                      start="2026-11-10 11:00", end="2026-11-10 12:00")
        assert reservation.status == "activa"

    def test_unidades_distintas_simultaneas_permitidas(self):
        # Consigna prueba 4: MIC-01 ocupado -> MIC-02 puede reservar el mismo horario.
        service, _ = make_service()
        service.reserve(unit="MIC-01", requester="Ana Prueba",
                        start="2026-11-10 10:00", end="2026-11-10 11:00")
        reservation = service.reserve(unit="MIC-02", requester="Beto Prueba",
                                      start="2026-11-10 10:00", end="2026-11-10 11:00")
        assert reservation.status == "activa"


class TestCancelacion:
    def test_cancelar_conserva_registro_y_libera_horario(self):
        # Consigna prueba 6: cancelar no borra; el horario vuelve a estar libre.
        service, repo = make_service()
        reservation = service.reserve(unit="MIC-01", requester="Ana Prueba",
                                      start="2026-11-10 10:00", end="2026-11-10 11:00")
        cancelled = service.cancel(reservation.id)
        assert cancelled.id == reservation.id
        assert cancelled.status == "cancelada"

        stored = repo.get(reservation.id)
        assert stored is not None, "cancelar no debe borrar el registro"
        assert stored.status == "cancelada"

        same_slot = service.reserve(unit="MIC-01", requester="Beto Prueba",
                                    start="2026-11-10 10:00", end="2026-11-10 11:00")
        assert same_slot.status == "activa"

    def test_cancelar_id_desconocido_rechaza(self):
        service, _ = make_service()
        with pytest.raises(ReservationNotFoundError):
            service.cancel(999)

    def test_doble_cancelacion_rechaza(self):
        service, _ = make_service()
        reservation = service.reserve(unit="MIC-01", requester="Ana Prueba",
                                      start="2026-11-10 10:00", end="2026-11-10 11:00")
        service.cancel(reservation.id)
        with pytest.raises(AlreadyCancelledError):
            service.cancel(reservation.id)


class TestDisponibilidad:
    def test_consulta_y_creacion_usan_mismas_reglas(self):
        # Disponible antes, ocupada en el intervalo exacto, libre en el borde (D0).
        service, _ = make_service()
        assert service.is_available(unit="MIC-01", start="2026-11-10 10:00",
                                    end="2026-11-10 11:00") is True
        service.reserve(unit="MIC-01", requester="Ana Prueba",
                        start="2026-11-10 10:00", end="2026-11-10 11:00")
        assert service.is_available(unit="MIC-01", start="2026-11-10 10:00",
                                    end="2026-11-10 11:00") is False
        assert service.is_available(unit="MIC-01", start="2026-11-10 11:00",
                                    end="2026-11-10 12:00") is True

    def test_disponibilidad_con_inputs_invalidos_rechaza_con_mismas_reglas(self):
        service, _ = make_service()
        with pytest.raises(UnknownUnitError):
            service.is_available(unit="XXX-99", start="2026-11-10 10:00",
                                 end="2026-11-10 11:00")
        with pytest.raises(EmptyRequesterError):
            service.reserve(unit="MIC-01", requester="   ",
                            start="2026-11-10 10:00", end="2026-11-10 11:00")
