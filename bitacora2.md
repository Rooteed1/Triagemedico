# Bitácora de prompts de la sesión

**Proyecto:** TriageAI  
**Fecha:** 12 de octubre de 2026  
**Propósito:** Conservar en orden los mensajes y solicitudes enviados por el
usuario durante esta sesión, relativos a la integración de Supabase, autenticación
y registro de atenciones.

> Se transcriben los mensajes del usuario tal como fueron recibidos, incluidos
> errores tipográficos. Los adjuntos se anotan aparte cuando acompañaron una
> solicitud. No se incluyen las respuestas del asistente.

## Prompts en orden cronológico

### 1. Solicitud de integrar Supabase y aclarar requisitos

> es hoara de agregar la ase de datos en supa base usando potsgrest ( la base
> dde datos contara con un registro y un guradado de pacientes atendidos [se
> tiene ya en el programa esa funcion de agregar o poner nombre al paciente y
> un guarado de registro de toma de medidad]) ayudame o haz pregunstas de como
> implemetar bien la base datos y que sea funcional y que sea usada bien en la
> caraterisiticas de la app

### 2. Aclaración sobre identificación, historial, despliegue y almacenamiento

> si, el nombre sera suficiente, si, si tiene accedi al historial pero no a
> desacargar ( eso solo aplica al login ) se usa en telefonos en su version web
> ( ya esta alojada en streamlink, no, solo disponible con supabase, no, solo
> que muestre el historial normal )

### 3. Aclaración sobre acceso al historial

> solo usuarios con sesion iniciada y cada sesion debe de mostrar el historial
> que haya realizado ese usuario

### 4. Solicitud de documentar los requisitos en Markdown

> no hay codigo de login ( esa debes de crearla aprate y poner en la pantalla
> un icono de iniciar sescion y de registro ) la app debe de funcioar normal aun
> sin login lo unico de no gusarda si no hay sesion iniciada son los egistros
> ( unas vez iniciado si guarda) pero las funciones de medicion y de analisis
> deben de estar tanto para la funcion sin sesion iniciada como sesion iniciada

### 5. Solicitud de implementar el código

> ahora realizalo ya el codigo

**Adjunto incluido en el mensaje:** `REQUISITOS_SUPABASE_Y_AUTENTICACION.md`.

### 6. Solicitud de crear esta bitácora

> ahora crea un archivo ( bitacora2.md) en cual registres todo los promps que
> se usaron en esta sesion

## Requisitos que quedaron expresados en la sesión

- Usar Supabase/PostgreSQL para guardar las atenciones.
- Mantener el nombre del paciente como dato disponible en la aplicación.
- Permitir varias atenciones y mostrar el historial por cuenta autenticada.
- Restringir el historial a usuarios con sesión; cada usuario solo consulta sus
  propios registros.
- Añadir registro e inicio de sesión a la interfaz.
- Permitir mediciones y análisis tanto con sesión como sin ella.
- No guardar registros cuando no hay sesión.
- No ofrecer descarga del historial en el alcance solicitado.
- Mantener la experiencia de la versión web utilizable desde teléfonos.
- Usar Supabase como persistencia; no recurrir a un guardado local como
  alternativa silenciosa.
