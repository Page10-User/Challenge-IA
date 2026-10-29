# Challenge-IA

Desarrollo de un sistema de reservas de equipos de laboratorio, construido con agentes de programación y evidencia verificable (trabajo individual para Tópicos de Ingeniería).

> **Estado:** Fase 3 (setup del proyecto). Este README se completa por secciones a medida que avanza el trabajo.

## 1. Especificación breve

- **Problema:** la coordinación ficticia de un laboratorio necesita consultar disponibilidad por unidad e intervalo, reservar y cancelar **sin perder el historial**, con persistencia entre reinicios.
- Requisitos verificables, reglas de negocio y criterios de aceptación: [`docs/SPEC.md`](docs/SPEC.md) (v1.0, aprobada por el humano).
- Fuente de los requisitos: [`docs/challenge-agents.md`](docs/challenge-agents.md).

## 2. Solución

- **Stack:** Python 3.12, `sqlite3` (biblioteca estándar) para persistencia, `pytest` para pruebas. Sin interfaz gráfica: consola con subcomandos.
- **Estructura en construcción:** `src/reservas/` (modelos, reglas, repositorio, service, CLI) + `tests/`.
- **Datos:** inventario fijo en `data/inventory.json` (versionado); reservas en `data/reservas.db` (no versionado, se crean al usar la app).
- **Comandos de la app:** se documentan aquí cuando exista la CLI (Fase 4).

## 3. Preparación del agente

- Entorno/harness: agente de código sobre OpenCode (modelo GLM-5.3-Flash via proveedor OpenCode), Windows + PowerShell. Instrucciones del agente: [`AGENTS.md`](AGENTS.md).
- Evidencia de uso real (comandos, versiones, resultados, fallos incluidos): [`docs/evidence/verification-log.md`](docs/evidence/verification-log.md).
- Instrucciones que adaptaron la tarea: convención de intervalos `[inicio, fin)` (ver `DECISIONS.md`, D0) y flujo spec-antes-que-código (AGENTS.md §2).
- Memoria persistente entre sesiones (Engram): clave de proyecto `tp - challenge` (ver `.engram/config.json`).

## 4. Registro de decisiones y delegación

- Decisiones técnicas y de dominio con alternativas descartadas: [`DECISIONS.md`](DECISIONS.md) (D0–D4).
- Episodios de delegación (objetivo → agente → decisión humana → evidencia): `docs/evidence/episode-N.md` cuando ocurran.
- Evaluación de herramientas: `TOOLING.md` (en elaboración).
