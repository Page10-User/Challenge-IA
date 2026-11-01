# Episodio 1 — Delegación: creación y verificación de las pruebas

Registro conforme a `challenge-agents.md` §4.3 (formato 1→5). Solo se
registró lo ocurrido; no hay transcripciones completas ni fallas inventadas.
Registrado el 2026-11-01; el trabajo cubre el 29–31/10.

## 1. Objetivo y requisito

Cubrir las verificaciones requeridas por la consigna (§3.3) con una suite
`pytest` que pruebe las reglas de negocio **antes** de implementarlas (TDD,
regla de `AGENTS.md` §2): validaciones de entrada, superposición con
intervalos semiabiertos `[inicio, fin)`, disponibilidad, cancelación que
conserva el registro y libera el horario, y persistencia entre reinicios.

## 2. → Contexto suministrado y extracto de instrucción

- Contexto: `docs/SPEC.md` v1.0 aprobada (commit `5456bab`) y decisiones
  D0–D4 en `DECISIONS.md` (`1256045`) **antes** de escribir el primer test;
  fases 4a/4b/4c propuestas por el agente y aprobadas una por una, con la
  regla "tests primero" permanente.
- Extracto de instrucción del humano (01-11, selección de episodios):
  > "1. Delegación en el proceso de las creación de los test, donde vos
  > principalmente los creaste y yo luego los verifiqué y probé manualmente."

## 3. → Acción o resultado del agente

- `tests/test_rules.py` (31 casos): primera fuente; corrido deliberadamente
  en rojo (ImportError) antes de implementar `rules.py`.
- `tests/test_service.py` + `tests/test_persistence.py` (11 casos): rojo
  (`2 errors`) primero; luego `models.py`, `repository.py` (`SqliteRepository`
  + `InMemoryRepository` para reinicio simulado) y `service.py`, con reloj
  inyectado (D3) → verde `42 passed`.
- `tests/test_cli.py` (7 casos): rojo → implementación de `cli.py` como capa
  fina → verde `49 passed` (suite completa).
- Refactor de única fuente: `validate_reservation` compone `validate_unit` +
  `validate_time_window`; disponibilidad y reserva reutilizan las mismas
  funciones (RG-02, sin lógica duplicada).

## 4. → Decisión humana (aceptar/corregir, con motivo)

- **Aceptar, con verificación independiente.** El humano ejecutó la suite por
  su cuenta en dos entornos (venv pytest 9.2.0 y global 8.4.2: `49 passed` en
  ambos — evidencia: `op-interno/Prueba pytest Suite Completa — 31-10-2026.txt`,
  sin versionar) y realizó **22 pruebas manuales exploratorias del CLI** con
  pasos reproducibles (`op-interno/Pruebas manuales/pruebas-manuales.md`).
- **Corrección recíproca real (caso #16).** En esas pruebas manuales el humano
  redactó una expectativa incorrecta: se confundió al **interpretar el formato
  de fecha establecido** (`YYYY-MM-DD HH:MM`, más concretamente en la parte
  `MM-DD`), confusión reforzada por leer los valores fijos de la suite de
  pruebas, y concluyó erróneamente que D3 estaba violado. El
  agente lo contrastó contra la SPEC y demostró que el sistema operó
  correctamente. Decisión humana: **no modificar su registro** (conservar el
  error como valor pedagógico) y pedir una nota al pie del agente que lo
  explique; el humano además re-verificó la regla por su cuenta con una
  fecha de 2025 y confirmó el rechazo esperado ("...lo volví a probar con
  una fecha de '2025' para asegurarme que salte y efectivamente el error
  está contemplado").
- **Corrección del agente aceptada por el humano.** El humo real detectó que
  `python -m reservas` no arrancaba con los tests en verde; el humano aprobó
  la solución propuesta (`pyproject.toml` + `pip install -e .`): "apruebo A".
  Ver `episode-2.md` y `docs/evidence/leccion-paquete-instalable.md`.

## 5. → Enlaces a commit, archivo, prueba o resultado verificable

- Commits: `2f818fe` (rules + 31 tests), `3b14c1e` (service/repository/
  persistencia + tests), `026a236` (CLI + 7 tests).
- Archivos: `tests/test_rules.py`, `tests/test_service.py`,
  `tests/test_persistence.py`, `tests/test_cli.py`, `src/reservas/rules.py`.
- Evidencia: filas (A) y (H) en `docs/evidence/verification-log.md`;
  evidencia humana no versionada en `op-interno/` (ver arriba).
