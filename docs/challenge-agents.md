# Desarrollo de un sistema de reservas con agentes

**Modalidad:** individual · **Entrega:** una única entrega de repositorio

Construir una solución local pequeña y verificable a partir de una necesidad de negocio, utilizando un agente de programación. La entrega debe mostrar la especificación, la preparación del agente, lo delegado y la verificación humana de los resultados.

---

## 1. Contexto ficticio

La coordinación de un laboratorio registra pedidos en mensajes y una planilla. A veces se confirma la misma unidad para horarios superpuestos; otras veces una cancelación sigue bloqueando el horario. Necesita consultar disponibilidad, reservar y cancelar sin perder el historial. El inventario ya está definido; cada ID identifica una unidad física distinta.

| ID de unidad | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

## 2. Alcance y reglas mínimas

- Leer el inventario precargado y consultar disponibilidad por unidad e intervalo. No se requiere administrar el inventario.
- Crear una reserva identificable con unidad, solicitante ficticio no vacío, inicio y fin. Una unidad por reserva es suficiente.
- Cancelar conservando identificador y datos, y liberar el intervalo.
- Persistir reservas y estados para recuperarlos al reiniciar la aplicación.

### Reglas de negocio

- Una reserva **activa** ocupa el intervalo; una **cancelada** no bloquea disponibilidad.
- Validar:
  - unidad conocida;
  - solicitante no vacío ni compuesto solo por espacios;
  - fechas y horas válidas;
  - inicio estrictamente anterior al fin.
- Rechazar superposiciones de reservas activas de la misma unidad.
- Permitir límites consecutivos.
- Permitir reservas simultáneas de unidades distintas.
- La consulta de disponibilidad debe usar estas mismas reglas.

### Ejemplo

Con MIC-01 reservado de 10:00 a 11:00:

- Rechazar 10:30 a 11:30.
- Permitir 11:00 a 12:00.
- MIC-02 puede reservarse de 10:00 a 11:00 aunque MIC-01 esté ocupado.

---

## 3. Preparación del agente y verificación

### 3.1 Trabajar con un entorno existente

Usar un agente de programación que actúe sobre el repositorio con herramientas reales; no basta copiar una respuesta de chat. El *harness* es el entorno que coordina modelo, herramientas, contexto y ejecución: se utiliza uno existente, no se construye uno. Un agente basta; no se exige MCP, Linear, memoria externa, multiagente ni servicios pagos.

Documentar con evidencia concreta:

- **Entorno, versión e identificador del modelo** cuando estén disponibles, su función y el motivo de la elección. Indicar si un dato no es visible, sin inventarlo.
- **Instrucciones y configuraciones realmente usadas**, saneadas; contexto suministrado y qué se excluyó. Si la configuración es externa al repositorio, incluir un extracto y cómo se aplicó.
- **Herramientas y acciones permitidas**, controles y aprobaciones humanas previstos y aplicados. Explicar qué cambios o resultados se revisaron antes de aceptarlos.
- **Al menos una adaptación específica comprobable**, como una instrucción sobre turnos consecutivos o un procedimiento de persistencia, con evidencia de uso. Conservar progreso y decisiones en un archivo versionado; no se exige reiniciar sesiones ni provocar fallas.

### 3.2 Decisiones y límites técnicos

- Elegir lenguaje, dependencias, almacenamiento e interfaz; consola o API local son suficientes, sin interfaz gráfica obligatoria.
- La aplicación y sus pruebas deben reproducirse sin la cuenta de modelo del autor.
- Documentar zona horaria, formato de fechas, tratamiento de fechas pasadas y límites de duración o anticipación, si se aplican.
- Resolver lo no especificado con supuestos razonables y coherentes, sin depender de consultas posteriores ni de requisitos ocultos.

**Fuera de alcance:** autenticación y roles reales, notificaciones, pagos, integraciones externas, despliegue obligatorio, frente gráfico complejo, concurrencia distribuida y escalabilidad de producción.

### 3.3 Verificaciones requeridas

Incluir y ejecutar **pruebas automáticas** de:

1. creación válida;
2. rechazo de superposición;
3. límites consecutivos;
4. unidades distintas simultáneas;
5. entradas inválidas;
6. cancelación que conserva el registro y libera el horario.

Comprobar **persistencia** de reservas activas y canceladas tras detener y reiniciar sin borrar datos. Esta verificación puede ser automática o un procedimiento manual reproducible con resultados esperados y observados.

Además:

- Distinguir lo informado por el agente de las comprobaciones realmente ejecutadas.
- Registrar comando o procedimiento, versión y resultado, incluidos fallos o pasos no ejecutados.
- Las capturas no reemplazan pruebas ni resultados reproducibles.
- Si el acceso al agente limita el trabajo, declarar lo completado y bloqueado con evidencia, sin inventar registros ni asumir una exención de evaluación.

---

## 4. Repositorio y criterios de evaluación

### 4.1 Contenido a entregar

Código, pruebas automáticas, inventario inicial, dependencias y archivos de bloqueo cuando correspondan.

### 4.2 El README como punto de entrada

Organizar el README en **cuatro secciones**; puede enlazar otros archivos:

1. **Especificación breve:** problema, alcance, requisitos verificables, reglas, supuestos y criterios de aceptación. La versión inicial y los cambios significativos, con sus motivos, deben ser recuperables en Git; no hay un mínimo de commits.
2. **Solución:** estructura, decisiones técnicas, requisitos previos y versiones; instalación, carga inicial y reinicio de datos, comandos de aplicación y pruebas, ejemplo de entrada y salida. Indicar dónde persisten los datos, advertir si el reinicio de datos borra reservas y declarar pendientes y limitaciones.
3. **Preparación del agente:** entorno y modelo, instrucciones, contexto, permisos, adaptación y retención del progreso, con enlaces a la evidencia de uso real.
4. **Registro de decisiones y delegación:** decisiones significativas, motivos, alternativas cuando exista una disyuntiva y consecuencias; incluir los tres episodios descritos a continuación.

### 4.3 Tres episodios reales de delegación

Para cada episodio, registrar, en este orden:

1. Objetivo y requisito
2. → Contexto suministrado y extracto de instrucción
3. → Acción o resultado del agente
4. → Decisión humana de aceptar, corregir o rechazar, con motivo
5. → Enlace a archivo, commit, prueba o resultado verificable

Reglas:

- Vincular la evidencia con la versión entregada.
- Registrar correcciones solo si ocurrieron; no inventar fallas ni adjuntar transcripciones completas.

### 4.4 Restricciones de contenido

- No incluir secretos, tokens, credenciales, conversaciones privadas completas ni datos reales de estudiantes.
- Usar solicitantes ficticios.
- El repositorio debe explicar por sí solo qué se construyó y cómo se comprobó.

### 4.5 Rúbrica

| Dimensión | Peso | Qué se observa |
|---|---|---|
| Especificación | 25 % | Requisitos y aceptación verificables; reglas y supuestos coherentes; evolución recuperable. |
| Preparación y uso del agente | 25 % | Instrucciones, contexto, permisos y adaptación específica con evidencia de uso real. |
| Funcionamiento y pruebas | 30 % | Alcance y reglas operativos; pruebas centrales, persistencia y ejecución reproducible. |
| Trazabilidad y decisiones | 20 % | Tres episodios que conectan requisitos, resultados, revisión humana y evidencia. |

Se evalúa evidencia del repositorio, no solo afirmaciones del README. Extras, herramientas pagas, cantidad de agentes o commits y estética no dan puntos por sí mismos.

---

## 5. Entrega

- Enviar el enlace al repositorio a **dgaifirst@gmail.com** con el asunto exacto **«Challenge IA»**.
- Comprobar que el repositorio sea accesible y revisar los permisos.
- Se recomienda identificar rama y commit.
- No se requieren entregas intermedias, defensa oral, video ni encuentros posteriores.