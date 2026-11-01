# Procedimiento manual de verificación de persistencia

> Objetivo: demostrar de forma reproducible que las reservas **activas y
> canceladas** sobreviven a detener y reiniciar el sistema, sin borrar datos
> (requisito RF-05 de `docs/SPEC.md`). Todo se hace con el punto de entrada
> real (`python -m reservas`) en PowerShell, contra la base de datos real
> (`data/reservas.db`). Sin red, sin credenciales.

## 0. Precondiciones

1. Terminal PowerShell en la raíz del proyecto:
   `cd "C:\Users\Usuario\Desktop\Topicos Ingenieria\TP - Challenge"`.
2. Entorno virtual activado: `.\.venv\Scripts\Activate.ps1`
   (o usar `.\.venv\Scripts\python.exe` explícito en cada comando).
3. Paquete instalado en el venv: `pip install -e .` (solo la primera vez;
   ver `leccion-paquete-instalable.md`).
4. La aplicación NO debe estar en ejecución al comenzar (cada comando se
   ejecuta, termina y libera la base; el "reiniciar" de este procedimiento
   es simplemente ejecutar un proceso nuevo).

**Convención de reinicio:** la aplicación no es un servidor: cada invocación
de `python -m reservas ...` es un proceso completo que abre la base de
datos, opera y la cierra. "Detener y reiniciar" aquí significa terminar un
proceso y ejecutar otro posterior; la persistencia se demuestra en que la
información escrita por procesos anteriores es leída por procesos nuevos.

## 1. Estado inicial (línea de base)

```powershell
python -m reservas listar
```

Esperado: la lista completa de reservas existentes (en la primera ejecución
de este procedimiento: 5 reservas, ids 1 a 5, con actividades y canceladas
mezcladas). Anotar la salida: es el punto de comparación.

## 2. Crear una reserva nueva

```powershell
python -m reservas disponibilidad --unidad MUL-01 --inicio "2026-11-05 14:00" --fin "2026-11-05 15:00"
python -m reservas reservar --unidad MUL-01 --solicitante "Carla Prueba" --inicio "2026-11-05 14:00" --fin "2026-11-05 15:00"
```

Esperado: la unidad `MUL-01` reporta DISPONIBLE y la reserva se registra
con un id nuevo (en la primera ejecución: id 6). Solicitante ficticio.

## 3. REINICIO 1 — lo activo sobrevive

Cerrar el proceso anterior (terminó solo al responder) y ejecutar procesos
nuevos:

```powershell
python -m reservas listar
python -m reservas disponibilidad --unidad MUL-01 --inicio "2026-11-05 14:00" --fin "2026-11-05 15:00"
```

Esperado: (a) `listar` muestra la id nueva con estado `[activa]`, junto con
todo lo anterior intacto; (b) `MUL-01` ahora reporta **OCUPADA** en ese
intervalo.

## 4. Cancelar (no borra: cambia el estado y libera el horario)

```powershell
python -m reservas cancelar --id <id_de_la_reserva_nueva>
```

Esperado: mensaje de cancelación conservando el historial. Si se intenta
cancelar de nuevo, el sistema rechaza con error (estado ya cancelado).

## 5. REINICIO 2 — lo cancelado sobrevive y el horario queda libre

```powershell
python -m reservas listar
python -m reservas disponibilidad --unidad MUL-01 --inicio "2026-11-05 14:00" --fin "2026-11-05 15:00"
```

Esperado: (a) `listar` sigue mostrando la reserva con estado `[cancelada]`,
con sus datos originales (unidad, solicitante, fechas) sin cambios;
(b) `MUL-01` vuelve a reportar **DISPONIBLE** — la cancelación liberó el
horario, pero el registro permanece.

## 6. Verificación a nivel de base de datos (opcional pero recomendable)

```powershell
.\.venv\Scripts\python.exe -c "import sqlite3; con = sqlite3.connect('data/reservas.db'); print(con.execute('SELECT COUNT(*) FROM reservations').fetchone()[0])"
```

Esperado: la misma cantidad de reservas que mostró `listar` (6 en la primer
ejecución: 5 preexistentes + 1 nueva). Ninguna fila se borró; las
canceladas siguen en la tabla con su estado.

## 7. Criterio de aceptación

El procedimiento se considera exitoso si, tras cada reinicio:
- [ ] Las reservas anteriores aparecen exactamente como estaban (estado y datos).
- [ ] La reserva nueva aparece tras el primer reinicio.
- [ ] Tras cancelarla, reaparece tras el segundo reinicio con estado `[cancelada]`.
- [ ] La unidad cancelada vuelve a estar DISPONIBLE para el mismo intervalo.
- [ ] El conteo directo en SQLite coincide con lo que muestra `listar`.

## 8. Registro de ejecuciones

Las corridas de este procedimiento se registran como filas (A) agente y (H)
humano en `docs/evidence/verification-log.md`, con comando, fecha y salida.
