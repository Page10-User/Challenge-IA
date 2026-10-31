"""Persistencia de reservas: interfaz común + implementaciones.

`SqliteRepository` cumple el requisito de sobrevivir a reinicios
(consigna §3.3, prueba 7); `InMemoryRepository` existe para los tests de
service, que deben correr sin tocar archivos. Las fechas se guardan como
strings 'YYYY-MM-DD HH:MM' (D2), tal como las entregó la validación.
"""

import sqlite3
from pathlib import Path

from reservas.models import Reservation

_SCHEMA = """
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit TEXT NOT NULL,
    requester TEXT NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('activa', 'cancelada'))
)
"""


class Repository:
    """Contrato mínimo que usa el service."""

    def add(self, reservation: Reservation) -> int:
        raise NotImplementedError

    def get(self, reservation_id: int) -> Reservation | None:
        raise NotImplementedError

    def list_by_unit(self, unit: str) -> list[Reservation]:
        raise NotImplementedError

    def all(self) -> list[Reservation]:
        raise NotImplementedError

    def update(self, reservation: Reservation) -> None:
        raise NotImplementedError


class InMemoryRepository(Repository):
    """Repositorio en memoria, para tests aislados de la persistencia."""

    def __init__(self) -> None:
        self._items: dict[int, Reservation] = {}
        self._next_id = 1

    def add(self, reservation: Reservation) -> int:
        reservation.id = self._next_id
        self._items[reservation.id] = reservation
        self._next_id += 1
        return reservation.id

    def get(self, reservation_id: int) -> Reservation | None:
        return self._items.get(reservation_id)

    def list_by_unit(self, unit: str) -> list[Reservation]:
        return [r for r in self._items.values() if r.unit == unit]

    def all(self) -> list[Reservation]:
        return list(self._items.values())

    def update(self, reservation: Reservation) -> None:
        if reservation.id not in self._items:
            raise KeyError(f"No existe la reserva con id {reservation.id}.")
        self._items[reservation.id] = reservation


class SqliteRepository(Repository):
    """Repositorio persistente en un archivo SQLite local."""

    def __init__(self, db_path: str | Path) -> None:
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute(_SCHEMA)
        self._conn.commit()

    def add(self, reservation: Reservation) -> int:
        cursor = self._conn.execute(
            "INSERT INTO reservations (unit, requester, start, end, status) "
            "VALUES (?, ?, ?, ?, ?)",
            (reservation.unit, reservation.requester,
             reservation.start, reservation.end, reservation.status),
        )
        self._conn.commit()
        reservation.id = cursor.lastrowid
        return reservation.id

    def get(self, reservation_id: int) -> Reservation | None:
        row = self._conn.execute(
            "SELECT id, unit, requester, start, end, status "
            "FROM reservations WHERE id = ?",
            (reservation_id,),
        ).fetchone()
        return self._to_reservation(row) if row else None

    def list_by_unit(self, unit: str) -> list[Reservation]:
        rows = self._conn.execute(
            "SELECT id, unit, requester, start, end, status "
            "FROM reservations WHERE unit = ? ORDER BY id",
            (unit,),
        ).fetchall()
        return [self._to_reservation(row) for row in rows]

    def all(self) -> list[Reservation]:
        rows = self._conn.execute(
            "SELECT id, unit, requester, start, end, status "
            "FROM reservations ORDER BY id"
        ).fetchall()
        return [self._to_reservation(row) for row in rows]

    def update(self, reservation: Reservation) -> None:
        cursor = self._conn.execute(
            "UPDATE reservations SET unit = ?, requester = ?, start = ?, "
            "end = ?, status = ? WHERE id = ?",
            (reservation.unit, reservation.requester, reservation.start,
             reservation.end, reservation.status, reservation.id),
        )
        self._conn.commit()
        if cursor.rowcount == 0:
            raise KeyError(f"No existe la reserva con id {reservation.id}.")

    @staticmethod
    def _to_reservation(row: sqlite3.Row) -> Reservation:
        return Reservation(
            id=row["id"], unit=row["unit"], requester=row["requester"],
            start=row["start"], end=row["end"], status=row["status"],
        )
