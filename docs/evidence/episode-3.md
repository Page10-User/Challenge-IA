# Episodio 3 — Delegación: documentación y registro de evidencia

Registro conforme a `challenge-agents.md` §4.3 (formato 1→5). Solo se
registró lo ocurrido; no hay transcripciones completas ni fallas inventadas.
Registrado el 2026-11-01; el trabajo cubre el 26/10–01/11.

## 1. Objetivo y requisito

Que el repositorio documente por sí solo qué se construyó y cómo se
comprobó (consigna §3.1 y §4.4): especificación verificable, decisiones con
alternativas descartadas, progreso por tarea y un log de verificación con
los comandos **realmente ejecutados** por agente (A) y humano (H), fallos
incluidos. Regla instituida en `AGENTS.md` §7 desde antes de escribir código.

## 2. → Contexto suministrado y extracto de instrucción

- Contexto: la estructura de evidencia (`docs/SPEC.md`, `DECISIONS.md`,
  `PROGRESS.md`, `docs/evidence/verification-log.md`) fue definida por el
  humano en `AGENTS.md` §5–§7 antes de codificar; el agente la pobló tarea a
  tarea, con aprobación humana del contenido clave (SPEC v1.0).
- Extracto de instrucción del humano (01-11, selección de episodios):
  > "3. Y como tercer episodio, delegación en documentación, donde anotaste
  > (por ejemplo), los comandos y pruebas realizadas en el proceso, tanto
  > mío como tuyos en el verification-log, entre otros (como DECISIONS.md,
  > SPEC.md, PROGRESS.md)."

## 3. → Acción o resultado del agente

- `docs/SPEC.md` v1.0 (`5456bab`): requisitos verificables RF-01..RF-05,
  reglas RG-01..RG-06 y aceptación por criterio; aprobada explícitamente por
  el humano **antes** de la primera implementación.
- `DECISIONS.md` (`1256045`): D0–D4 con motivo y alternativas descartadas;
  todo cambio de dominio requiere decisión humana registrada ahí antes de
  que exista código.
- `PROGRESS.md`: una entrada por fase (objetivo, qué se hizo, archivos,
  verificación con comando y resultado, pendiente, commit).
- `docs/evidence/verification-log.md`: filas (A) del agente y (H) del
  humano, incluyendo **fallos reales** y su corrección (p. ej. `No module
  named reservas`, tabla asumida `reservas` vs `reservations`).
- Integración de evidencia humana sin alterarla: las corridas del humano
  (`op-interno/`: pytest completa en dos entornos, 22 pruebas manuales del
  CLI, repetición del procedimiento de persistencia) se registraron en el
  log citando archivo y resultado exacto, tras leerlos (filas H del 31-10
  y del 01-11).
- Documentos didácticos derivados de errores reales:
  `docs/evidence/leccion-paquete-instalable.md` y
  `docs/evidence/persistence-procedure.md`.

## 4. → Decisión humana (aceptar/corregir/contribuir, con motivo)

- **Aceptar.** La SPEC se aprobó antes de codificar; los docs finales
  (README por secciones, TOOLING.md) se revisaron por diff con OK explícito
  ("Bien, leído y me gustó", "todo checked").
- **Contribución humana real integrada.** El humano aportó evidencia propia
  no versionada (`op-interno/`) y repitió por su cuenta el procedimiento de
  persistencia (5/5 criterios verificados); el agente la integró citándola,
  sin reescribirla.
- **Corrección aceptada en ambos sentidos (caso #16).** El agente demostró
  con la SPEC que la prueba #16 del humano era un falso positivo; el humano
  lo aceptó y decidió **no modificar su registro** (conservar el error como
  valor pedagógico), pidiendo una nota del agente al pie del archivo para
  mantener la transparencia (aplicada en
  `op-interno/Pruebas manuales/pruebas-manuales.md`).

## 5. → Enlaces a commit, archivo, prueba o resultado verificable

- Commits: `5456bab` (SPEC), `1256045` (D0–D4), `a768753` (docs de
  setup/progreso/log), `ba7f329` (procedimiento y evidencia de
  persistencia), `e34705c` (README), `7df5ed3` (TOOLING).
- Archivos: `docs/SPEC.md`, `DECISIONS.md`, `PROGRESS.md`,
  `docs/evidence/verification-log.md`, `docs/evidence/episode-1..3.md`.
- Evidencia humana (sin versionar, referenciada): archivos en `op-interno/`.
