# Evaluación de herramientas

Evaluación honesta de las herramientas usadas en el proyecto: qué contribuyó,
qué no, qué se descubrió y qué alternativas fueron descartadas, con su
motivo. Enlazado desde el README (§4). Conforme a lo que pide la consigna
(§3.1): entorno, versión e identificador del modelo con su motivación,
instrucciones y herramientas usadas, y aprobaciones humanas aplicadas.

## 1. Harness y modelo

| Ítem | Detalle |
|---|---|
| Harness | OpenCode `v2.1.4` (TUI sobre Windows + PowerShell) |
| Modelo | `GLM-5.3-Flash Free`, proveedor OpenCode |
| Función | Agente de programación sobre el repositorio con herramientas reales (leer, escribir, editar, buscar, ejecutar shell, git) |
| Motivo de la elección | Acceso disponible durante el bloque gratuito del curso; cumple el requisito de la consigna (un agente sobre el repo basta), sin servicios pagos |
| Declaración de límites | No participó otro modelo ni agentes en paralelo; lo no visible se declara sin inventarlo |

**Plugin del harness: `gentle-ai` `v4.2.0`** (verificado con `gentle-ai --version`). Configura OpenCode: define el agente de trabajo usado ("Gentleman", con reglas de colaboración y de verificación), la carga dinámica de `AGENTS.md` del repositorio como instrucciones del agente y la integración con Engram (memoria) descrita en §2. **Es preparación del agente, no del producto:** la aplicación y sus pruebas se reproducen por sí solas sin este plugin (sin cuenta de modelo, sin red, sin servicios pagos); se declara por transparencia de evidencia, no como dependencia del sistema.

## 2. Herramientas del agente realmente usadas, con controles

- **Shell (PowerShell)**: ejecución real de pytest, la app CLI, `pip`, `git`. Los comandos y salidas quedaron registrados en `docs/evidence/verification-log.md` (filas A).
- **Lectura/escritura/edición de archivos**: redacción de código, tests y evidencia. Control aplicado: cada tarea se delimitó a los paths permitidos por `AGENTS.md` §5; fuera de la estructura se pidió permiso (ej.: `pyproject.toml` fue aprobado antes de crearse).
- **Búsqueda (grep/glob)**: localización de símbolos y documentación existente.
- **Memoria persistente (Engram, MCP)**: retención de progreso y decisiones entre sesiones (clave de proyecto `tp - challenge`, `.engram/config.json`). Es un extra, no un requisito de la consigna; se usó como bitácora de contexto, mientras la evidencia formal vive versionada en el repo (`PROGRESS.md`, `DECISIONS.md`, logs).
- **Aprobaciones humanas aplicadas**: ningún commit, push, dependencia nueva o borrado de datos pasó sin pregunta previa (regla de `AGENTS.md` §10). El humano revisó diffs y ejecutó la suite por su cuenta (filas H del log de verificación).

## 3. Herramientas de desarrollo: elección y descartes

| Elección | Alternativa descartada | Motivo |
|---|---|---|
| `sqlite3` (biblioteca estándar) | Archivo JSON plano | La consigna pide sobrevivir a reinicios con historial; SQLite resuelve atomicidad y consultas sin dependencias nuevas. Un JSON requeriría serializar/reescribir todo y incrementa el riesgo de corrupción |
| `pytest` | `unittest` | Fixtures (tmp_path, inyección de reloj y repositorio), aserciones planas y parametrización de bordes (31 casos de reglas). El costo de su dependencia de desarrollo es justificado y `AGENTS.md` lo fijó como stack al crear el proyecto |
| `argparse` (biblioteca estándar) | `click`/`typer` | Subcomandos en español con cero dependencias nuevas; la limitación conocida (flags duplicadas) quedó registrada en el mini-backlog en vez de agregar un paquete por eso |
| `pyproject.toml` + `pip install -e .` | `PYTHONPATH` o estructura plana | La estructura plana es válida, pero el src-layout ya estaba elegido; el packaging formal es la mitad del diseño de esa estructura (lección documentada) |
| Git + GitHub (operaciones remotas con `git push` desde el repo) | — | Versionado y revisión humana por diff; commits pequeños con motivo |

## 4. Qué aportó cada herramienta (con evidencia)

- **TDD con pytest**: el ciclo rojo→verde detectó el contrato correcto antes de implementar (ImportError deliberado primero, suite final `49 passed`). Sin "reglas duplicadas": la única función de superposición se testea en un solo módulo.
- **El humo del entry point real** (exigible a cualquier binario): detectó lo que la suite no podía ver — `No module named reservas` con los tests en verde. Documentado en `docs/evidence/leccion-paquete-instalable.md`.
- **SQLite**: el conteo directo `SELECT COUNT(*)` como tercera vía de verificación (app, tests y SQL coinciden) en el procedimiento de persistencia.
- **Git como evidencia**: la historia separa spec, decisiones, tests e implementación en commits pequeños vinculados a tareas.

## 5. Qué falló o sorprendió (fallos reales, no pulidos)

1. **"Testing no es entrega"**: 49 tests en verde + programa que no arrancaba. La causa: el src-layout exige instalar el paquete; la inyección de `sys.path` en `conftest.py` disfrazaba el problema en el entorno de pruebas. Lección registrada y convertida en §4 de `AGENTS.md` + `pip install -e .`.
2. **Intérprete global vs venv**: `python -m reservas` resolvió el Python global sin el paquete. El comando correcto siempre es el del venv (o activarlo).
3. **Encoding en salida redirigida**: por pipe en Windows los acentos se ven alterados (cp1252 vs UTF-8); en consola interactiva renderiza bien. No afectó al producto, sí a la interpretación de evidencia capturada.
4. **Nombres de archivo con em dash (—)**: los archivos de evidencia humana en `op-interno/` llevan guión largo; buscar el nombre con guion simple falló. Se resolvió inspeccionando el nombre byte a byte.
5. **La herramienta falla de forma intermitente, no determinista**: el agente introduce vocabulario ajeno o corrupto en textos largos, varias veces por sesión (trazable en el log de verificación y en esta misma sesión). Control adoptado: releer el propio diff/artefacto tras escribir — detectó y corrigió todos los casos registrados. Es la razón por la que cada documento de este repo fue releído tras editarse.
6. **Memoria externa no sustituye evidencia**: Engram a veces no registró sesiones (fallo transitorio); el proyecto no dependió de ella para nada verificable — la evidencia formal se versiona en el repo. La herramienta de memoria se trata como caché, no como fuente de verdad.

## 6. Conclusión

El conjunto elegido (harness OpenCode + modelo de acceso libre + pytest + sqlite3 + argparse + git) cubrió el desafío sin dependencias de runtime ni servicios pagos. Los aciertos decisivos fueron el flujo spec-primero, el TDD con reloj inyectado y la revisión humana por diff; los tropiezos reales (paquete no instalado, intérprete global, corrupción de textos) quedaron como evidencia y como reglas escritas del repositorio.
