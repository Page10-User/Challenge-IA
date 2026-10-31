# Verification log

Comandos realmente ejecutados durante el proyecto, con versión y resultado
(incluidos fallos). La fuente de reglas de este log: AGENTS.md §6/§7 y consigna
§3.3. Distingue lo ejecutado por el agente de lo ejecutado por el humano.

Convención: **(A)** = ejecutado por el agente · **(H)** = ejecutado por el
humano.

Consolidado: fechas en hora local del sistema (UTC-3). Los hashes citados corresponden al estado post-rebase del 27-10-2026; entre paréntesis se citan los originales cuando difieren.

| Fecha | Ejecutor | Comando | Resultado |
|---|---|---|---|
| 26-10 | (A) | `git init -b main` | OK: repo creado (`736b4bb` baseline luego comiteado). |
| 26-10 | (A) | `git config user.name` / `user.email` | Global configurado: "Gonzalo Acostalopez" / gonzalineritolol@gmail.com. |
| 26-10 | (A) | `git add .gitignore AGENTS.md docs/; git commit` | OK: baseline `736b4bb` (4 archivos, 394 ins.). |
| 26-10 | (A) | `git remote add origin https://github.com/Page10-User/Challenge-IA.git` + `git remote -v` | OK: remoto registrado y verificado. |
| 26-10 | (A) | `engram init 'tp - challenge'` | OK: `.engram/config.json` creado (clave de proyecto de memoria). |
| 27-10 | (A) | `engram save '...' --project 'tp - challenge'` (#368, #369, #371, #372) | OK: registro de fases en memoria persistente. |
| 27-10 | (A) | `git push -u origin main` (1er intento) | **FALLO**: `Invalid username or token. Password authentication is not supported`. Credencial vencida en Vault de Windows (GCM). |
| 27-10 | (A) | `git credential-manager github list`; `cmdkey /list` | Diagnóstico: sin cuentas activas en GCM; targets legacy de VS en el Vault. Sin secretos impresos. |
| 27-10 | (H) | `git credential-manager github login` | OK: re-autenticación OAuth (browser), credencial fresca en Vault. |
| 27-10 | (A) | `git push -u origin main` (2do intento) | **FALLO**: `! [rejected] main -> main (fetch first)` — remoto con trabajo no local. |
| 27-10 | (A) | `git fetch origin` + `git log main..origin/main --oneline` + `git ls-tree -r origin/main` | OK: remoto tiene `e90a37a "Initial commit"` (LICENSE + README stub), sin ancestro común (historias independientes). |
| 27-10 | (H) | `git rebase origin/main` | OK: "Successfully rebased and updated refs/heads/main". Evidencia: `op-interno/Primer Push — 27-10-2026.txt` (sin versionar). |
| 27-10 | (H) | `git push -u origin main` | OK: `e90a37a..1256045`, rama `main` tracking `origin/main`. Evidencia: mismo archivo. |
| 28-10 | (A) | `git status -sb` + `git fetch` + `git log --oneline --graph -8` | OK: `main` en sync con `origin/main`; post-rebase: `e90a37a` → `d7c5af1` → `5456bab` → `1256045`. |
| 28-10 | (A) | `py --version` | OK: Python 3.12.2. |
| 28-10 | (A) | `py -m venv .venv` | OK: entorno virtual creado en el repo. |
| 28-10 | (A) | `.venv\Scripts\python.exe -m pip install pytest --quiet` | OK: pytest 9.2.0 (pip 24.0). Aviso de release de pip más nuevo, no accionado (no es requerido). |
| 28-10 | (A) | `.venv\Scripts\python.exe -m pytest --version` | OK: pytest 9.2.0 (sin tests todavía: Fase 4 pendiente). |
| 29-10 | (A) | `pytest tests/test_rules.py -v` (antes de implementar `src/reservas/rules.py`) | **FALLO esperado (rojo TDD)**: `collected 0 items / 1 error` — ImportError de `reservas.rules` inexistente. |
| 29-10 | (A) | `pytest tests/test_rules.py -v` (tras implementar `src/reservas/rules.py`) | OK: `31 passed in 0.11s` — RG-01…RG-08, bordes de D0/D4 y errores propios con mensajes claros. |
| 29-10 | (H) | `pytest .\test_rules.py -v` (pytest global 8.4.2, fuera del venv) | OK: `31 passed in 0.14s` — verificación manual independiente en otro entorno (pinned venv: 9.2.0). Evidencia: `op-interno/Prueba pytest test_rules — 29-10-2026.txt` (sin versionar). |
| 29-10 | (A) | `pytest tests/test_service.py tests/test_persistence.py -v` (antes de implementar models/repository/service) | **FALLO esperado (rojo TDD)**: `collected 0 items / 2 errors` — ImportError de `reservas.models/service`. |
| 29-10 | (A) | `pytest tests/ -v` (tras implementar) | OK: `42 passed in 0.21s` (pytest 9.2.0, Python 3.12.2) — 31 rules + 9 service + 2 persistence. |
| 29-10 | (A) | `pytest tests/test_persistence.py -v` | OK: `2 passed in 0.11s` — prueba 7 del challenge (activas y canceladas sobreviven al reinicio). |
| 30-10 | (H) | `pytest -v .\test_persistence.py .\test_service.py` (pytest global 8.4.2, fuera del venv) | OK: `11 passed in 0.16s` — verificación manual independiente. Evidencia: `op-interno/Prueba pytest test_persistence & service - 30-10-2026.txt` (sin versionar). |
| 30-10 | (H) | `pytest -v .\tests\test_persistence.py .\tests\test_service.py` (venv, pytest 9.2.0) | OK: `11 passed in 0.14s` — misma suite en el entorno pinned. Evidencia: mismo archivo. |
| 30-10 | (A) | `pytest tests/test_cli.py -q` (antes de implementar cli) | **FALLO esperado (rojo TDD)**: ImportError de `reservas.cli`. |
| 30-10 | (A) | `pytest tests/ -v` (tras implementar cli.py + \_\_main\_\_.py) | OK: `49 passed in 0.33s` (42 previos + 7 CLI). |
| 30-10 | (A) | `python -m reservas ...` (smoke del entry point real) | **FALLO**: `No module named reservas` — src-layout sin instalar: la consola no encuentra el paquete por path (los tests solo pasan por inyección de `conftest.py`). |
| 30-10 | (A) | `pip install -e .` (venv; con `pyproject.toml` nuevo) | OK: instalación editable (código 0); `src/reservas` registrado formalmente en el venv. Artefacto `.egg-info/` ignorado por `.gitignore`. |
| 30-10 | (A) | `python -m reservas` (sin subcomando, venv) | OK: menú de bienvenida con lista de comandos; código 0 (sin tocar la DB). Nota: con salida redirigida por pipe los acentos renderizan alterados; en consola interactiva correcto (ver lección §7). |
| 30-10 | (A) | Smoke completo: `reservar` ×2, `disponibilidad`, `cancelar`, `listar` (DB real) | OK: id 1 (MIC-01, Ana Prueba) cancelada conservando historial; id 2 (OSC-01, Beto Prueba) activa; MIC-01 OCUPADA y MIC-02 DISPONIBLE en el mismo intervalo; listar muestra ambos estados. Solicitantes ficticios. |
| 30-10 | (A) | `pytest tests/ -q` (post-instalación) | OK: `49 passed in 0.32s` — la instalación editable no perturba la suite. |
| 31-10 | (H) | `pytest .\tests\ -v` (venv, pytest 9.2.0) | OK: `49 passed in 0.38s` — suite completa post-CLI, incluida la config de `pyproject.toml` (`configfile: pyproject.toml` en la salida). Evidencia: `op-interno/Prueba pytest Suite Completa — 31-10-2026.txt` (sin versionar). |
| 31-10 | (H) | `pytest .\tests\ -v` (pytest global 8.4.2) | OK: `49 passed in 0.34s` — misma suite en otro entorno. Evidencia: mismo archivo. |
