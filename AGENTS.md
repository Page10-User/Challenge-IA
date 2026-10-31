# AGENTS.md

Instrucciones para agentes de programación que trabajan en este repositorio.
Leer completo antes de actuar. Si algo de este archivo contradice un pedido directo del humano, **avisar y preguntar** antes de continuar.

---

## 1. Qué se está construyendo

Un sistema local y pequeño de **reservas de equipos de laboratorio**: consultar disponibilidad por unidad e intervalo, reservar y cancelar sin perder el historial, con persistencia entre reinicios. Interfaz de consola o API local; sin interfaz gráfica.

Es un trabajo individual de la materia Tópicos de Ingeniería. Además del código, **importa que el repositorio documente cómo se construyó con agentes y cómo se verificó**.

**Fuente de verdad de la consigna:** `docs/challenge-agents.md` (copia en PDF: `docs/challenge-agents.pdf`). Ante duda sobre requisitos, leer ese archivo antes de suponer. No modificarlo.

---

## 2. Flujo de trabajo obligatorio

1. **Spec antes que código.** No escribir código de la aplicación hasta que exista `docs/SPEC.md` y el humano lo haya aprobado explícitamente.
2. **Plan antes de ejecutar.** Para cualquier tarea no trivial, proponer un plan breve (pasos, archivos a tocar, cómo se verificará) y **esperar aprobación**.
3. **Tests primero para reglas de negocio.** Escribir o actualizar el test que falla, luego la implementación, luego ejecutar los tests.
4. **Cambios pequeños.** Una tarea = un cambio acotado = un commit (o pocos).
5. **El humano revisa antes de aceptar.** Mostrar un resumen del diff y los resultados de pruebas. No dar una tarea por cerrada sin ejecutar los tests.
6. **Registrar al cerrar cada tarea** (ver sección 7).

---

## 3. Reglas del dominio

Estas reglas salen de la consigna. Si hay conflicto, manda `docs/challenge-agents.md`.

- Inventario fijo (no hay administración de inventario): `MIC-01`, `MIC-02`, `OSC-01`, `MUL-01`, `FUE-01`. Cada ID es una unidad física distinta. Se carga desde `data/inventory.json`.
- Una reserva tiene: identificador, unidad, solicitante (ficticio), inicio, fin, estado (`activa` | `cancelada`).
- Una reserva **activa** ocupa el intervalo. Una **cancelada** no bloquea.
- **Cancelar no borra:** se conserva identificador y datos, solo cambia el estado.
- Validaciones: unidad conocida; solicitante no vacío ni solo espacios; fechas/horas válidas; inicio **estrictamente anterior** al fin.
- Se rechazan superposiciones de reservas activas de la **misma** unidad. Unidades distintas pueden coincidir en horario.
- La consulta de disponibilidad usa **las mismas reglas** que la creación (una sola función de verdad; no duplicar lógica).

### Convención de intervalos (adaptación específica del proyecto)

Los intervalos son **semiabiertos: `[inicio, fin)`**. Dos intervalos se superponen si y solo si `inicio_a < fin_b` **y** `inicio_b < fin_a`. Por eso 10:00–11:00 y 11:00–12:00 **no** se superponen.
Esta regla debe existir en **un solo lugar** del código y estar cubierta por tests de borde. Cualquier cambio a esta convención requiere decisión humana registrada en `DECISIONS.md`.

### Decisiones resueltas

La interfaz, el formato de fechas/horario, el tratamiento de reservas en el pasado y los límites de duración/anticipación fueron resueltos por el humano (2026-10-26) y están documentados en `docs/SPEC.md` (v1.0) y `DECISIONS.md` (D1–D4). Toda nueva decisión de dominio se registra ahí antes de que exista código. Si una decisión vuelve a volverse ambigua, reabrir el ítem con opciones y preguntar.

---

## 4. Stack y comandos

Stack propuesto (confirmar al crear el proyecto): **Python**, `sqlite3` de la biblioteca estándar para persistencia, `pytest` para pruebas. Dependencias mínimas; no agregar ninguna sin aprobación.

Entorno: Windows, PowerShell. Comandos esperados (ajustar si el proyecto los cambia):

```powershell
# Crear y activar entorno virtual
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependencias y el paquete en modo editable
pip install -r requirements.txt
pip install -e .

# Ejecutar pruebas
python -m pytest -v

# Ejecutar la aplicación (sin subcomando: menú de bienvenida con la lista de comandos)
python -m reservas <subcomando>
```

La aplicación y los tests **deben funcionar sin cuenta de modelo, sin red y sin credenciales**.

---

## 5. Estructura recomendada del repositorio

```
TP - Challenge/
├── AGENTS.md              # este archivo
├── README.md              # entrada del repo, 4 secciones (ver sección 8)
├── PROGRESS.md            # progreso por tarea (versionado)
├── DECISIONS.md           # decisiones y alternativas (versionado)
├── TOOLING.md             # evaluación de herramientas
├── .gitignore
├── .engram/config.json    # clave del proyecto en Engram (memoria persistente)
├── requirements.txt
├── docs/
│   ├── challenge-agents.md    # consigna (no editar)
│   ├── challenge-agents.pdf
│   ├── SPEC.md                # especificación: requisitos verificables y aceptación
│   └── evidence/
│       ├── verification-log.md        # comandos ejecutados, versión, resultado
│       ├── persistence-procedure.md   # procedimiento manual de reinicio (si aplica)
│       └── episode-1.md, episode-2.md, episode-3.md
├── data/
│   ├── inventory.json         # inventario inicial (SÍ se versiona)
│   └── reservas.db            # datos de ejecución (NO se versiona)
├── src/
│   └── reservas/
│       ├── __init__.py
│       ├── models.py          # entidades y estados
│       ├── rules.py           # validaciones + superposición (única fuente)
│       ├── repository.py      # persistencia SQLite
│       ├── service.py         # reservar, cancelar, disponibilidad
│       └── cli.py             # interfaz de consola
└── tests/
    ├── test_rules.py
    ├── test_service.py
    └── test_persistence.py
```

Reglas de estructura:
- Lógica de negocio separada de la interfaz y de la persistencia.
- No crear archivos o carpetas fuera de esta estructura sin avisar.
- `data/reservas.db`, `.venv/`, `__pycache__/`, `.pytest_cache/` van en `.gitignore`.
- La memoria persistente de agentes (Engram) usa la clave de proyecto `tp - challenge`, fijada por `.engram/config.json` (versionado). No renombrar la clave sin decisión registrada: la historia de memoria vive bajo ese nombre.

---

## 6. Pruebas requeridas

Deben existir y ejecutarse (nombres orientativos):

1. Creación válida.
2. Rechazo de superposición (ej.: MIC-01 10:00–11:00 ocupado → rechazar 10:30–11:30).
3. Límites consecutivos permitidos (11:00–12:00 sí).
4. Unidades distintas simultáneas (MIC-02 10:00–11:00 con MIC-01 ocupado).
5. Entradas inválidas: unidad desconocida, solicitante vacío o solo espacios, fecha inválida, inicio ≥ fin.
6. Cancelación: conserva el registro y libera el horario.
7. Persistencia: reservas activas **y** canceladas sobreviven a detener y reiniciar, sin borrar datos.

Al reportar resultados distinguir siempre **lo que el agente afirma** de **lo que se ejecutó realmente**: indicar el comando, la versión de Python/pytest y la salida. Si algo no se ejecutó, decirlo.

---

## 7. Registro de progreso y evidencia

Al cerrar **cada tarea**, el agente actualiza:

- `PROGRESS.md`: qué se hizo, qué quedó pendiente, qué tests se ejecutaron y su resultado.
- `DECISIONS.md`: toda decisión significativa, con motivo y alternativas descartadas.
- `docs/evidence/verification-log.md`: comando ejecutado, versión, resultado (incluidos fallos).

Formato de entrada en `PROGRESS.md`:

```
## YYYY-MM-DD — Título de la tarea
- Objetivo / requisito:
- Qué se hizo:
- Archivos tocados:
- Verificación (comando → resultado):
- Pendiente:
- Commit:
```

### Episodios de delegación

La consigna exige **tres episodios reales** donde el humano delega al agente. Cuando el humano indique que una tarea es un episodio, preparar `docs/evidence/episode-N.md` con: objetivo y requisito → contexto suministrado y extracto de instrucción → acción o resultado del agente → decisión humana (aceptar/corregir/rechazar, con motivo) → enlace a commit/archivo/prueba.
**No inventar fallas ni correcciones.** Solo registrar lo que ocurrió. No adjuntar transcripciones completas.

---

## 8. README

Debe tener cuatro secciones: (1) Especificación breve, (2) Solución, (3) Preparación del agente, (4) Registro de decisiones y delegación. Los detalles de cada sección están en `docs/challenge-agents.md`, sección 4.2. No reescribir el README completo sin pedido; proponer cambios por sección.

---

## 9. Git

- Repositorio remoto (público): `https://github.com/Page10-User/Challenge-IA.git` (remoto `origin`).
  - Verificar con `git remote -v` antes de cualquier `push`. **No cambiar ni agregar remotos sin preguntar.**
  - La autenticación se maneja fuera del repositorio (por ejemplo, `gh auth login`). Nunca escribir tokens ni credenciales en la URL, en archivos ni en comandos mostrados.
- Rama principal y de entrega: `main`. Trabajo en ramas cortas: `feat/...`, `fix/...`, `docs/...`, `test/...`.
- Commits pequeños, en imperativo y con motivo. Formato sugerido: `tipo: descripción` (ej.: `test: agregar casos de borde de intervalos`).
- La spec inicial y cada cambio significativo de requisitos se commitean **por separado**, con el motivo en el mensaje.
- Para GitHub preferir `gh` (GitHub CLI) desde terminal. Mostrar el comando antes de ejecutarlo si crea o modifica algo remoto.

---

## 10. Permisos y límites del agente

**Permitido sin preguntar:**
- Leer archivos del repositorio.
- Ejecutar tests y comandos de solo lectura (`git status`, `git diff`, `git log`).
- Editar archivos dentro de las rutas de la estructura de la sección 5 durante una tarea aprobada.

**Preguntar antes de:**
- Instalar o agregar dependencias.
- Crear, mover o borrar archivos fuera de lo planificado.
- Hacer commits, crear ramas o PRs, o `git push`.
- Cualquier operación remota en GitHub.
- Modificar `docs/challenge-agents.md`, `docs/SPEC.md` aprobado, o la convención de intervalos.

**Prohibido:**
- `git push --force`, reescribir historial, borrar ramas o repos.
- Borrar `data/reservas.db` o datos existentes sin confirmación explícita.
- Incluir secretos, tokens, credenciales, conversaciones privadas completas o datos reales de estudiantes. Los solicitantes son **siempre ficticios** (ej.: "Ana Prueba").
- Leer o escribir fuera de la carpeta del proyecto.
- Afirmar que algo funciona sin haberlo ejecutado.

---

## 11. Estilo de código

- Python con *type hints*; funciones cortas y con un solo propósito.
- Identificadores en inglés; documentación, comentarios y mensajes al usuario en español.
- Errores de validación con excepciones propias y mensajes claros (qué falló y por qué).
- Sin dependencias ocultas ni estado global; la fecha/hora actual se inyecta o se aísla para poder testear.

---

## 12. Definición de "hecho"

Una tarea está hecha cuando:
- [ ] El cambio cumple el requisito de `docs/SPEC.md` al que responde.
- [ ] Los tests relevantes existen y **se ejecutaron**, con resultado registrado.
- [ ] El humano revisó el diff y aceptó (o pidió correcciones).
- [ ] `PROGRESS.md` (y `DECISIONS.md`, si corresponde) están actualizados.
- [ ] No quedaron secretos, datos reales ni archivos fuera de la estructura.
- [ ] El commit enlaza con la tarea.

---

## 13. Historial de este archivo

Este archivo es parte de la evidencia del trabajo (preparación del agente). Cada cambio significativo se commitea con su motivo. Si una instrucción se agrega porque el agente cometió un error o hubo una ambigüedad, anotarlo aquí:

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-10-26 | Se agrega `.engram/config.json` al árbol y una nota sobre la clave de Engram | Tras `git init`, Engram resolvía el proyecto por remoto (`challenge-ia`) en conflicto con la historia existente bajo `tp - challenge`; se fija la clave canónica y se versiona la referencia |
| 2026-10-30 | Se agrega `pip install -e .` al setup y se completa el comando de la app (`python -m reservas`) | El agente detectó en la prueba de humo que `python -m reservas` fallaba (`No module named reservas`): el src-layout exige instalar el paquete; se suma `pyproject.toml` y la instalación editable (lección en `docs/evidence/leccion-paquete-instalable.md`) |