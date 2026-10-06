# TriageAI

Sistema de triaje médico con lógica difusa desarrollado en Python y desplegable como aplicación web con Streamlit.

## Características

- Sliders interactivos para temperatura, frecuencia cardíaca y dolor
- Lógica difusa basada en reglas clínicas simples
- Cálculo de urgencia con nivel porcentual
- Visualización del resultado con curva de prioridad
- Historial de registros local o en Supabase

## Requisitos

- Python 3.10+
- pip

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución local

```bash
streamlit run app.py
```

## Variables de entorno opcionales

Copia `.env.example` a `.env` y configura estas variables si quieres guardar resultados en Supabase:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_clave_anonima_o_service_role
```

## Despliegue gratuito

### Opción recomendada
- Streamlit Cloud

## Estructura del proyecto

```text
triageai/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── data/
```

## Nota

Este es un prototipo académico para apoyo de decisión y no sustituye a un diagnóstico médico profesional.
