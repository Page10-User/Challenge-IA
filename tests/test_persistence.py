"""Tests de persistencia (consigna §3.3, prueba 7).

Requisito: reservas activas Y canceladas sobreviven a detener y reiniciar,
sin borrar datos. El "reinicio" se simula con una instancia nueva del
repositorio apuntando al mismo archivo de SQLite. La BD vive en tmp_path,
jamás en data/reservas.db real.
"""

from datetime import datetime

from reservas.repository import SqliteRepository
from reservas.service import ReservationService

# Reloj fijo inyectado (D3): martes 2026-11-10 08:00.
NOW = datetime(2026, 11, 10, 8, 0)
UNITS = {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"}


def _service(db_path) -> tuple[ReservationService, SqliteRepository]:
    """Construye repositorio SQLite y service con el reloj inyectado."""
    repo = SqliteRepository(db_path)
    service = ReservationService(repo=repo, known_units=UNITS, clock=lambda: NOW)
    return service, repo


class TestPersistenciaTrasReinicio:
    def test_activas_y_canceladas_sobreviven_reinicio(self, tmp_path):
        db_path = tmp_path / "persistencia_test.db"

        # "1ra sesión": reservar dos, cancelar una, cerrar.
        session1, _ = _service(db_path)
        activa = session1.reserve(unit="MIC-01", requester="Ana Prueba",
                                  start="2026-11-10 10:00", end="2026-11-10 11:00")
        a_cancelar = session1.reserve(unit="MIC-02", requester="Beto Prueba",
                                      start="2026-11-10 10:00", end="2026-11-10 11:00")
        session1.cancel(a_cancelar.id)

        # "2da sesión" (reinicio): instancias nuevas sobre el mismo archivo.
        session2, repo2 = _service(db_path)
        activa_recargada = repo2.get(activa.id)
        cancelada_recargada = repo2.get(a_cancelar.id)

        assert activa_recargada is not None
        assert activa_recargada.status == "activa"
        assert activa_recargada.requester == "Ana Prueba"

        assert cancelada_recargada is not None, "cancelar no puede borrar al reiniciar"
        assert cancelada_recargada.status == "cancelada"

        # El horario de la cancelada sigue libre; el de la activa, ocupado.
        assert session2.is_available(unit="MIC-02", start="2026-11-10 10:00",
                                     end="2026-11-10 11:00") is True
        assert session2.is_available(unit="MIC-01", start="2026-11-10 10:00",
                                     end="2026-11-10 11:00") is False

    def test_reinicio_preserva_ids_y_no_duplica(self, tmp_path):
        db_path = tmp_path / "ids_test.db"
        session1, _ = _service(db_path)
        reservation = session1.reserve(unit="FUE-01", requester="Caro Prueba",
                                       start="2026-11-10 14:00", end="2026-11-10 15:00")

        _, repo2 = _service(db_path)
        records = repo2.list_by_unit("FUE-01")
        assert [r.id for r in records] == [reservation.id]
        assert len(records) == 1
