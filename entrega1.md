# Documento del proyecto

## Entrega 1 · Prototipo funcional y repositorio

| Campo | Información |
|---|---|
| **Nombre del proyecto** | TriageAI: prototipo web de triaje médico con lógica difusa |
| **Equipo** | Pendiente de confirmar por el equipo |
| **Integrantes** | Pendiente de agregar nombres completos |
| **Rama de IA** | Inteligencia artificial computacional: lógica difusa (soft computing) |
| **Fecha** | 4 de octubre de 2026 |

## 1. Problemática a resolver

En los servicios de salud, el triaje ayuda a ordenar la atención según la condición inicial de cada paciente. La temperatura, el pulso y el dolor pueden variar gradualmente, por lo que una decisión basada en un único umbral rígido puede no reflejar por sí sola el nivel de riesgo. Una evaluación inicial consistente y comprensible puede apoyar la identificación de casos que necesitan atención prioritaria.

TriageAI es un prototipo académico que explora cómo presentar esa evaluación de forma transparente. Está dirigido a personal de salud y estudiantes que prueban un flujo de triaje; no sustituye el criterio profesional, un diagnóstico ni un protocolo clínico validado.

## 2. Descripción del proyecto

El programa es una aplicación web desarrollada en Python con Streamlit. Recibe temperatura corporal en °C, frecuencia cardíaca en pulsaciones por minuto y nivel de dolor de 0 a 10. Las mediciones se ingresan manualmente en controles numéricos. La interfaz muestra los campos en tarjetas separadas.

Con esas entradas, la aplicación combina lógica difusa y reglas explícitas para estimar un porcentaje de urgencia y una categoría de prioridad. Presenta un resumen que señala por separado los hallazgos de temperatura, pulso y dolor, y una gráfica de prioridad. Puede guardar registros en un historial CSV local; también incluye integración opcional con Supabase si se configura. El prototipo actual emplea reglas definidas explícitamente; no entrena automáticamente un modelo con los registros.

## 3. Rama de IA

**Rama asignada:** lógica difusa, dentro de la inteligencia artificial computacional o *soft computing*. El proyecto la denomina sistema neuro-difuso en sus requisitos iniciales; la versión implementada usa reglas difusas explícitas y no incorpora aprendizaje automático adaptativo.

**Justificación:** los signos y síntomas pueden ubicarse entre categorías como normal, elevado o crítico, en vez de cambiar de estado únicamente al cruzar un valor binario. La lógica difusa permite combinar esos grados mediante reglas que se pueden inspeccionar y explicar. Esto es adecuado para un prototipo donde se requiere mostrar por qué cada medición influye en la prioridad; los rangos utilizados son orientativos y deben ser revisados por profesionales antes de cualquier uso clínico.

## 4. Caso de uso

- **Usuario objetivo:** estudiante o personal de salud que realiza pruebas de evaluación inicial en adultos.
- **Situación en la que se usa el programa:** se ingresan temperatura, pulso en reposo y nivel de dolor durante una demostración o ejercicio académico de triaje.
- **Resultado esperado:** obtener una estimación de prioridad con explicación de cada hallazgo y una gráfica; si está habilitado el guardado, registrar la evaluación en el historial.

Los rangos de pulso están referidos a adultos en reposo. La aplicación informa que en menores de 3 meses una temperatura de 38 °C o más requiere valoración urgente; los rangos de este prototipo no deben extrapolarse a niños.

## 5. Requisitos

| Tipo | Requisito | Versión mínima / detalle |
|---|---|---|
| Sistema | Python | 3.10 o superior |
| Herramienta | pip | Incluido con Python; se recomienda actualizarlo antes de instalar |
| Interfaz web | Streamlit | 1.37.0 o superior |
| Cálculo numérico | NumPy | 1.26.0 o superior |
| Lógica difusa | scikit-fuzzy | 0.4.2 o superior |
| Dependencia científica | SciPy | 1.11.0 o superior |
| Dependencia de reglas/grafos | NetworkX | 3.2.0 o superior |
| Gráficas | Matplotlib | 3.8.0 o superior |
| Configuración | python-dotenv | 1.0.1 o superior |
| Datos | pandas | 2.1.0 o superior |
| Persistencia en nube | Supabase Python SDK | 2.0.0 o superior; opcional, requiere credenciales propias |
| Navegador | Chrome, Edge o Firefox actualizado | Necesario para abrir la interfaz local |

Las dependencias de Python se instalan desde `requirements.txt`. El historial local requiere permiso de escritura en la carpeta `data/`. Para guardar en Supabase también se requiere configurar `SUPABASE_URL` y `SUPABASE_KEY` en el entorno; este servicio no es necesario para ejecutar la versión local.

## 6. Instrucciones de instalación y ejecución

**Modalidad:** aplicación web local con Streamlit. No se ha generado un `.exe` ni se ha publicado una URL pública.

**Enlace del repositorio o de la aplicación:** el enlace remoto del repositorio y la URL pública están pendientes de proporcionar/publicar. Una vez ejecutada localmente, Streamlit muestra la dirección, normalmente `http://localhost:8501`.

### 6.1 Instalación

Para ejecutar la versión web publicada no se instala nada en el equipo del usuario. Para instalar y probar el prototipo localmente en Windows:

1. Instalar Python 3.10 o superior y abrir PowerShell en la carpeta del proyecto.
2. Crear y activar el entorno virtual:

   ```powershell
   python -m venv .venv
   . .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación, permitir scripts solo en la sesión actual y volver a activar:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   . .\.venv\Scripts\Activate.ps1
   ```

3. Instalar las dependencias:

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

### 6.2 Ejecución

1. En PowerShell, entrar a la carpeta del proyecto y activar el entorno virtual:

   ```powershell
   . .\.venv\Scripts\Activate.ps1
   ```

2. Ejecutar la aplicación:

   ```powershell
   python -m streamlit run app.py
   ```

3. Abrir en el navegador la dirección local indicada por Streamlit, normalmente `http://localhost:8501`. Si ese puerto está ocupado, iniciar con otro, por ejemplo:

   ```powershell
   python -m streamlit run app.py --server.port 8502
   ```

## Estado de la entrega

El prototipo local y su flujo principal están implementados. La compilación de `app.py` y pruebas dirigidas de clasificación se han ejecutado correctamente. El despliegue público, el enlace remoto del repositorio, los nombres del equipo y cualquier validación clínica formal quedan pendientes; deben completarse antes de presentar esos elementos como terminados.

## 7. Lista de verificación de la entrega

| Entregable | Ubicación (enlace o ruta) | Listo (Sí/No) |
|---|---|---|
| Código completo en repositorio | Código disponible localmente en [app.py](app.py); falta inicializar/publicar un repositorio Git | No |
| Archivo de dependencias | [requirements.txt](requirements.txt) | Sí |
| Datos de prueba | No hay un conjunto separado de datos de prueba. `data/triage_history.csv` es el historial generado por la aplicación, no un dataset de prueba | No |
| Historial de commits de todos los integrantes | No existe repositorio Git (`.git`) ni historial de commits en la carpeta del proyecto | No |
| Créditos y licencias en el README | [README.md](README.md); falta agregar créditos y licencias | No |
