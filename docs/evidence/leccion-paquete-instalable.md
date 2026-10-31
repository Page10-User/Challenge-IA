# Lección: un `src`-layout sin instalar no es un programa

Caso real del proyecto (30-10-2026), documentado con enfoque didáctico y
académico: qué falló, por qué falló, cómo se resolvió y qué enseñanza
deja. Todos los comandos citados se ejecutaron realmente; los fallos se
transcriben tal cual ocurrieron (ver `verification-log.md`).

## 1. Contexto

Durante la Fase 4c se implementó la interfaz de consola (`cli.py`) con su
suite de pruebas (`tests/test_cli.py`). El ciclo TDD se completó en verde:
**49 pruebas pasando**. Aparentemente, la tarea estaba terminada.

## 2. El error

La verificación del punto de entrada real —el programa tal como lo usará
un usuario— mostró lo contrario:

```text
PS .\.venv\Scripts\python.exe -m reservas
C:\...\.venv\Scripts\python.exe: No module named reservas
```

La suite estaba en verde y, sin embargo, **la aplicación no arrancaba**.
Ningún test lo había detectado.

## 3. Diagnóstico

Tres causas encadenadas:

1. **El proyecto usa `src`-layout**: el paquete vive en `src/reservas/`,
   separado de la raíz del repositorio. Python no busca paquetes ahí por
   defecto: solo mira los directorios listados en `sys.path`.
2. **La suite "pasaba" por una inyección de tests**: `tests/conftest.py`
   agrega manualmente `src/` a `sys.path` para que `import reservas`
   funcione *dentro de pytest*. Es una cinta de seguridad del entorno de
   pruebas, no una solución del programa: funcionaba en los tests y en
   ningún otro lado.
3. Además, al hacer el humo se ejecutó `python -m reservas` sin activar
   el entorno virtual: `python` resolvió el intérprete **global** del
   sistema, que no tiene el paquete. Segunda lección: el programa se
   ejecuta con el `python` del venv (o activando el venv antes).

## 4. Solución fundamentada

La práctica estándar de la industria para `src`-layout es hacerlo
**instalable** y luego instalarlo en modo editable:

- Se agregó `pyproject.toml` (configuración mínima de empaquetado con
  `setuptools`, cero dependencias nuevas) que declara dónde viven los
  paquetes (`src`).
- Se ejecutó una única vez: `pip install -e .` (instalación *editable*).

¿Por qué editable y no una instalación normal? La `-e` (editable) no
copia el código al entorno: crea un enlace que apunta al código fuente
real del repositorio. Así se edita el código y los cambios se reflejan
sin reinstalar, y al mismo tiempo `python -m reservas` funciona porque el
paquete quedó formalmente registrado en el venv.

Con esto, el comando documentado en `AGENTS.md` §4 es exactamente el que
funciona: `python -m reservas <comando>`.

## 5. Verificación posterior

```text
PS .\.venv\Scripts\python.exe -m reservas
Bienvenido al sistema de reservas de equipos de laboratorio.
Comandos disponibles: disponibilidad, reservar, cancelar, listar
```

Smoke completo contra la base de datos real (`data/reservas.db`): dos
reservas registradas (id 1 y 2), disponibilidad ocupada/libre según la
convención de intervalos, cancelación conservando el historial, y `listar`
mostrando ambos estados (`[cancelada]` y `[activa]`). La suite siguió en
verde: **49 passed**.

## 6. Reflexión didáctica

- **Testing no es entrega.** Un 100% de tests en verde puede convivir con
  un programa que no arranca: la suite prueba *lógica*, no *despliegue*.
  El "hecho" (AGENTS.md §12) incluye poder ejecutarlo como usuario real.
- **La cinta de seguridad disfraza.** Las soluciones que solo viven en el
  entorno de pruebas (aquí, la inyección de `sys.path` en `conftest.py`)
  deben ser tratadas como auxiliares, nunca como evidencia de que la app
  corre.
- **El error es evidencia valiosa.** El registro del fallo en el log de
  verificación (con su salida real) es material de evaluación del
  challenge: muestra cómo se detectó, se diagnosticó y se resolvió.
- **Colocación de código.** Si el proyecto no necesita empaquetarse, la
  estructura plana también es válida. Con `src`-layout, en cambio, el
  paso de instalación no es burocracia: es la mitad del diseño.

## 7. Nota adicional: encoding en salida redirigida

Durante la verificación se observó que, al capturar la salida en una
tubería (pipe), los acentos se ven alterados; en la consola interactiva
el texto renderiza correctamente. Causa: cuando la salida no va a la
consola, Python codifica con la página de código predeterminada del
sistema para texto redirigido (en Windows, habitualmente `cp1252`), y el
receptor que decodifica como UTF-8 interpreta mal esos bytes. No
requería corrección para el usuario de consola, pero es un caso de
enseñanza sobre encoding: el mismo texto falló o funcionó según el
canal de salida, igual que el paquete funcionaba según el intérprete.
