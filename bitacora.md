# Bitácora del Proyecto TriageAI

## Solicitud inicial
Se pidió crear un prototipo web de triaje médico con lógica difusa, usando Python, con una interfaz amigable para ingresar:
- temperatura
- frecuencia cardíaca
- nivel de dolor

Además, se planteó la posibilidad de desplegar la aplicación en navegador, con registro de datos y opción de almacenamiento gratuito.

## Ayuda entregada
Se apoyó en la creación de la estructura base del proyecto, incluyendo:
- archivo principal `app.py`
- requisitos de instalación en `requirements.txt`
- configuración de entorno y variables de ejemplo
- documentación básica en `README.md`
- lógica de cálculo de prioridad con `scikit-fuzzy`
- interfaz de usuario con `Streamlit`
- historial local para guardar resultados
- soporte para conexión opcional a Supabase

## Configuración y ejecución
Se explicó y validó el proceso para:
1. crear un entorno virtual en Python
2. instalar dependencias
3. activar el entorno en Windows PowerShell
4. ejecutar la app con Streamlit
5. resolver errores comunes de módulos faltantes como `scipy`

## Resultado
El proyecto quedó en una versión funcional de MVP para correr localmente en navegador con Streamlit, lista para continuar con mejoras como:
- despliegue gratuito en Streamlit Cloud
- almacenamiento en Supabase
- mejora visual de la interfaz
- registro de pacientes y historial más completo

## Ajustes posteriores: rediseño visual y valores clínicos reales
Durante la fase de refinamiento del producto se realizaron cambios importantes en la experiencia visual y en la lógica de ejemplo del sistema.

### 1) Rediseño de interfaz
Se mejoró la apariencia visual de la aplicación para que se vea más limpia, moderna y profesional, con enfoque minimalista. Los cambios incluyen:
- fondo claro con gradiente sutil
- cards con bordes suaves y sombras discretas
- mejor jerarquía visual para títulos, métricas y resultados
- badges de prioridad con colores diferenciados para urgencia baja, media y alta
- distribución más ordenada de los datos del paciente y del resumen clínico

Esto permitió que la app se percibiera como un prototipo más cuidado, más cercano a una herramienta usable para demostración o presentación.

### 2) Valores iniciales reales y basados en clínica
Se ajustaron los valores predeterminados del sistema para que no partieran de un caso artificial. Se definieron rangos clínicamente coherentes para:
- temperatura corporal
- frecuencia cardíaca
- nivel de dolor

Se incorporó una base de referencia realista para un paciente estable, con ejemplos de:
- fiebre leve
- fiebre moderada
- hipotermia leve
- hipotermia severa
- urgencia alta

Los valores usados quedaron alineados a rangos reales del cuerpo humano, por ejemplo:
- 36.0 °C a 37.4 °C = rango normal
- 37.5 °C a 37.9 °C = febrícula
- 38.0 °C a 39.9 °C = fiebre moderada
- 40.0 °C o más = urgencia médica alta
- 35.0 °C o menos = riesgo de hipotermia

### 3) Perfiles clínicos predefinidos
Se añadió un selector de perfiles dentro de la barra lateral para facilitar pruebas con casos reales y representativos, sin necesidad de introducir valores manualmente cada vez. Esto ayuda a evaluar mejor cómo responde la lógica difusa ante distintos escenarios clínicos.

## Estado actual
La aplicación queda en una versión funcional, visualmente mejorada y con valores base más realistas. Se mantiene lista para:
- demostración en navegador
- ajustes adicionales de UX
- conexión con Supabase o almacenamiento persistente
- despliegue web posterior

## Actualización: análisis clínico de signos vitales (2026-10-04)

Se solicitó que cada medición se analizara con rangos explícitos para adultos en reposo y que una medición anormal no se presentara como normal por falta de activación de una regla difusa.

### Rangos incorporados

- **Temperatura:** menos de 35.0 °C se señala como hipotermia que requiere valoración inmediata; 35.0–35.9 °C como temperatura baja que requiere vigilancia; 36.0–37.4 °C como rango normal; 37.5–37.9 °C como febrícula; 38.0–39.9 °C como fiebre moderada; 40.0 °C o más como señal para valoración inmediata.
- **Pulso en adultos en reposo:** menos de 40 ppm o más de 130 ppm se señala para valoración inmediata; 40–59 ppm y 101–130 ppm requieren evaluación y vigilancia; 60–100 ppm se considera el rango normal de referencia.
- **Dolor (escala 0–10):** 0–3 leve; 4–6 moderado; 7–10 intenso y requiere valoración clínica.

La prioridad combina la salida difusa con un nivel mínimo de urgencia para los hallazgos clínicos; si coinciden varias alteraciones moderadas, se eleva la estimación. Se amplió el universo de entrada del motor para cubrir los rangos disponibles en la interfaz. El análisis se identifica como orientativo y no sustituye la valoración de personal de salud. La interfaz advierte que los rangos de pulso son para adultos en reposo y que una temperatura de 38 °C o más en menores de 3 meses requiere valoración urgente.

### Corrección y verificación

Se reprodujo el caso **33 °C, 59 ppm y dolor 5/10**, que antes devolvía 0% y prioridad baja porque la temperatura quedaba fuera del universo difuso y no había una regla clínica independiente para esa hipotermia. Tras el ajuste, el caso devuelve **85% y prioridad alta**, y el resumen identifica hipotermia, pulso bajo y dolor moderado.

También se comprobaron valores normales, los límites de temperatura y pulso, fiebre, dolor intenso y los máximos disponibles en los campos. `python -m py_compile app.py` finalizó sin errores; la comprobación dirigida del caso pasó; el archivo no presenta diagnósticos y el servidor local respondió HTTP 200.

### Ajuste de interfaz

Las entradas de temperatura, frecuencia cardíaca y dolor se muestran en tarjetas separadas en el área principal. Se retiró el selector de perfiles clínicos; la barra lateral conserva el identificador y la opción de guardar el registro.
