"""Tests de la interfaz de consola (capa fina sobre `service`).

La CLI no debe tener lógica de negocio propia: reserva, cancela y consulta
a través de `ReservationService`, con la DB real reemplazada por una en
tmp_path y el reloj fijo (D3): `datetime.now()` solo vive en la entrypoint
real, jamás en los tests ni en la lógica.
"""

from datetime import datetime
from pathlib import Path

from reservas import cli

# Reloj fijo inyectado (D3): martes 2026-11-10 08:00.
NOW = datetime(2026, 11, 10, 8, 0)


def _run(capsys, tmp_path: Path, argv: list[str]) -> tuple[int, str, str]:
    """Ejecuta la CLI con DB temporal y reloj fijo; devuelve (code, out, err)."""
    code = cli.main(argv, db_path=tmp_path / "cli_test.db", clock=lambda: NOW)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


RESERVA_OK = [
    "reservar", "--unidad", "MIC-01", "--solicitante", "Ana Prueba",
    "--inicio", "2026-11-10 10:00", "--fin", "2026-11-10 11:00",
]


class TestMenuDeBienvenida:
    def test_sin_argumentos_muestra_bienvenida_y_comandos(self, capsys, tmp_path):
        code, out, _ = _run(capsys, tmp_path, [])
        assert code == 0
        assert "Comandos disponibles" in out
        for command in ("disponibilidad", "reservar", "cancelar", "listar"):
            assert command in out


class TestReservar:
    def test_reserva_valida_imprime_confirmacion_con_id(self, capsys, tmp_path):
        code, out, _ = _run(capsys, tmp_path, RESERVA_OK)
        assert code == 0
        assert "Reserva" in out and "id" in out

    def test_input_invalido_reporta_error_y_sale_1(self, capsys, tmp_path):
        bad = ["reservar", "--unidad", "XXX-99", "--solicitante", "Ana Prueba",
               "--inicio", "2026-11-10 10:00", "--fin", "2026-11-10 11:00"]
        code, _, err = _run(capsys, tmp_path, bad)
        assert code == 1
        assert "XXX-99" in err


class TestDisponibilidad:
    def test_reporta_disponible_y_ocupada(self, capsys, tmp_path):
        code, out, _ = _run(capsys, tmp_path, [
            "disponibilidad", "--unidad", "MIC-01",
            "--inicio", "2026-11-10 10:00", "--fin", "2026-11-10 11:00",
        ])
        assert code == 0
        assert "DISPONIBLE" in out

        _run(capsys, tmp_path, RESERVA_OK)
        code, out, _ = _run(capsys, tmp_path, [
            "disponibilidad", "--unidad", "MIC-01",
            "--inicio", "2026-11-10 10:00", "--fin", "2026-11-10 11:00",
        ])
        assert code == 0
        assert "OCUPADA" in out


class TestCancelar:
    def test_cancela_y_el_reintento_rechaza(self, capsys, tmp_path):
        _run(capsys, tmp_path, RESERVA_OK)
        code, out, _ = _run(capsys, tmp_path, ["cancelar", "--id", "1"])
        assert code == 0
        assert "Reserva" in out and "cancelada" in out

        code, _, err = _run(capsys, tmp_path, ["cancelar", "--id", "1"])
        assert code == 1
        assert "ya estaba cancelada" in err

    def test_id_inexistente_rechaza(self, capsys, tmp_path):
        code, _, err = _run(capsys, tmp_path, ["cancelar", "--id", "999"])
        assert code == 1
        assert "No existe" in err


class TestListar:
    def test_lista_incluye_estado_y_marca_canceladas(self, capsys, tmp_path):
        _run(capsys, tmp_path, RESERVA_OK)
        _run(capsys, tmp_path, [
            "reservar", "--unidad", "OSC-01", "--solicitante", "Beto Prueba",
            "--inicio", "2026-11-10 10:00", "--fin", "2026-11-10 11:00",
        ])
        _run(capsys, tmp_path, ["cancelar", "--id", "1"])

        code, out, _ = _run(capsys, tmp_path, ["listar"])
        assert code == 0
        assert "MIC-01" in out and "cancelada" in out
        assert "OSC-01" in out and "activa" in out
