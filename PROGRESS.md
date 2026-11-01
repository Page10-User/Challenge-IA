# PROGRESS

Progreso por tarea según `AGENTS.md` §7. Fechas en hora local; hashes nuevos tras el rebase del 27-10 (se citan ambos cuando aplica).

## 2026-10-26 — Baseline del repositorio (Fase 1)
- Objetivo / requisito: repo versionado como evidencia de "preparación del agente" (consigna §3.1/§4; AGENTS.md §2).
- Qué se hizo: `git init -b main`; creación de `.gitignore` (`.venv/`, `__pycache__/`, `.pytest_cache/`, `data/reservas.db`); commit baseline con `AGENTS.md`, `docs/challenge-agents.md/.pdf` y `.gitignore`; registro del remoto `origin`.
- Archivos tocados: `.gitignore`, `AGENTS.md`, `docs/challenge-agents.md`, `docs/challenge-agents.pdf`.
- Verificación (comando → resultado): `git remote -v` → `origin https://github.com/Page10-User/Challenge-IA.git` (fetch/push); `git log` → baseline presente. Ver `docs/evidence/verification-log.md`.
- Pendiente: SPEC v1.0 (Fase 2).
- Commit: `d7c5af1` (hash post-rebase; original `736b4bb`).

## 2026-10-26 — SPEC v1.0 aprobada y decisiones D0–D4 (Fase 2)
- Objetivo / requisito: spec antes que código (AGENTS.md §2.1) y registro de decisiones significativas (consigna §4.2/§4.4; AGENTS.md §7).
- Qué se hizo: borrado `docs/SPEC.md` v1.0 (reglas RG-01…RG-08, requisitos RF-01…RF-09 con criterios de aceptación, mapeo de pruebas de la consigna §3.3, supuestos, checklist de revisión); creado `DECISIONS.md` con D0–D4 (decisión/motivo/alternativas/consecuencias). Manejo de identidad del proyecto de memoria (Engram) tras `git init`: clave `tp - challenge` fijada en `.engram/config.json` y documentada en AGENTS.md §5/§13. Revisión humana: checklist de SPEC marcado en `[X]`.
- Archivos tocados: `docs/SPEC.md`, `DECISIONS.md`, `.engram/config.json`, `AGENTS.md`.
- Verificación (comando → resultado): revisión y aprobación explícita del humano (checklist `[X]` en SPEC.md); `git log` → commits presentes.
- Pendiente: código con tests primero (Fase 4).
- Commit: `5456bab` (SPEC; original `44c10a3`) y `1256045` (DECISIONS + .engram + AGENTS.md; original `db94465`).

## 2026-10-27 — Primer push al remoto (integración de raíz web)
- Objetivo / requisito: publicar `main` en el repo de entrega (AGENTS.md §9; consigna §5).
- Qué se hizo: primer intento falló por credencial vencida de GitHub en el Vault de Windows (GCM, `credential.helper=manager`); el humano re-autenticó (`git credential-manager github login`, OAuth); el remoto tenía un `Initial commit` web (`e90a37a`: LICENSE + README stub) sin ancestro común → integración decidida por el humano: rebase de nuestros 3 commits sobre `origin/main` + push final con tracking.
- Archivos tocados: ninguno (operación de integración; ver hashes post-rebase citados en las entradas de Fase 1 y 2).
- Verificación (comando → resultado): `git push -u origin main` → `e90a37a..1256045`, rama `main` tracking `origin/main`; evidencia escrita por el humano en `op-interno/Primer Push — 27-10-2026.txt` (sin versionar). Fallos previos registrados en `docs/evidence/verification-log.md`.
- Pendiente: nada remoto pendiente.
- Commit: — (no aplica; hashes de rebase citados en las entradas de Fase 1/2).

## 2026-10-28 — Setup del proyecto (Fase 3)
- Objetivo / requisito: reproducción de app y pruebas sin cuenta de modelo, sin red y sin credenciales (consigna §3.2; AGENTS.md §4).
- Qué se hizo: `py -m venv .venv`; instalación de `pytest 9.2.0` (pinned en `requirements.txt`); `data/inventory.json` con las 5 unidades; `src/reservas/__init__.py`; README con esqueleto de las 4 secciones; `docs/evidence/verification-log.md` con historial de comandos reales (incluidos fallos del push).
- Archivos tocados: `.venv/` (ignorado), `requirements.txt`, `data/inventory.json`, `src/reservas/__init__.py`, `README.md`, `PROGRESS.md`, `docs/evidence/verification-log.md`.
- Verificación (comando → resultado): `py --version` → Python 3.12.2; `.venv\Scripts\python.exe -m pip install pytest --quiet` → instalado; `.venv\Scripts\python.exe -m pytest --version` → pytest 9.2.0; `python -m pytest` aún sin tests (pendiente Fase 4: primer rojo).
- Pendiente: Fase 4 — `tests/test_rules.py` (rojo) → implementación `rules.py`.
- Commit: `97edac4` (chore setup) y `a768753` (docs), aprobados y enviados por el humano.

## 2026-10-29 — Reglas de negocio con TDD (Fase 4a)
- Objetivo / requisito: RG-01…RG-08 en un solo lugar del código y cubiertas por tests de borde (AGENTS.md §3, SPEC RF-04/RF-05, D0/D4); errores propios con mensajes claros (AGENTS.md §11).
- Qué se hizo: TDD completo — se escribió `tests/test_rules.py` (31 casos) contra el contrato de SPEC y se ejecutó **rojo** (ImportError, módulo inexistente); luego se implementó `src/reservas/rules.py` (única función `intervals_overlap`, parse estricto de D2, validaciones en orden estable con reloj inyectado D3) y se volvió a ejecutar el mismo run.
- Archivos tocados: `tests/conftest.py`, `tests/test_rules.py`, `src/reservas/rules.py`.
- Verificación (comando → resultado): rojo `collected 0 items / 1 error` (ImportError) → verde `31 passed in 0.11s` (pytest 9.2.0, Python 3.12.2). Verificación manual adicional del humano con pytest global 8.4.2: `31 passed in 0.14s`. Detalle en `docs/evidence/verification-log.md`.
- Pendiente: Fase 4b — service (reservar/cancelar/disponibilidad), repository (SQLite), tests de service/persistence, CLI.
- Commit: `2f818fe` (feat: reglas de negocio y suite TDD).

## 2026-10-29 — Service, repositorio y persistencia con TDD (Fase 4b)
- Objetivo / requisito: casos de uso (reservar/cancelar/disponibilidad, consigna §3.3 pruebas 1–4 y 6) y persistencia SQLite que sobrevive a reinicios (prueba 7), sin duplicar reglas (RG-02 en un solo lugar; AGENTS.md §2/§3).
- Qué se hizo: TDD — tests de service (InMemoryRepository, reloj inyectado D3) y de persistence (SQLite en tmp_path, reinicio simulado con instancia nueva) escritos primero y corridos en **rojo** (`collected 0 items / 2 errors`, ImportError); luego implementación de `models.py` (Reservation, estados activa/cancelada), `repository.py` (Repository + InMemoryRepository + SqliteRepository, fechas como strings 'YYYY-MM-DD HH:MM' D2) y `service.py` (ReservationService). Refactor single-source: `rules` ahora expone `validate_unit` y `validate_time_window`; `validate_reservation` se compone de ambas y el service reutiliza las mismas funciones en disponibilidad y creación. Contratos previos intactos: 31 tests de rules siguen en verde.
- Archivos tocados: `tests/test_service.py`, `tests/test_persistence.py`, `src/reservas/models.py`, `src/reservas/repository.py`, `src/reservas/service.py`, `src/reservas/rules.py` (refactor sin cambio de comportamiento), `PROGRESS.md`, `docs/evidence/verification-log.md`.
- Verificación (comando → resultado): rojo `collected 0 items / 2 errors` → verde `42 passed in 0.21s` (pytest 9.2.0, Python 3.12.2). Persistencia confirmada aislada: `2 passed in 0.11s`. Verificación manual del humano en dos entornos: global 8.4.2 `11 passed in 0.16s` y venv 9.2.0 `11 passed in 0.14s` (30-10).
- Pendiente: Fase 4c — CLI (`cli.py` + `python -m reservas`), manual de persistencia en `docs/evidence/`, README completado.
- Commit: `3b14c1e`.

## 2026-10-30 — CLI con menú de bienvenida y paquete instalable (Fase 4c)
- Objetivo / requisito: interfaz de consola con subcomandos en español (D1) sin lógica propia (capa fina sobre `service`); RF-03: cancelar conservando historial; disponible y reservable desde la interfaz del usuario real.
- Qué se hizo: TDD — `tests/test_cli.py` (7 casos: menú sin argumentos, reservar válida/inválida, disponibilidad libre/ocupada, cancelar simple/doble/inexistente, listar con estados) corrido en **rojo** (ImportError); implementación de `cli.py` (argparse sin dependencias nuevas, menú estático sin subcomando, mensajes de error de `rules`/`service` a stderr con código de salida 1) y `__main__.py`. Descubrimiento real: el entry point `python -m reservas` falló (`No module named reservas`) y la suite no lo detectaba — el src-layout exige instalar el paquete. Decisión humana aprobada: `pyproject.toml` mínimo + `pip install -e .` (sin dependencias nuevas); smoke completo contra la DB real en verde. Error documentado con enfoque didáctico en `docs/evidence/leccion-paquete-instalable.md` y `AGENTS.md` actualizado (§4 y §13).
- Archivos tocados: `tests/test_cli.py`, `src/reservas/cli.py`, `src/reservas/__main__.py`, `pyproject.toml` (nuevo), `.gitignore` (+`*.egg-info/`), `AGENTS.md` (§4 y §13), `docs/evidence/leccion-paquete-instalable.md` (nueva), `PROGRESS.md`, `docs/evidence/verification-log.md`.
- Verificación (comando → resultado): rojo ImportError → verde `49 passed in 0.33s` (42 previos + 7 CLI); sorpresa: `python -m reservas` global **FALLO** `No module named reservas` (registrado); tras `pip install -e .`: menú OK (código 0), smoke completo OK (2 reservas, superposición, cancelación, listar), `49 passed in 0.32s` post-instalación. Verificación manual del humano (31-10) en dos entornos: venv 9.2.0 `49 passed in 0.38s` y global 8.4.2 `49 passed in 0.34s`. Además, pruebas manuales exploratorias del CLI por el humano (22 casos con conclusiones): `op-interno/Pruebas manuales/pruebas-manuales.md`.
- Pendiente: Fase 5 — manual/procedimiento de persistencia (`docs/evidence/persistence-procedure.md`), README por secciones completado, episodios de delegación cuando el humano marque.
- Nota: `data/reservas.db` contiene 2 reservas ficticias del smoke (Ana/Beto Prueba: id 1 cancelada, id 2 activa); si el manual de persistencia requiere DB limpia, pedirlo explícitamente antes de borrar nada.
- Commit: `026a236`; push `a768753..026a236` (31-10, aprobado por el humano).

## 2026-10-31/01-11 — Procedimiento de persistencia ejecutado (Fase 5.1)
- Objetivo / requisito: RF-05 de la SPEC — reservas activas y canceladas sobreviven a detener y reiniciar el sistema, sin borrar datos; la consigna exige demostrarlo con evidencia.
- Qué se hizo: se escribió `docs/evidence/persistence-procedure.md` (procedimiento reproducible de 7 pasos con criterios de aceptación y convención explícita de reinicio: cada invocación de `python -m reservas ...` es un proceso completo contra `data/reservas.db`). Ejecución (A) completa el 31-10, punta a punta con el entry point real: baseline 5 reservas → reserva MUL-01 2026-11-05 14:00–15:00 (id 6, Carla Prueba) → REINICIO 1: id 6 `[activa]` + MUL-01 OCUPADA → cancelar id 6 + doble cancelación rechazada ("La reserva 6 ya estaba cancelada.", exit 1) → REINICIO 2: id 6 `[cancelada]` con datos intactos + MUL-01 DISPONIBLE → conteo SQLite = 6. Repetición (H) del humano el 01-11 con MIC-02 (id 7, Gon-User-Test, 2026-11-01 14:00 → 2026-11-10 14:00): los 5 criterios de aceptación verificados, conteo SQLite = 7.
- Archivos tocados: `docs/evidence/persistence-procedure.md` (nuevo), `docs/evidence/verification-log.md` (3 filas A + 1 fila H).
- Verificación (comando → resultado): (A) pasos 1–6 OK (con FALLO honesto del primer intento del paso 6: tabla asumida `reservas`, la real es `reservations`, corregido); doble cancelación rechazada; conteo SQLite coincide. (H) 5/5 criterios en verde (`op-interno/Pruebas manuales/persistence-procedure-manual.md`, sin versionar). `pytest tests/ -q` → `49 passed` post-procedimiento.
- Pendiente: Fase 5.2 (README por secciones), 5.3 (TOOLING.md), episodios de delegación cuando el humano marque.
- Nota: la DB real queda con 7 reservas (ids 1–7, ninguna borrada); id 6 (MUL-01/Carla Prueba) e id 7 (MIC-02/Gon-User-Test) en estado `[cancelada]` — evidencia permanente de que cancelar no borra.
- Commit: `ba7f329` (push `026a236..e34705c`, 01-11, aprobado por el humano).

## 2026-11-01 — README completado por secciones (Fase 5.2)
- Objetivo / requisito: README como punto de entrada según `challenge-agents.md` §4.2 — cuatro secciones que expliquen por sí solas qué se construyó y cómo se comprobó (§4.4).
- Qué se hizo: estado actualizado (Fases 1–4 completas, Fase 5 en curso); §1 con resumen de reglas de dominio (5 unidades, D0 semiabiertos con ejemplo, cancelar no borra, D2/D3/D4); §2 reescrita completa: arquitectura en capas (rules única fuente, RG-02), versiones probadas (Python 3.12.2; pytest 9.2.0 venv / 8.4.2 global), instalación con `pip install -e .`, datos con advertencia explícita de que reiniciar NO borra (`docs/evidence/persistence-procedure.md`), comandos reales de la app, ejemplo de entrada/salida con salida real del smoke del 30-10, pendientes y limitaciones (episodios, mini-backlog). §3/§4 intactas hasta que el humano marque episodios y se redacte TOOLING.md. Verificado contra §4.2 líneas 101–108 antes de redactar.
- Archivos tocados: `README.md`.
- Verificación (comando → resultado): releo completo tras editar (1 typo corregido); suite `49 passed` vigente; commit aprobado por el humano tras leer el diff.
- Pendiente: Fase 5.3 (TOOLING.md), episodios de delegación (cuando el humano marque), mini-backlog (en espera de relevación).
- Commit: `e34705c`.

## 2026-11-01 — Evaluación de herramientas y episodios de delegación (Fase 5.3 + cierre de 5)
- Objetivo / requisito: `TOOLING.md` (consigna §3.1: entorno/modelo/instrucciones/herramientas con fallos y descartes) y los tres episodios reales de delegación exigidos por §4.3, seleccionados por el humano.
- Qué se hizo: TOOLING.md creado (harness OpenCode 2.1.4 + GLM-5.3-Flash Free; herramientas con controles; tabla elección vs descartes; 6 fallos reales incluido el patrón de corrupción de texto del agente y el control "releer tras escribir"; bloques de gentle-ai v4.2.0 verificado, declarado como preparación del agente y no del producto). Episodios definidos por el humano: (1) creación y verificación de tests, (2) control de versiones (commit/push; primer push y rebase iniciales reservados al humano), (3) documentación y evidencia. Redactados `docs/evidence/episode-1..3.md` con el formato 1→5 de la consigna, citas verbatim de instrucciones del humano y solo correcciones que ocurrieron (caso #16, falso positivo; paquete no instalable). README §2/§4 actualizados con los enlaces a episodios.
- Archivos tocados: `TOOLING.md`, `README.md`, `docs/evidence/episode-1.md`, `docs/evidence/episode-2.md`, `docs/evidence/episode-3.md`, `PROGRESS.md`.
- Verificación (comando → resultado): releo de los 3 episodios + TOOLING tras editar (correcciones de texto del agente: "Corrección" ×4, "manuale"→"manualmente", citas normalizadas); suite `49 passed` vigente; commits con aprobación explícita del humano.
- Pendiente: mini-backlog (en espera de relevación; D5 requiere DECISIONS + parche de SPEC aprobados).
- Commit: (pendiente).
