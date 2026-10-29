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
- Commit: (pendiente de aprobación del humano).
