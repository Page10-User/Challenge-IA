"""Tests de reglas de negocio (RG-01 a RG-08, SPEC v1.0).

Cubre: entradas inválidas (consigna §3.3 prueba 5) y los casos borde de los
límites D4 y de la convención de intervalos D0. El reloj siempre se inyecta
(D3): ningún test depende de la hora real del sistema.
"""

from datetime import datetime, timedelta

import pytest

from reservas import rules
from reservas.rules import (
    EmptyRequesterError,
    InvalidDatetimeError,
    InvalidIntervalError,
    PastStartError,
    TooFarAheadError,
    TooShortDurationError,
    UnknownUnitError,
)

# "Ahora" fijo: martes 2026-11-10 08:00 (naive local, según D2/D3).
NOW = datetime(2026, 11, 10, 8, 0)

UNITS = {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"}


def _valid(unit: str = "MIC-01", requester: str = "Ana Prueba",
           start: str = "2026-11-10 10:00", end: str = "2026-11-10 11:00") -> dict:
    return {"unit": unit, "requester": requester, "start": start, "end": end}


class TestDatosValidos:
    def test_creacion_valida_devuelve_intervalo_parseado(self):
        parsed = rules.validate_reservation(NOW, UNITS, **_valid())
        assert parsed == (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))

    def test_todas_las_unidades_conocidas_aceptan(self):
        for unit in UNITS:
            rules.validate_reservation(NOW, UNITS, unit=unit,
                                       requester="Ana Prueba",
                                       start="2026-11-10 10:00",
                                       end="2026-11-10 10:30")

    def test_solicitante_con_texto_acepta_sin_importar_espacios_internos(self):
        # Los espacios internos NO invalidan; solo el vacío y el "solo espacios" (RG-04).
        rules.validate_reservation(NOW, UNITS, unit="MIC-01", requester="Ana  Prueba",
                                   start="2026-11-10 10:00", end="2026-11-10 10:30")


class TestUnidad:
    def test_unidad_desconocida_rechaza(self):
        with pytest.raises(UnknownUnitError) as exc:
            rules.validate_reservation(NOW, UNITS, unit="XXX-99", requester="Ana Prueba",
                                       start="2026-11-10 10:00", end="2026-11-10 10:30")
        assert "XXX-99" in str(exc.value)


class TestSolicitante:
    @pytest.mark.parametrize("requester", ["", "   ", "\t\n"])
    def test_solicitante_vacio_o_solo_espacios_rechaza(self, requester):
        with pytest.raises(EmptyRequesterError):
            rules.validate_reservation(NOW, UNITS, unit="MIC-01", requester=requester,
                                       start="2026-11-10 10:00", end="2026-11-10 10:30")


class TestFechas:
    @pytest.mark.parametrize("raw", [
        "2026-11-10 9:00",      # sin cero inicial en la hora (formato estricto D2)
        "2026-1-10 10:00",      # sin cero inicial en el mes
        "2026/11/10 10:00",     # separador incorrecto
        "2026-02-30 10:00",     # fecha imposible
        "2026-11-10 25:00",     # hora imposible
        "2026-11-10",           # falta la hora
        "garbage",              # no es una fecha
    ])
    def test_formato_invalido_rechaza(self, raw):
        data = _valid(start=raw, end="2026-11-10 11:00")
        with pytest.raises(InvalidDatetimeError) as exc:
            rules.validate_reservation(NOW, UNITS, **data)
        assert raw in str(exc.value)

    def test_formato_invalido_en_end_rechaza(self):
        data = _valid(start="2026-11-10 10:00", end="2026-11-10 10:60")
        with pytest.raises(InvalidDatetimeError):
            rules.validate_reservation(NOW, UNITS, **data)


class TestIntervalo:
    def test_inicio_igual_al_fin_rechaza(self):
        data = _valid(start="2026-11-10 10:00", end="2026-11-10 10:00")
        with pytest.raises(InvalidIntervalError):
            rules.validate_reservation(NOW, UNITS, **data)

    def test_inicio_posterior_al_fin_rechaza(self):
        data = _valid(start="2026-11-10 11:00", end="2026-11-10 10:00")
        with pytest.raises(InvalidIntervalError):
            rules.validate_reservation(NOW, UNITS, **data)


class TestPasado:
    def test_inicio_en_pasado_rechaza(self):
        data = _valid(start="2026-11-10 07:59", end="2026-11-10 08:59")
        with pytest.raises(PastStartError) as exc:
            rules.validate_reservation(NOW, UNITS, **data)
        assert "2026-11-10 07:59" in str(exc.value)

    def test_inicio_exactamente_al_presente_acepta(self):
        # Borde de D3: se rechaza si inicio < ahora; igual ya no es pasado.
        rules.validate_reservation(NOW, UNITS, unit="MIC-01", requester="Ana Prueba",
                                   start="2026-11-10 08:00", end="2026-11-10 09:00")


class TestDuracionMinima:
    def test_duracion_de_29_minutos_rechaza(self):
        data = _valid(start="2026-11-10 10:00", end="2026-11-10 10:29")
        with pytest.raises(TooShortDurationError):
            rules.validate_reservation(NOW, UNITS, **data)

    def test_duracion_de_30_minutos_justos_acepta(self):
        # Borde de RG-08: duración de 30 minutos exactos está permitida.
        rules.validate_reservation(NOW, UNITS, unit="MIC-01", requester="Ana Prueba",
                                   start="2026-11-10 10:00", end="2026-11-10 10:30")


class TestAnticipacionMaxima:
    def test_anticipacion_de_15_dias_y_un_minuto_rechaza(self):
        # 2026-11-25 08:01 es el tope exacto (NOW + 15 días) más un minuto.
        data = _valid(start="2026-11-25 08:01", end="2026-11-25 08:31")
        with pytest.raises(TooFarAheadError):
            rules.validate_reservation(NOW, UNITS, **data)

    def test_anticipacion_de_15_dias_justos_acepta(self):
        # Borde de RG-07: `inicio <= ahora + 15 días` exactos, permitido.
        limite = NOW + timedelta(days=15)
        rules.validate_reservation(NOW, UNITS, unit="MIC-01", requester="Ana Prueba",
                                   start=limite.strftime("%Y-%m-%d %H:%M"),
                                   end=(limite + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M"))


class TestSuperposicion:
    """La función única de superposición (D0): `aI < bF y bI < aF`."""

    def test_solapamiento_parcial_se_detecta(self):
        a = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        b = (datetime(2026, 11, 10, 10, 30), datetime(2026, 11, 10, 11, 30))
        assert rules.intervals_overlap(*a, *b) is True

    def test_limites_consecutivos_despues_no_se_superponen(self):
        a = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        b = (datetime(2026, 11, 10, 11, 0), datetime(2026, 11, 10, 12, 0))
        assert rules.intervals_overlap(*a, *b) is False

    def test_limites_consecutivos_antes_no_se_superponen(self):
        a = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        b = (datetime(2026, 11, 10, 9, 0), datetime(2026, 11, 10, 10, 0))
        assert rules.intervals_overlap(*a, *b) is False

    def test_toque_interno_se_detecta(self):
        a = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        b = (datetime(2026, 11, 10, 9, 30), datetime(2026, 11, 10, 10, 1))
        assert rules.intervals_overlap(*a, *b) is True

    def test_contencion_entra_incluso_cuando_comparten_inicio(self):
        a = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 12, 0))
        b = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        assert rules.intervals_overlap(*a, *b) is True

    def test_intervalos_identicos_se_superponen(self):
        a = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        b = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        assert rules.intervals_overlap(*a, *b) is True

    def test_intervalos_separados_no_se_superponen(self):
        a = (datetime(2026, 11, 10, 10, 0), datetime(2026, 11, 10, 11, 0))
        b = (datetime(2026, 11, 10, 12, 0), datetime(2026, 11, 10, 13, 0))
        assert rules.intervals_overlap(*a, *b) is False

    def test_intervalos_de_dias_distintos_no_se_superponen(self):
        a = (datetime(2026, 11, 10, 22, 0), datetime(2026, 11, 10, 23, 0))
        b = (datetime(2026, 11, 11, 9, 0), datetime(2026, 11, 11, 10, 0))
        assert rules.intervals_overlap(*a, *b) is False
