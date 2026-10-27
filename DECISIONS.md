# Decisiones del proyecto

Registro versionado de decisiones significativas: qué se decidió, por qué, qué alternativas se descartaron y qué consecuencias tiene. Las decisiones PENDIENTES de `AGENTS.md` (§3) se resolvieron con el humano el 2026-10-26 y generaron D1–D4. La D0 ya venía de la adaptación específica documentada en `AGENTS.md`.

| ID | Tema | Decisión (resumen) | Aprobación |
|---|---|---|---|
| D0 | Convención de intervalos | Semiabierta `[inicio, fin)` | Adaptación del proyecto (AGENTS.md) |
| D1 | Interfaz | Consola con subcomandos | Humano, 2026-10-26 |
| D2 | Zona horaria y formato | Hora local, `YYYY-MM-DD HH:MM` | Humano, 2026-10-26 |
| D3 | Reservas en el pasado | Rechazar si `inicio < ahora` | Humano, 2026-10-26 |
| D4 | Límites | Duración mín. 30 min; anticipación máx. 15 días | Humano, 2026-10-26 |

---

## D0 — Convención de intervalos: semiabierta `[inicio, fin)` (2026-10-26)

**Decisión:** dos intervalos se superponen si y solo si `inicio_a < fin_b` y `inicio_b < fin_a`. Consecuencia: 10:00–11:00 y 11:00–12:00 **no** se superponen; los límites consecutivos están permitidos y son consecutivos reales, sin hueco implícito.

**Motivo:** la consigna exige "permitir límites consecutivos" (§2) y el ejemplo de `10:00–11:00` seguido de `11:00–12:00` como posibilidad. Una convención cerrada `[inicio, fin]` obligaría a reglas adicionales para ese caso; la semiabierta hace que una única condición general produzca exactamente el comportamiento pedido.

**Adaptación específica:** esta convención es la adaptación aportada por el proyecto a la consigna (§3.1 del challenge). Debe existir en **un solo lugar** del código (`src/reservas/rules.py`) cubierta con tests de borde. Cambiarla requiere nueva decisión humana aquí registrada.

**Alternativas descartadas:**
- Intervalos cerrados `[inicio, fin]` con poda de igualdad: agrega reglas especiales para el caso exacto y es más fácil de implementar mal.
- Intervalos con margen de "cambio de turno" (p. ej. 5 minutos entre reservas): fuente de ambigüedad sobre cuál margen aplicar; el challenge no la pide.

**Consecuencia:** disponibilidad, creación, listado y cualquier análisis comparten la misma función de superposición, escrita una sola vez.

## D1 — Interfaz: consola con subcomandos (2026-10-26)

**Decisión:** CLI local `python -m reservas <subcomando>` con comandos `disponibilidad`, `reservar`, `cancelar`, `listar`. Nombres en español para el usuario; identificadores de código en inglés (`rules.py`, `service.py`, etc.).

**Motivo:** sin dependencias (el stack es minimalista), verificación reproducible al 100% por consola y tests, sin puerto ni protocolo HTTP que documentar. Encaja con "pequeño y verificable".

**Alternativas descartadas:**
- API local HTTP (FastAPI o similar): agrega dependencia externa, servidor con ciclo de vida y capas de depuración; sin beneficios que encajen en el alcance del challenge.

**Consecuencia:** no hay GUI (conforme a la consigna); toda acción es ejecutable en un comando con salida observable y exit codes (`0`/`1`).

## D2 — Zona horaria y formato de fechas: hora local + `YYYY-MM-DD HH:MM` (2026-10-26)

**Decisión:** entrada y salida usan hora local con el formato `YYYY-MM-DD HH:MM`; resolución al minuto (sin segundos). La zona horaria queda aislada/inyectable para que los tests sean independientes de la máquina.

**Motivo:** es el formato que el coordinador del laboratorio naturalmente escribe/lee y mantiene un orden lexicográfico utilizable en SQLite. Complicar con UTC o sufijos de zona no hacía falta ya que todo es local.

**Alternativas descartadas:**
- UTC + ISO 8601 con desplazamiento (`2026-10-27T10:00:00-03:00`): carga interpretativa innecesaria para el usuario y redundante para un sistema local.
- Naive "sin zona declarada": ambiguo y depende de la zona horaria oculta de cada entorno; documentar explícitamente la local reduce ese riesgo sin eliminarlo.

**Consecuencia:** la app solo acepta e imprime `YYYY-MM-DD HH:MM`; casos como `2027-03-02 25:00` o `2026-02-30 10:00` son errores de formato y no se autocorrigen.

## D3 — Reservas en el pasado: rechazo si `inicio < ahora` (2026-10-26)

**Decisión:** el sistema rechaza una reserva cuyo `inicio` es anterior al momento actual. El "ahora" se pasa inyectado al servicio (no se llama `datetime.now()` dentro de la lógica), permitiendo tests deterministas.

**Motivo:** en un sistema de reservas, un intervalo pasado casi siempre refleja un error de carga (año u hora mal tipeada) y, en un sistema confiable, merece un rechazo explícito; en este alcance el coordinador no registra utilización retroactiva.

**Alternativas descartadas:**
- Permitir sin validar: más simple, pero admite "reservar" en el pasado, lo que contamina el historial de activas para el mismo intervalo.
- Rechazar solo si `fin < ahora`: permite crear reservas cuyo inicio ya pasó (ej. hoy por la mañana); dificultad adicional para definir su disponibilidad actual.

**Consecuencia:** los tests controlan tiempo con "ahora" ficticio; el README advertirá que no funciona para registrar uso retroactivo.

## D4 — Límites de duración y anticipación: mín. 30 min; máx. 15 días (2026-10-26)

**Decisión:** se rechaza una reserva si su duración es menor a 30 minutos o si su `inicio` es posterior a `ahora + 15 días`. Casos borde permitidos: duración de 30 minutos justos; `inicio` exactamente 15 días en el futuro. `fin` no tiene tope adicional; solo aplica `inicio < fin` (RG-05) y la duración mínima (RG-08).

**Motivo:** criterio del humano, que quiso mayor exigencia y fijó la ventana de anticipación en 15 días (sobre la propuesta inicial de 30); se registra tal cual para que el spec capture los bordes con precisión.

**Alternativas descartadas:**
- Sin límites (solo `inicio < fin`): más simple, pero admite errores de carga (como una reserva de 5 minutos) y reservas muy lejanas fuera de la ventana útil del laboratorio.

**Consecuencia:** dos errores nuevos de negocio con mensajes propios; dos tests de borde por límite en `tests/test_rules.py`.

---

**Nota de contenido:** no hay secretos, datos reales de estudiantes ni transcripciones privadas aquí; los solicitantes en ejemplos son ficticios.
