# SPEC — Sistema de reservas de equipos de laboratorio

**Versión:** 1.0 · **Fecha:** 2026-10-26 · **Estado:** borrador para aprobación humana (se comitea aparte, con el motivo en el mensaje).

Sistema local de consola para un laboratorio ficticio: consultar disponibilidad por unidad e intervalo, reservar y cancelar **sin perder el historial**, con persistencia en SQLite entre reinicios. App y pruebas se reproducen sin cuenta de modelo, sin red y sin credenciales.

Fuente de los requisitos: `docs/challenge-agents.md` (no se modifica). Nada de este spec contradice ese documento.

## Uso rápido

```powershell
python -m reservas disponibilidad --unidad MIC-01 --desde "2026-10-27 10:00" --hasta "2026-10-27 11:00"
python -m reservas reservar --unidad MIC-01 --solicitante "Ana Prueba" --desde "2026-10-27 10:00" --hasta "2026-10-27 11:00"
python -m reservas cancelar --id 1
python -m reservas listar
python -m pytest -v
```

Códigos de salida: `0` éxito; `1` error de validación o negocio con mensaje claro (qué falló y por qué).

## Alcance y fuera de alcance

**Alcance:** inventario fijo leído de `data/inventory.json`; disponibilidad, reservas y cancelaciones persistidas en `data/reservas.db` (SQLite); interfaz de consola con subcomandos (D1).

**Fuera de alcance (consigna §3.2):** autenticación y roles reales, notificaciones, pagos, integraciones externas, despliegue obligatorio, interfaz gráfica, concurrencia distribuida y escalabilidad de producción. Tampoco hay administración del inventario.

## Inventario (fijo, de `data/inventory.json`)

| ID | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

Cada ID es una unidad física distinta. El archivo se versiona; no hay comandos para modificarlo.

## Decisiones resueltas (resumen; detalle en `../DECISIONS.md`)

| ID | Tema | Decisión |
|---|---|---|
| D0 | Convención de intervalos | Semiabierta `[inicio, fin)` |
| D1 | Interfaz | Consola con subcomandos (en español para el usuario) |
| D2 | Fechas/horas | Hora local, formato de entrada/salida `YYYY-MM-DD HH:MM`; resolución al minuto |
| D3 | Reservas en el pasado | Se rechaza si `inicio < ahora`; el "ahora" se inyecta al servicio para que los tests sean deterministas |
| D4 | Límites | Duración mínima 30 min; anticipación máxima 15 días |

La convención `[inicio, fin)` vive en **un solo lugar** del código (`src/reservas/rules.py`) y está cubierta por tests de borde. Cambiarla requiere decisión humana registrada en `DECISIONS.md`.

## Reglas de negocio

| ID | Regla |
|---|---|
| RG-01 | Dos intervalos `[aI, aF)` y `[bI, bF)` se superponen si y solo si `aI < bF` y `bI < aF`. Por eso 10:00–11:00 y 11:00–12:00 **no** se superponen (límites consecutivos permitidos). |
| RG-02 | Una reserva **activa** ocupa el intervalo; una **cancelada** no bloquea disponibilidad. |
| RG-03 | Una reserva involucra **una** unidad. Se rechaza toda superposición con reservas activas de la **misma** unidad; unidades distintas pueden coincidir en horario. |
| RG-04 | `solicitante` ficticio; no vacío ni compuesto solo por espacios. |
| RG-05 | `inicio` estrictamente anterior a `fin`. |
| RG-06 | Fechas/horas bien formadas en `YYYY-MM-DD HH:MM` (p. ej. `2026-02-30` es inválido). |
| RG-07 | Anticipación máxima: se rechaza si `inicio > ahora + 15 días`. El caso borde es `inicio == ahora + 15 días` exactos (permitido). Solo se limita `inicio`; `fin` puede caer más allá de ese tope. |
| RG-08 | Duración mínima: se rechaza si `fin - inicio < 30 minutos`. El caso borde es una duración de 30 minutos justos (permitida). |

Estados posibles de una reserva: `activa` · `cancelada`. Cancelar no elimina: conserva identificador y datos, solo cambia el estado.

## Requisitos funcionales y criterios de aceptación

| ID | Requisito | Criterio de aceptación (verificable) |
|---|---|---|
| RF-01 | Cargar inventario desde `data/inventory.json` al iniciar. | Con archivo válido, los IDs conocidos son exactamente los 5 de la tabla; con archivo faltante o inválido, la app termina con error claro y exit ≠ 0. |
| RF-02 | Consultar disponibilidad por unidad e intervalo. | `disponibilidad` sobre una unidad sin reservas activas que superpongan imprime `Disponible`; si existe una activa superpuesta (RG-01), imprime `No disponible` e identifica la reserva bloqueante. Unidad desconocida → error. |
| RF-03 | Crear una reserva con unidad, solicitante, inicio y fin; toda reserva tiene identificador único y estado inicial `activa`. | `reservar` válido imprime el ID y los datos; una consulta posterior del mismo intervalo muestra `No disponible`. El identificador se usa en `cancelar` y en `listar`. |
| RF-04 | Validar todas las reglas RG-04…RG-08 antes de registrar nada. | Cada violación produce un mensaje específico, exit ≠ 0 y **no** se registra la reserva. Casos borde cubiertos: solicitante `"   "`, `2026-02-30 10:00`, `inicio == fin`, `inicio > fin`, inicio en pasado, duración de 29 min (rechazo) y de 30 min justos (permitida), anticipación de 15 días justos (permitido) y 15 días + 1 minuto (rechazo). |
| RF-05 | Rechazar superposición de reservas activas de la misma unidad usando la **misma** regla que la disponibilidad. | Con MIC-01 activa 10:00–11:00: rechazar 10:30–11:30; aceptar 11:00–12:00; aceptar MIC-02 10:00–11:00 (con MIC-01 ocupado). La única definición de superposición vive en `src/reservas/rules.py`. |
| RF-06 | Cancelar por ID conservando el registro. | Tras `cancelar`: el registro sigue existiendo con estado `cancelada` (visible en `listar`), el intervalo vuelve a `Disponible` y una nueva reserva sobre ese intervalo es aceptada. Cancelar un ID inexistente o ya cancelada → error. |
| RF-07 | Persistir reservas y estados entre reinicios. | Procedimiento manual reproducible (`docs/evidence/persistence-procedure.md`): crear una reserva, cancelar otra, cerrar y reabrir la app → ambas siguen presente, la activa bloquea y la cancelada no, sin borrar `data/reservas.db`. |
| RF-08 | Listar todas las reservas (soporte para verificación). | `listar` imprime id, unidad, solicitante, intervalo y estado de cada reserva, incluidas las canceladas. |
| RF-09 | Separación de responsabilidades: reglas (`rules.py`), persistencia (`repository.py`), casos de uso (`service.py`) y consola (`cli.py`). | La lógica de negocio no se duplica en la CLI ni en la capa de datos: `service.py` delega en `rules.py`; `cli.py` no implementa reglas. |

## Pruebas requeridas (mapeo con la consigna §3.3)

| # Consigna | Archivo | Cómo se verifica |
|---|---|---|
| 1. Creación válida | `tests/test_service.py` | Caso feliz RF-03 con el "ahora" inyectado. |
| 2. Rechazo de superposición | `tests/test_service.py` | MIC-01 10:00–11:00 activa → rechazar 10:30–11:30 (RF-05, RG-01). |
| 3. Límites consecutivos | `tests/test_service.py` | Aceptar 11:00–12:00 con 10:00–11:00 activa (RG-01, RG-02). |
| 4. Unidades distintas simultáneas | `tests/test_service.py` | MIC-02 10:00–11:00 aceptada con MIC-01 ocupado (RG-03). |
| 5. Entradas inválidas | `tests/test_rules.py` | Unidad desconocida, solicitante vacío o `"   "`, fecha mal formada tal como `2026-02-30`, `inicio >= fin`, inicio en pasado, duración < 30 min, anticipación > 15 días (RF-04). |
| 6. Cancelación conserva registro y libera | `tests/test_service.py` | RF-06 completo, incluido re-reservar el horario liberado. |
| Persistencia | `tests/test_persistence.py` + procedimiento manual | RF-07: activas **y** canceladas sobreviven a detener y reiniciar sin borrar datos. |

Toda prueba trabaja con reloj aislado: el "ahora" (D3) se pasa por parámetro; la lógica no llama `datetime.now()` directamente.

## Supuestos y convenciones adicionales

1. Identificador de reserva: entero secuencial autoincremental gestionado por SQLite. Aparece en `listar`, `cancelar` y en la salida de `reservar`.
2. Cancelar una reserva ya cancelada es error explícito ("ya está cancelada"), no una operación silenciosa.
3. Uso local de un solo usuario: sin bloqueos; la concurrencia queda fuera de alcance.
4. Los solicitantes son siempre ficticios (p. ej. `Ana Prueba`); el sistema no valida identidad.
5. Las fechas se almacenan en SQLite como cadenas `YYYY-MM-DD HH:MM` (D2), ordenables lexicográficamente en consultas.
6. Si `data/reservas.db` se corrompe o se quiere partir de cero: borrar el archivo y reiniciar la app (reset manual documentado en el README; no es automatizado).

## Checklist de revisión (para el humano)

- [X] D1–D4 reflejan exactamente lo decidido en la conversación.
- [X] La convención `[inicio, fin)` y los límites de D4 están bien capturados (incluidos los casos borde).
- [X] Los comandos propuestos y sus mensajes de salida coinciden con lo esperado.
- [X] Los criterios de aceptación de RF-01…RF-09 son verificables sin herramientas extra.

## Evolución

La versión inicial queda registrada en Git; cada cambio significativo se comitea aparte con su motivo. No se exige un mínimo de commits.
