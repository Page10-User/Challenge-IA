"""Entidades del dominio de reservas sin lógica de negocio.

La lógica de validación vive en `rules` (única fuente) y los casos de uso
en `service`; este módulo solo describe el dato y su estado.
"""

from dataclasses import dataclass

# Estados de una reserva (RG-03: cancelar no borra, solo cambia el estado).
ACTIVE = "activa"
CANCELLED = "cancelada"


@dataclass
class Reservation:
    """Una reserva del inventario fijo.

    `start` y `end` se manejan como strings en formato estricto
    'YYYY-MM-DD HH:MM' (D2): así la persistencia es transparente y la
    conversión a datetime ocurre solo donde se necesita (reglas/service).
    """

    id: int | None
    unit: str
    requester: str
    start: str
    end: str
    status: str = ACTIVE

    def is_active(self) -> bool:
        return self.status == ACTIVE
