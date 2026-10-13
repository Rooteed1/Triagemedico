 # Requisitos de Supabase, autenticación e historial

## Objetivo

Definir cómo integrar Supabase y PostgreSQL con TriageAI para guardar las
atenciones realizadas y ofrecer un historial privado por usuario, sin impedir
que la aplicación se use para medir y analizar sin iniciar sesión.

## Comportamiento solicitado

### Uso sin iniciar sesión

- La aplicación debe seguir disponible sin cuenta y sin iniciar sesión.
- Se deben poder ingresar las mediciones, calcular el nivel de urgencia y
  consultar el análisis y sus visualizaciones normalmente.
- No se deben guardar las mediciones ni crear registros cuando no exista una
  sesión autenticada.
- No se debe mostrar el historial de atenciones a usuarios sin sesión.
- No se debe usar un CSV local como alternativa de guardado. Supabase es el
  único almacenamiento persistente de los registros.

### Uso con sesión iniciada

- La pantalla debe ofrecer opciones visibles para **iniciar sesión** y
  **registrarse**, representadas con iconos y etiquetas accesibles.
- Una vez autenticado, el usuario puede guardar cada evaluación realizada.
- El usuario puede consultar el historial de las atenciones que guardó con su
  propia cuenta.
- Un usuario nunca debe poder consultar los registros de otra cuenta, aunque
  intente cambiar parámetros o llamar directamente a la base de datos.
- El historial se presenta en la aplicación como una lista o tabla normal. La
  descarga o exportación del historial no forma parte de este alcance.
- Debe haber una forma visible de cerrar sesión. Tras cerrarla, se deben ocultar
  las opciones de guardado e historial protegido.

### Pantalla y dispositivos

- La aplicación continúa siendo web y debe poder utilizarse desde teléfonos.
- Los iconos y controles de autenticación deben adaptarse a la pantalla móvil,
  ser fáciles de pulsar y tener texto accesible (por ejemplo, etiquetas o
  tooltips).
- La autenticación no debe bloquear ni alterar el flujo de medición y análisis
  que funciona sin sesión.

## Datos que se guardan

Cada evaluación guardada representa una atención y debe incluir, como mínimo:

- Identificador único del registro.
- Identificador del usuario autenticado propietario del registro.
- Nombre del paciente introducido en la aplicación.
- Fecha y hora de la atención.
- Temperatura.
- Frecuencia cardíaca.
- Nivel de dolor.
- Porcentaje de urgencia calculado.
- Nivel o etiqueta de prioridad resultante.
- Resumen o hallazgos del análisis, cuando estén disponibles.

El nombre es el dato identificador del paciente solicitado para la interfaz; no
se requieren otros datos personales en este alcance. Cada nueva evaluación
guardada genera una nueva atención, incluso si corresponde al mismo nombre.
Como los nombres pueden coincidir, la propiedad y separación de los historiales
se basan en el usuario autenticado y el identificador único del registro, no en
el nombre del paciente.

## Diseño inicial de almacenamiento

### Tabla `triage_records`

Para el alcance actual, se puede conservar una tabla de atenciones con una fila
por evaluación. No es necesario crear una tabla separada de pacientes para
guardar y consultar el historial solicitado.

Columnas recomendadas:

| Columna | Tipo sugerido | Uso |
| --- | --- | --- |
| `id` | `uuid` | Clave primaria generada por PostgreSQL |
| `user_id` | `uuid` | Propietario; referencia al usuario de Supabase Auth |
| `patient_name` | `text` | Nombre mostrado para la atención |
| `created_at` | `timestamptz` | Fecha y hora generada en el servidor |
| `temperature` | `numeric` | Temperatura ingresada |
| `heart_rate` | `integer` | Frecuencia cardíaca ingresada |
| `pain` | `integer` | Nivel de dolor ingresado |
| `urgency_score` | `numeric` | Porcentaje de urgencia calculado |
| `priority_label` | `text` | Nivel/etiqueta de prioridad |
| `summary` | `text` | Resumen del análisis, si se persiste |

Los nombres de columnas deben alinearse con el código y las migraciones finales.
Los rangos de medición deben validarse en la aplicación y, cuando sea viable,
también mediante restricciones de base de datos.

## Autenticación y autorización

- Utilizar Supabase Auth para registro, inicio y cierre de sesión.
- Como método inicial se recomienda correo electrónico y contraseña. El método
  debe confirmarse al implementar; no se incluyen proveedores externos en este
  alcance.
- Mantener la sesión de forma compatible con el despliegue web y el uso en
  teléfonos.
- Obtener el `user_id` del usuario autenticado; no aceptar del formulario un
  `user_id` arbitrario como propietario del registro.
- Activar Row Level Security (RLS) en `triage_records`.
- Crear políticas que permitan a un usuario autenticado insertar y leer solo
  filas cuyo `user_id` sea igual a `auth.uid()`.
- No habilitar acceso anónimo a los registros.
- No incluir ni exponer la clave `service_role` en el código del navegador, en
  el repositorio ni en la interfaz. Usar únicamente credenciales apropiadas para
  el cliente junto con RLS.
- No dar permisos de actualización o borrado desde el cliente mientras esas
  funciones no sean parte del producto.

## Guardado e historial

- El guardado debe estar disponible únicamente tras iniciar sesión.
- Si una persona sin sesión intenta guardar, se debe explicar que necesita
  iniciar sesión; la medición y el análisis ya calculados deben seguir visibles.
- Al guardar, se deben enviar a Supabase el nombre, las mediciones y el
  resultado, vinculados a la cuenta autenticada.
- El historial debe consultar Supabase filtrando por el usuario actual. RLS debe
  reforzar esa separación aunque el cliente omita o manipule filtros.
- Ordenar el historial desde la atención más reciente y mostrar, como mínimo,
  fecha, paciente, mediciones y nivel de prioridad.
- Si Supabase no está configurado, no hay conexión o falla una operación, mostrar
  un error comprensible. No indicar que se guardó cuando no se confirmó y no
  guardar silenciosamente en CSV.
- Los errores de autenticación, guardado y consulta deben distinguirse para que
  el usuario sepa si debe iniciar sesión, reintentar o revisar la conexión.

## Criterios de aceptación

1. Un visitante sin sesión puede ingresar mediciones y ver el mismo cálculo,
   análisis y visualizaciones disponibles para un usuario autenticado.
2. La aplicación no crea registros persistentes mientras el visitante no haya
   iniciado sesión.
3. La interfaz muestra opciones de iniciar sesión y registrarse con iconos y
   etiquetas utilizables tanto en escritorio como en teléfono.
4. Una persona puede registrarse, iniciar sesión y cerrar sesión.
5. Un usuario autenticado puede guardar una atención con el nombre y las
   mediciones ingresadas y recibe confirmación solo si Supabase la guardó.
6. Después de iniciar sesión, el usuario ve sus propios registros guardados,
   incluidos registros anteriores de la misma cuenta.
7. Dos usuarios distintos no pueden ver los registros del otro.
8. Cerrar sesión oculta el historial y deshabilita el guardado, sin deshabilitar
   las mediciones ni el análisis.
9. Si Supabase falla, la app informa el problema, conserva el resultado visible
   de la medición y no crea un registro local como respaldo.
10. No se ofrece descarga ni exportación del historial en esta entrega.

## Fuera de alcance

- Descarga o exportación de historiales.
- Acceso administrativo o consulta de registros de otros usuarios.
- Identificación de pacientes por correo, documento u otro dato distinto del
  nombre mostrado.
- Borrado o edición de atenciones desde la interfaz.
- Respaldo local en CSV.
- Cambios al algoritmo de medición, cálculo o análisis clínico existente.

## Implementación

La aplicación incorpora el flujo descrito en `app.py`. Para habilitarlo en un
despliegue, configura `SUPABASE_URL` y `SUPABASE_ANON_KEY` y ejecuta
`supabase/triage_records.sql` en el SQL Editor de Supabase. No configures una
clave `service_role` o `sb_secret_` en la aplicación. Hasta completar esos pasos,
la medición y el análisis siguen disponibles, pero autenticación, guardado e
historial no estarán habilitados.


NOTA ( se encontro que el programa guarda registros de anteriores sesiones revias eso para que no pase o se muestren los de otros pacientes, si guarda que por cache de navigador esta bien pero solo debe de mostrar las acciones de la persona logueda o de la peronsa que hoz las solicitudes  )