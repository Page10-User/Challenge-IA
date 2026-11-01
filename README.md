# Challenge-IA

Desarrollo de un sistema de reservas de equipos de laboratorio, construido con agentes de programación y evidencia verificable (trabajo individual para Tópicos de Ingeniería).

> **Estado:** Fases 1–4 completas (reglas de dominio, service + persistencia SQLite, CLI, paquete instalable). Fase 5 en curso: cierre documental.

## 1. Especificación breve

- **Problema:** la coordinación ficticia de un laboratorio necesita consultar disponibilidad por unidad e intervalo, reservar y cancelar **sin perder el historial**, con persistencia entre reinicios.
- Requisitos verificables, reglas de negocio y criterios de aceptación: [`docs/SPEC.md`](docs/SPEC.md) (v1.0, aprobada por el humano).
- Reglas de dominio (resumen): inventario fijo de 5 unidades (`MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`); intervalos **semiabiertos** `[inicio, fin)` — 10:00–11:00 y 11:00–12:00 NO se superponen (D0); cancelar **no borra**, solo cambia el estado; reservas activas de la **misma** unidad no pueden superponerse; inicio estrictamente anterior al fin (D4: duración mínima 30 min, anticipación máxima 15 días) y no en el pasado (D3); solicitante no vacío.
- Fuente de los requisitos: [`docs/challenge-agents.md`](docs/challenge-agents.md).

## 2. Solución

### Arquitectura

Tres capas separadas (la interfaz no contiene reglas y las reglas viven en un solo lugar):

- [`src/reservas/rules.py`](src/reservas/rules.py) — **única fuente** de validaciones y superposición (`validate_unit`, `validate_time_window`, `validate_reservation`); disponibilidad y reserva usan las mismas funciones (RG-02).
- [`src/reservas/models.py`](src/reservas/models.py) — entidad `Reservation` con estados `activa` / `cancelada`.
- [`src/reservas/repository.py`](src/reservas/repository.py) — `SqliteRepository` (SQLite estándar) y `InMemoryRepository` para pruebas.
- [`src/reservas/service.py`](src/reservas/service.py) — casos de uso: reservar, cancelar (conserva el registro), disponibilidad.
- [`src/reservas/cli.py`](src/reservas/cli.py) — capa fina sobre el service (argparse, sin dependencias nuevas).

Decisiones técnicas clave (motivo y alternativas en [`DECISIONS.md`](DECISIONS.md)): fechas como strings `YYYY-MM-DD HH:MM` (D2), reloj inyectado para poder testear el pasado (D3), intervalos semiabiertos (D0), límites de duración/anticipación (D4).

### Requisitos previos y versiones

- Python 3.12 (probado con 3.12.2), Windows + PowerShell.
- `pytest` para pruebas (probado con 9.2.0 en venv y 8.4.2 global: suite completa en verde en ambos).
- Sin otras dependencias de ejecución (solo biblioteca estándar).

### Instalación

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .          # el src-layout exige instalar el paquete (ver lección)
python -m pytest -v       # esperado: 49 passed
```

### Datos: dónde persisten y qué pasa al reiniciar

- Inventario fijo: `data/inventory.json` (versionado, 5 unidades; no hay administración de inventario, por consigna).
- Reservas: `data/reservas.db` (SQLite, **no versionado**; se crea automáticamente al usar la app).
- **Advertencia honesta: reiniciar la aplicación o la máquina NO borra datos.** Las reservas activas y canceladas sobreviven entre reinicios — procedimiento reproducido y verificado por el agente y por el humano: [`docs/evidence/persistence-procedure.md`](docs/evidence/persistence-procedure.md).
- La única forma de "reiniciar datos" es borrar `data/reservas.db` a mano; en este proyecto no se hizo sin confirmación explícita. Si alguien la borra, la base inicia vacía (las reservas previas se pierden, son solo datos ficticios).

### Comandos de la aplicación

```powershell
python -m reservas                                                          # sin subcomando: menú de bienvenida
python -m reservas disponibilidad --unidad MIC-01 --inicio "2026-11-10 10:00" --fin "2026-11-10 11:00"
python -m reservas reservar --unidad MIC-01 --solicitante "Ana Prueba" --inicio "2026-11-10 10:00" --fin "2026-11-10 11:00"
python -m reservas cancelar --id 1
python -m reservas listar                                                   # incluye activas y canceladas
```

Formato de fecha/hora estricto: `YYYY-MM-DD HH:MM` (D2). Cada comando imprime su resultado o un error claro con código de salida 1.

### Ejemplo de entrada y salida (salida real, smoke del 30-10)

```text
$ python -m reservas reservar --unidad MIC-01 --solicitante "Ana Prueba" --inicio "2026-11-10 10:00" --fin "2026-11-10 11:00"
Reserva registrada con el id 1 (MIC-01 2026-11-10 10:00 - 2026-11-10 11:00).

$ python -m reservas disponibilidad --unidad MIC-01 --inicio "2026-11-10 10:00" --fin "2026-11-10 11:00"
OCUPADA: MIC-01 2026-11-10 10:00 - 2026-11-10 11:00

$ python -m reservas cancelar --id 1
Reserva 1 cancelada (conserva el historial).

$ python -m reservas listar
1: MIC-01 2026-11-10 10:00 - 2026-11-10 11:00 | Ana Prueba [cancelada]
```

### Pendientes y limitaciones

- Episodios de delegación: pendientes de selección humana (`docs/evidence/episode-N.md` en su momento).
- Mini-backlog en espera (post-fases): rechazo de flags duplicadas en la CLI (hoy argparse aplica "gana la última"), tope máximo de duración de reserva (propuesta D5: 6 meses), hint en `listar -h`.
- Solo interfaz de consola (sin gráficos ni red), por consigna. Solicitantes siempre ficticios.

## 3. Preparación del agente

- Entorno/harness: agente de código sobre OpenCode (modelo GLM-5.3-Flash via proveedor OpenCode), Windows + PowerShell. Instrucciones del agente: [`AGENTS.md`](AGENTS.md).
- Evidencia de uso real (comandos, versiones, resultados, fallos incluidos): [`docs/evidence/verification-log.md`](docs/evidence/verification-log.md).
- Instrucciones que adaptaron la tarea: convención de intervalos `[inicio, fin)` (ver `DECISIONS.md`, D0) y flujo spec-antes-que-código (AGENTS.md §2).
- Memoria persistente entre sesiones (Engram): clave de proyecto `tp - challenge` (ver `.engram/config.json`).

## 4. Registro de decisiones y delegación

- Decisiones técnicas y de dominio con alternativas descartadas: [`DECISIONS.md`](DECISIONS.md) (D0–D4).
- Episodios de delegación (objetivo → agente → decisión humana → evidencia): `docs/evidence/episode-N.md` cuando ocurran.
- Evaluación de herramientas (elección, descartes, aciertos y fallos reales): [`TOOLING.md`](TOOLING.md).
