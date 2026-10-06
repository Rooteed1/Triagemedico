# Bitácora integral del proyecto TriageAI

**Proyecto:** Prototipo web de triaje médico con lógica difusa  
**Fecha de registro:** 4 de octubre de 2026  
**Propósito:** Reunir en un solo documento las solicitudes relevantes del usuario, los problemas comunicados y la ayuda/cambios realizados durante el proyecto.

> Los PRD extensos, capturas y mensajes de error se resumen fielmente para que el registro sea legible. Los rangos clínicos compartidos por el usuario se conservan explícitamente. Esta bitácora no implica validación clínica del sistema.

## Registro cronológico de solicitudes

### Definición del proyecto y plataforma

1. **PRD inicial: sistema neuro-difuso de triaje.** Crear un MVP para calcular un Índice de Prioridad de Atención a partir de temperatura, frecuencia cardíaca y dolor; mantener reglas explicables y auditables, probarlo en un entorno controlado y considerar datos históricos como evolución futura. El PRD inicial planteó rangos de entrada, conjuntos/reglas difusas, niveles de prioridad y validación con casos de prueba.
2. **PRD de TriageAI como aplicación web.** Mantener el proyecto en Python con un `app.py`; usar Streamlit para la interfaz, scikit-fuzzy para inferencia, NumPy para universos numéricos y Matplotlib para gráficas. Se solicitaron entradas interactivas, cálculo de prioridad, explicación visual y una aplicación orientada al personal de salud.
3. **Consulta:** cómo llevar el sistema a la web.
4. **Consulta:** en qué plataforma web publicarlo.
5. **Consulta:** posibilidad de distribuirlo como `.exe` con PyInstaller o Nuitka y guardar la base de datos localmente dentro de la aplicación.
6. **Consulta:** recomendación para un `.exe` conectado a una base de datos en la nube.
7. **Decisión de alcance:** mantenerlo en el navegador y comparar opciones gratuitas de despliegue para un proyecto escolar.
8. **Decisión de plataforma y datos:** elegir la primera opción de despliegue recomendada y preguntar si se podrían registrar datos para obtener un conjunto de datos.

### Construcción y resolución del entorno

9. **Implementación:** empezar a crear toda la estructura y el código del sistema.
10. **Revisión y puesta en marcha:** revisar el código y explicar qué instalar, dónde instalarlo y qué comandos usar para resolver errores.
11. **Configuración de PowerShell:** se compartieron comandos para permitir la activación del entorno virtual durante la sesión y activar `.venv`.
12. **Diagnóstico con adjuntos:** se compartió texto/captura de terminal para localizar un error.
13. **Error de dependencia:** se reportó `ModuleNotFoundError: No module named 'scipy'` al importar scikit-fuzzy.
14. **Documentación breve:** crear un archivo Markdown corto que registre lo solicitado y la ayuda recibida.
15. **Nuevos adjuntos de error:** se compartieron textos/capturas adicionales para revisar el estado del código.
16. **Señalamiento de error:** se indicó que uno de los adjuntos mostraba un error.
17. **Error de puerto:** se compartió que Streamlit no podía usar el puerto 8503 porque ya estaba ocupado.
18. **Confirmación breve:** se envió el mensaje “ok,emjro”; no especificaba un cambio técnico concreto.
19. **Error de dependencia:** se reportó `ModuleNotFoundError: No module named 'networkx'` al importar el módulo de control de scikit-fuzzy.

### Interfaz, entradas y lógica clínica

20. **Rediseño visual:** mejorar o rehacer la interfaz para que fuera más minimalista, ordenada, profesional y con mejor acabado.
21. **Valores iniciales realistas:** establecer valores predeterminados de temperatura, pulso y dolor basados en la información clínica que proporcionó el usuario.
22. **Aprobación:** implementar esos valores iniciales.
23. **Actualización de la primera bitácora:** añadir a `bitacora.md` lo solicitado en los prompts recientes.
24. **Captura flexible de datos:** añadir controles para escribir las mediciones manualmente y un selector desplegable por cada dato, de modo que se pudiera seleccionar un valor o escribirlo.
25. **Simplificación y mayor rango de entrada:** quitar el perfil clínico y ampliar las cantidades disponibles en las entradas.
26. **Error de ejecución:** se reportó `KeyError: 'urgencia'` en `calculate_triage`, al intentar leer esa clave de la salida del sistema difuso.
27. **Confirmación “haz esto”:** aceptar la propuesta de organizar las mediciones en tarjetas individuales con aspecto de panel clínico.
28. **Corrección de clasificación con rangos específicos:** se indicó que `33 °C`, `59 ppm` y dolor `5` no se estaban analizando correctamente. Se pidió actualizar los rangos y generar un análisis diferenciado cuando cualquiera de las tres mediciones fuera anormal.
29. **Registro de la corrección:** actualizar `bitacora.md` con los rangos, el caso corregido y los cambios recientes.
30. **Esta solicitud:** crear `bitacora1.md` con todas las solicitudes del proyecto y sus prompts relevantes.

## Criterios clínicos compartidos por el usuario

Estos rangos se incorporaron como referencias orientativas para **adultos en reposo**. No representan por sí solos un protocolo clínico validado.

### Temperatura

- **Menos de 35.0 °C:** hipotermia moderada/severa; el usuario la señaló como urgencia y pidió valoración médica inmediata.
- **35.0–35.9 °C:** hipotermia leve; vigilancia.
- **36.0–37.4 °C:** rango normal/estable.
- **37.5–37.9 °C:** febrícula; vigilancia.
- **38.0–39.9 °C:** fiebre moderada; valorar evolución y síntomas.
- **40.0 °C o más:** temperatura muy alta; valoración inmediata.
- El usuario especificó que en menores de 3 meses una temperatura de 38 °C o más requiere valoración urgente; el rango de pulso adulto no debe aplicarse a menores.

### Pulsaciones por minuto

- **Menos de 40 ppm o más de 130 ppm:** posible bradicardia/taquicardia severa en reposo; valoración inmediata, especialmente si hay síntomas.
- **40–59 ppm o 101–130 ppm:** pulso bajo/elevado que requiere evaluación y vigilancia; el usuario señaló que un pulso bajo puede ser normal en atletas.
- **60–100 ppm:** rango normal de referencia para adultos en reposo.

### Dolor

Se conserva la escala de **0 a 10** ya definida para el MVP. La aplicación diferencia dolor leve (0–3), moderado (4–6) e intenso (7–10); el dolor se informa como hallazgo y no como diagnóstico.

## Ayuda y cambios registrados

- Se construyó un MVP local con Python y Streamlit, con lógica difusa mediante scikit-fuzzy, NumPy y Matplotlib.
- Se prepararon dependencias, instrucciones de ejecución, variables opcionales de Supabase e historial local CSV; la conexión a Supabase es opcional.
- Se orientó la instalación y activación del entorno virtual en Windows PowerShell, incluyendo la resolución de dependencias faltantes `scipy` y `networkx`.
- Se abordó el conflicto de puertos de Streamlit ejecutándolo en un puerto alternativo cuando el solicitado estaba ocupado.
- Se mejoró la presentación visual y se organizaron las mediciones de temperatura, pulso y dolor en tarjetas en el área principal. El selector de perfiles clínicos fue retirado; la barra lateral mantiene el identificador del paciente y la opción de guardar.
- Se mantuvo la entrada numérica manual: temperatura de 30 a 45 °C, pulso de 30 a 220 ppm y dolor de 0 a 10.
- Se corrigió la lectura de una salida difusa inexistente para evitar el `KeyError: 'urgencia'`.
- Se amplió el universo del sistema difuso y se añadieron comprobaciones clínicas explícitas. La puntuación difusa complementa la evaluación; no puede bajar el nivel mínimo asignado a un hallazgo grave. La salida resume por separado temperatura, pulso y dolor, y eleva la estimación cuando coinciden varias alteraciones moderadas.

## Verificaciones registradas

- El caso que reportó el usuario, **33 °C, 59 ppm y dolor 5/10**, antes devolvía 0% y prioridad baja. Tras el cambio devuelve **85% y prioridad alta**, e identifica hipotermia, pulso bajo y dolor moderado.
- Se probaron rangos normales, límites bajos y altos, fiebre, dolor intenso y valores extremos de los campos.
- `python -m py_compile app.py` terminó sin errores; la comprobación dirigida del caso pasó; no se encontraron diagnósticos en `app.py`; el servidor local respondió HTTP 200 en el puerto 8510.

## Estado y pendientes

- **MVP local:** implementado y ejecutable con Streamlit.
- **Registro de datos:** historial local disponible; Supabase es opcional y requiere configuración.
- **Despliegue público:** se conversó sobre opciones gratuitas, pero el despliegue de producción no queda registrado como completado.
- **Alcance médico:** herramienta de demostración/apoyo orientativo. No diagnostica ni sustituye una valoración clínica; los rangos requieren revisión profesional antes de cualquier uso asistencial.
- **Aprendizaje con datos históricos y validación extensa:** aparecieron como objetivos/ideas del PRD; no se registra como implementado entrenamiento automático ni una validación clínica formal de una cohorte de casos.
