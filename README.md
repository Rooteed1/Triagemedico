# TriageAI

Sistema de triaje médico con lógica difusa desarrollado en Python y desplegable como aplicación web con Streamlit.

## Características

- Sliders interactivos para temperatura, frecuencia cardíaca y dolor
- Lógica difusa basada en reglas clínicas simples
- Cálculo de urgencia con nivel porcentual
- Visualización del resultado con curva de prioridad
- Registro e inicio de sesión con Supabase Auth
- Historial privado por usuario en Supabase PostgreSQL
- Uso de mediciones y análisis sin iniciar sesión (sin guardar registros)

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

## Configurar Supabase

1. En el panel del proyecto Supabase, habilita **Authentication > Providers >
   Email**.
2. Ejecuta [`supabase/triage_records.sql`](./supabase/triage_records.sql) en el
   SQL Editor de Supabase para crear la tabla y habilitar Row Level Security.
3. Configura estas variables en `.env` para desarrollo local o en los Secrets
   del servicio de despliegue:

   - `SUPABASE_URL`: URL del proyecto.
   - `SUPABASE_ANON_KEY`: clave pública `anon`/publishable del proyecto.

   Nunca configures `service_role` o una clave `sb_secret_` en la aplicación.

Sin estas variables la aplicación sigue permitiendo mediciones y análisis, pero
no habilita registro, inicio de sesión, guardado ni consulta del historial. Los
registros solo se guardan en Supabase y solo el usuario autenticado que los creó
puede consultarlos.

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
