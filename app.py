from __future__ import annotations

import base64
import binascii
import json
import logging
import os
from html import escape

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
import streamlit as st
from dotenv import load_dotenv
from streamlit.errors import StreamlitSecretNotFoundError
from skfuzzy import control as ctrl
from supabase import Client, create_client

load_dotenv()
logger = logging.getLogger(__name__)

st.set_page_config(page_title="TriageAI", page_icon="🏥", layout="wide")

# Paleta hospitalaria: azul clínico, verde azulado, blanco y tonos de triaje.
LEVELS = {
    "low": ("Prioridad baja", "Nivel 4", "#1E9E6A", "#E4F5EE"),
    "medium": ("Prioridad media", "Nivel 3", "#D98E00", "#FFF3D6"),
    "high": ("Prioridad alta", "Nivel 2", "#D32F2F", "#FDE7E7"),
}


def inject_css() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');
        :root { --blue:#0B5FA5; --blue-dark:#08467B; --teal:#0E9AA7; --tint:#EAF4FA; --line:#D3E3EE; --ink:#16324A; --muted:#58728A; }
        html, body, .stApp, [data-testid="stAppViewContainer"], h1, h2, h3, h4 { font-family:'Source Sans 3',sans-serif; color:var(--ink); }
        .stApp { background:#FFFFFF; }
        header[data-testid="stHeader"] { background:transparent; }
        .block-container { max-width:1120px; padding-top:1.2rem; padding-bottom:3rem; }
        [data-testid="stSidebar"] { background:var(--tint); border-right:1px solid var(--line); }
        .topbar { display:flex; align-items:center; gap:1rem; background:linear-gradient(100deg,var(--blue) 0%,var(--teal) 100%);
                  border-radius:14px; padding:1.1rem 1.4rem; margin-bottom:1.4rem; }
        .cross { flex:0 0 46px; height:46px; border-radius:10px; background:#fff;
                 background-image:linear-gradient(var(--blue),var(--blue)),linear-gradient(var(--blue),var(--blue));
                 background-size:56% 22%,22% 56%; background-position:center; background-repeat:no-repeat; }
        .brand { color:#fff; font-size:1.9rem; font-weight:700; line-height:1.1; margin:0; }
        .brand-sub { color:#E3F4F7; margin:.15rem 0 0; font-size:1rem; }
        .card { background:#fff; border:1px solid var(--line); border-radius:12px; padding:1.2rem 1.4rem; }
        .card-title { color:var(--blue); font-weight:700; font-size:1.1rem; margin:0 0 .6rem; }
        [data-testid="stForm"] { background:var(--tint); border:1px solid var(--line); border-radius:12px; padding:1.2rem 1.4rem; }
        div[data-testid="stFormSubmitButton"] > button { background:var(--blue); color:#fff; border:none; border-radius:8px;
                 padding:.7rem 1.2rem; font-weight:700; font-size:1.05rem; }
        div[data-testid="stFormSubmitButton"] > button:hover { background:var(--blue-dark); color:#fff; }
        div[data-testid="stFormSubmitButton"] > button:focus-visible { outline:3px solid var(--teal); outline-offset:2px; }
        button[data-baseweb="tab"][aria-selected="true"] { color:var(--blue); font-weight:700; }
        div[data-baseweb="tab-highlight"] { background:var(--blue); }
        .banner { border-radius:12px; padding:1rem 1.3rem; display:flex; justify-content:space-between; align-items:center; border-left:8px solid; }
        .banner b { font-size:1.3rem; }
        .banner span { font-size:.95rem; color:var(--muted); }
        .ring-wrap { display:flex; align-items:center; gap:1.4rem; padding:1.1rem 0 .4rem; }
        .ring { flex:0 0 150px; height:150px; border-radius:50%; display:flex; align-items:center; justify-content:center; }
        .ring-in { width:112px; height:112px; border-radius:50%; background:#fff; display:flex; flex-direction:column;
                   align-items:center; justify-content:center; }
        .ring-num { font-size:2.5rem; font-weight:700; line-height:1; }
        .ring-cap { font-size:.8rem; color:var(--muted); }
        .legend { color:var(--muted); font-size:.92rem; line-height:1.7; }
        .legend i { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:.5rem; }
        .vital { display:flex; gap:.8rem; padding:.7rem 0; border-bottom:1px solid var(--line); align-items:flex-start; }
        .vital:last-child { border-bottom:none; }
        .chip { flex:0 0 auto; font-size:.8rem; font-weight:700; padding:.2rem .65rem; border-radius:999px; margin-top:.1rem; }
        .vital-name { font-weight:700; }
        .vital-text { color:var(--muted); font-size:.93rem; }
        .note { color:var(--muted); font-size:.86rem; background:var(--tint); border-radius:8px; padding:.6rem .8rem; margin-top:.9rem; }
        @media (max-width:640px){ .ring-wrap{ flex-direction:column; align-items:flex-start; } .banner{ flex-direction:column; align-items:flex-start; gap:.3rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()


@st.cache_resource
def build_triage_system():
    temp_u = np.arange(30.0, 45.1, 0.1)
    hr_u = np.arange(30, 221, 1)
    pain_u = np.arange(0, 11, 1)
    urg_u = np.arange(0, 101, 1)

    temperature = ctrl.Antecedent(temp_u, "temperatura")
    heart_rate = ctrl.Antecedent(hr_u, "frecuencia_cardiaca")
    pain = ctrl.Antecedent(pain_u, "dolor")
    urgency = ctrl.Consequent(urg_u, "urgencia")

    temperature["baja"] = fuzz.trimf(temp_u, [34, 35.5, 37.5])
    temperature["media"] = fuzz.trimf(temp_u, [36.5, 38.5, 40.5])
    temperature["alta"] = fuzz.trimf(temp_u, [38.0, 40.0, 42.0])
    heart_rate["baja"] = fuzz.trimf(hr_u, [40, 60, 90])
    heart_rate["media"] = fuzz.trimf(hr_u, [70, 100, 130])
    heart_rate["alta"] = fuzz.trimf(hr_u, [110, 150, 200])
    pain["bajo"] = fuzz.trimf(pain_u, [0, 2, 4])
    pain["medio"] = fuzz.trimf(pain_u, [3, 5, 7])
    pain["alto"] = fuzz.trimf(pain_u, [6, 8, 10])
    urgency["baja"] = fuzz.trimf(urg_u, [0, 20, 40])
    urgency["media"] = fuzz.trimf(urg_u, [30, 50, 70])
    urgency["alta"] = fuzz.trimf(urg_u, [60, 80, 100])

    rules = [
        ctrl.Rule(temperature["alta"] & pain["alto"], urgency["alta"]),
        ctrl.Rule(temperature["alta"] & pain["medio"], urgency["alta"]),
        ctrl.Rule(temperature["media"] & pain["alto"], urgency["media"]),
        ctrl.Rule(heart_rate["alta"] & pain["alto"], urgency["alta"]),
        ctrl.Rule(temperature["baja"] & pain["bajo"], urgency["baja"]),
        ctrl.Rule(temperature["media"] & heart_rate["media"] & pain["medio"], urgency["media"]),
        ctrl.Rule(temperature["alta"] & heart_rate["alta"], urgency["alta"]),
        ctrl.Rule(pain["alto"], urgency["alta"]),
        ctrl.Rule(heart_rate["alta"], urgency["media"]),
        ctrl.Rule(temperature["media"] & pain["bajo"], urgency["baja"]),
    ]
    return ctrl.ControlSystem(rules)


def level_key(score: float) -> str:
    return "high" if score >= 70 else "medium" if score >= 40 else "low"


def assess_clinical_ranges(temperature: float, heart_rate: int, pain: int):
    """Devuelve (piso de riesgo, lista de (signo, texto, gravedad)). Gravedad: 0 normal, 1 vigilar, 2 crítico."""
    floors: list[float] = []
    items: list[tuple[str, str, int]] = []
    critical = False

    if temperature < 35.0:
        floors.append(85.0); critical = True
        items.append(("Temperatura", "Menor de 35 °C: hipotermia, requiere valoración médica inmediata", 2))
    elif temperature < 36.0:
        floors.append(45.0)
        items.append(("Temperatura", "Baja (35.0 a 35.9 °C): requiere vigilancia", 1))
    elif temperature < 37.5:
        items.append(("Temperatura", "Dentro del rango normal (36.0 a 37.4 °C)", 0))
    elif temperature < 38.0:
        floors.append(45.0)
        items.append(("Temperatura", "Febrícula (37.5 a 37.9 °C): requiere vigilancia", 1))
    elif temperature < 40.0:
        floors.append(55.0)
        items.append(("Temperatura", "Fiebre moderada (38.0 a 39.9 °C): valorar según evolución y síntomas", 1))
    else:
        floors.append(85.0); critical = True
        items.append(("Temperatura", "40 °C o más: requiere valoración médica inmediata", 2))

    if heart_rate < 40:
        floors.append(85.0); critical = True
        items.append(("Frecuencia cardíaca", "Menor de 40 ppm en reposo: requiere valoración médica inmediata", 2))
    elif heart_rate < 60:
        floors.append(45.0)
        items.append(("Frecuencia cardíaca", "Baja (40 a 59 ppm en reposo): requiere evaluación y vigilancia", 1))
    elif heart_rate <= 100:
        items.append(("Frecuencia cardíaca", "Dentro del rango normal en adultos en reposo (60 a 100 ppm)", 0))
    elif heart_rate <= 130:
        floors.append(45.0)
        items.append(("Frecuencia cardíaca", "Elevada (101 a 130 ppm en reposo): requiere evaluación y vigilancia", 1))
    else:
        floors.append(85.0); critical = True
        items.append(("Frecuencia cardíaca", "Mayor de 130 ppm en reposo: requiere valoración médica inmediata", 2))

    if pain <= 3:
        items.append(("Dolor", "Leve (0 a 3 de 10)", 0))
    elif pain <= 6:
        floors.append(40.0)
        items.append(("Dolor", "Moderado (4 a 6 de 10)", 1))
    else:
        floors.append(70.0)
        items.append(("Dolor", "Intenso (7 a 10 de 10): requiere valoración clínica", 2))

    if not critical and len(floors) >= 2:
        floors.append(65.0)
    return max(floors, default=0.0), items


def calculate_triage(temperature: float, heart_rate: int, pain: int) -> dict:
    sim = ctrl.ControlSystemSimulation(build_triage_system())
    sim.input["temperatura"] = temperature
    sim.input["frecuencia_cardiaca"] = heart_rate
    sim.input["dolor"] = pain
    sim.compute()

    floor, items = assess_clinical_ranges(temperature, heart_rate, pain)
    fuzzy = 0.0
    if "urgencia" in sim.output:
        out = np.asarray(sim.output["urgencia"]).ravel()
        fuzzy = float(out[0]) if out.size else 0.0
    score = max(fuzzy, floor)
    key = level_key(score)
    name, tag, _, _ = LEVELS[key]
    summary = (
        "Análisis orientativo para adulto en reposo: "
        + "; ".join(f"{n}: {t}" for n, t, _ in items)
        + f". Urgencia estimada: {score:.0f}% ({name}). No sustituye una valoración por personal de salud."
    )
    return {"score": score, "key": key, "label": f"{name} - {tag}", "items": items, "summary": summary}


# ---------- Supabase, autenticación e historial ----------
def _get_setting(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    try:
        secret = st.secrets.get(name)
    except StreamlitSecretNotFoundError:
        return None
    return str(secret) if secret else None


def get_supabase_config() -> tuple[str, str] | None:
    url = _get_setting("SUPABASE_URL")
    anon_key = _get_setting("SUPABASE_ANON_KEY")
    if not url or not anon_key:
        return None
    if anon_key.startswith("sb_secret_"):
        raise ValueError("SUPABASE_ANON_KEY debe ser la clave pública anon/publishable.")
    parts = anon_key.split(".")
    if len(parts) == 3:
        try:
            claims = json.loads(base64.urlsafe_b64decode(parts[1] + "==="))
        except (ValueError, UnicodeDecodeError, binascii.Error):
            claims = {}
        if claims.get("role") == "service_role":
            raise ValueError("No configures una clave service_role en la aplicación.")
    return url, anon_key


def get_supabase_client() -> Client | None:
    config = get_supabase_config()
    if config is None:
        return None
    cached_config = st.session_state.get("_supabase_config")
    client = st.session_state.get("_supabase_client")
    if client is None or cached_config != config:
        client = create_client(*config)
        st.session_state["_supabase_client"] = client
        st.session_state["_supabase_config"] = config
    return client


def save_record_to_history(client: Client, record: dict) -> None:
    client.table("triage_records").insert(record).execute()


def load_user_history(client: Client, user_id: str) -> list[dict]:
    response = (
        client.table("triage_records")
        .select("created_at, patient_name, temperature, heart_rate, pain, urgency_score, priority_label")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    return response.data or []


def render_history_table(client: Client, user_id: str) -> None:
    try:
        history = load_user_history(client, user_id)
    except Exception:
        logger.exception("No se pudo consultar el historial de Supabase.")
        st.error("No se pudo cargar tu historial. Verifica tu conexión e inténtalo de nuevo.")
        return

    if not history:
        st.info("Aún no hay atenciones guardadas en esta cuenta.")
        return
    rows = [
        {
            "Fecha": r.get("created_at", "-"),
            "Paciente": r.get("patient_name", "-"),
            "Temp. (°C)": r.get("temperature", "-"),
            "FC (ppm)": r.get("heart_rate", "-"),
            "Dolor": r.get("pain", "-"),
            "Urgencia (%)": r.get("urgency_score", "-"),
            "Nivel": r.get("priority_label", "-"),
        }
        for r in history
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_auth_controls() -> tuple[Client | None, str | None]:
    st.header("Cuenta")
    try:
        config = get_supabase_config()
        if config is None:
            st.info("Las mediciones funcionan sin cuenta. Configura Supabase para habilitar registro, inicio de sesión y guardado.")
            return None, None
        client = get_supabase_client()
        if client is None:
            st.info("Las mediciones funcionan sin cuenta. Configura Supabase para habilitar el historial.")
            return None, None
    except Exception:
        logger.exception("No se pudo configurar el cliente de Supabase.")
        st.error("No se pudo configurar la conexión con Supabase. Revisa SUPABASE_URL y SUPABASE_ANON_KEY.")
        return None, None

    try:
        session = client.auth.get_session()
    except Exception:
        logger.exception("No se pudo recuperar la sesión de Supabase.")
        st.error("No se pudo verificar tu sesión. Intenta iniciar sesión de nuevo.")
        session = None

    if session is not None:
        user = getattr(session, "user", None)
        user_id = getattr(user, "id", None)
        if not user_id:
            st.error("La sesión no contiene un usuario válido. Cierra sesión e inténtalo de nuevo.")
            return client, None
        email = getattr(user, "email", None) or "Usuario autenticado"
        user_metadata = getattr(user, "user_metadata", None)
        display_name = (
            user_metadata.get("full_name") or user_metadata.get("name")
            if isinstance(user_metadata, dict)
            else None
        )
        st.caption(f"Sesión iniciada: {display_name or email}")
        if display_name:
            st.caption(email)
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            try:
                client.auth.sign_out()
            except Exception:
                logger.exception("No se pudo cerrar la sesión de Supabase.")
                st.error("No se pudo cerrar la sesión. Inténtalo de nuevo.")
            else:
                st.session_state.pop("last_result", None)
                st.rerun()
        return client, user_id

    mode = st.radio(
        "Acceso",
        ("🔐 Iniciar sesión", "📝 Registrarse"),
        horizontal=True,
        label_visibility="collapsed",
    )
    with st.form("auth_form"):
        email = st.text_input("Correo electrónico", autocomplete="email")
        is_signup = mode.startswith("📝")
        display_name = (
            st.text_input("Nombre", autocomplete="name") if is_signup else ""
        )
        password = st.text_input(
            "Contraseña",
            type="password",
            autocomplete="new-password" if is_signup else "current-password",
        )
        submitted = st.form_submit_button(
            "Crear cuenta" if is_signup else "Iniciar sesión",
            use_container_width=True,
        )

    if submitted:
        if not email.strip() or not password or (is_signup and not display_name.strip()):
            st.error(
                "Escribe tu nombre, correo electrónico y contraseña."
                if is_signup
                else "Escribe tu correo electrónico y contraseña."
            )
        else:
            try:
                if not is_signup:
                    client.auth.sign_in_with_password(
                        {"email": email.strip(), "password": password}
                    )
                    st.rerun()
                else:
                    response = client.auth.sign_up(
                        {
                            "email": email.strip(),
                            "password": password,
                            "options": {
                                "data": {"full_name": display_name.strip()}
                            },
                        }
                    )
                    if getattr(response, "session", None) is not None:
                        st.success("Cuenta creada e inicio de sesión realizado.")
                        st.rerun()
                    else:
                        st.success("Cuenta creada. Revisa tu correo para confirmar la dirección e iniciar sesión.")
            except Exception as exc:
                logger.exception("Falló la operación de autenticación de Supabase.")
                action = "crear la cuenta" if is_signup else "iniciar sesión"
                st.error(f"No se pudo {action}: {exc}")
    return client, None


# ---------- Visualización ----------
SEV = {0: ("Normal", "#1E9E6A", "#E4F5EE"), 1: ("Vigilar", "#B87800", "#FFF3D6"), 2: ("Urgente", "#D32F2F", "#FDE7E7")}


def render_result(result: dict) -> None:
    name, tag, color, tint = LEVELS[result["key"]]
    score = min(result["score"], 100)
    st.markdown(
        f"""
        <div class="banner" style="background:{tint}; border-color:{color};">
          <b style="color:{color};">{name}</b><span>{tag} de triaje</span>
        </div>
        <div class="card" style="margin-top:.9rem;">
          <p class="card-title">Nivel de urgencia</p>
          <div class="ring-wrap">
            <div class="ring" style="background:conic-gradient({color} {score*3.6:.0f}deg, #E3EDF3 0);">
              <div class="ring-in"><span class="ring-num" style="color:{color};">{score:.0f}%</span><span class="ring-cap">urgencia</span></div>
            </div>
            <div class="legend">
              <div><i style="background:#1E9E6A;"></i>0 a 39: baja</div>
              <div><i style="background:#D98E00;"></i>40 a 69: media</div>
              <div><i style="background:#D32F2F;"></i>70 a 100: alta</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_findings(result: dict) -> None:
    rows = ""
    for n, t, sev in result["items"]:
        label, fg, bg = SEV[sev]
        rows += (
            f'<div class="vital"><span class="chip" style="color:{fg}; background:{bg};">{label}</span>'
            f'<div><div class="vital-name">{escape(n)}</div><div class="vital-text">{escape(t)}</div></div></div>'
        )
    st.markdown(
        f'<div class="card"><p class="card-title">Lectura por signo vital</p>{rows}'
        '<div class="note">Análisis orientativo para adultos en reposo. No sustituye una valoración por personal de salud.</div></div>',
        unsafe_allow_html=True,
    )


def render_curves(score: float) -> None:
    u = np.arange(0, 101, 1)
    curves = [("Baja", [0, 20, 40], "#1E9E6A"), ("Media", [30, 50, 70], "#D98E00"), ("Alta", [60, 80, 100], "#D32F2F")]
    fig, ax = plt.subplots(figsize=(10, 3.6))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")
    for label, abc, color in curves:
        y = fuzz.trimf(u, abc)
        ax.plot(u, y, label=label, linewidth=2.2, color=color)
        ax.fill_between(u, y, alpha=0.1, color=color)
    ax.axvline(score, color="#0B5FA5", linestyle="--", linewidth=2, label=f"Resultado: {score:.0f}%")
    ax.set_xlabel("Urgencia (%)", color="#58728A")
    ax.set_ylabel("Grado de pertenencia", color="#58728A")
    ax.tick_params(colors="#58728A")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color("#D3E3EE")
    ax.grid(True, alpha=0.25)
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.15))
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ---------- App ----------
def render_triage_form(
    patient_name: str,
    save_enabled: bool,
    client: Client | None,
    user_id: str | None,
) -> None:
    form_col, result_col = st.columns([1, 1.15], gap="large")
    save_error = False

    with form_col:
        with st.form("triage_form"):
            st.markdown('<p class="card-title">Signos vitales</p>', unsafe_allow_html=True)
            temperature = st.number_input(
                "Temperatura (°C)",
                30.0,
                45.0,
                36.8,
                0.1,
                help="Valor entre 30 y 45 °C. Normal: 36.0 a 37.4 °C.",
            )
            heart_rate = st.number_input(
                "Frecuencia cardíaca (ppm)",
                30,
                220,
                72,
                1,
                format="%d",
                help="Valor entre 30 y 220. Normal en reposo: 60 a 100 ppm.",
            )
            pain = st.slider(
                "Dolor (0 a 10)",
                0,
                10,
                2,
                help="0 es ausencia de dolor; 10 es el máximo imaginable.",
            )
            submitted = st.form_submit_button("Calcular prioridad", use_container_width=True)
        st.caption("En menores de 3 meses, una temperatura de 38 °C o más requiere valoración urgente.")

    if submitted:
        result = calculate_triage(temperature, int(heart_rate), int(pain))
        st.session_state["last_result"] = result
        if save_enabled and client is not None and user_id:
            if not patient_name.strip():
                st.error("Escribe el nombre del paciente para guardar esta atención.")
                save_error = True
            else:
                record = {
                    "patient_name": patient_name.strip(),
                    "temperature": float(temperature),
                    "heart_rate": int(heart_rate),
                    "pain": int(pain),
                    "urgency_score": float(result["score"]),
                    "priority_label": result["label"],
                    "summary": result["summary"],
                }
                try:
                    save_record_to_history(client, record)
                except Exception:
                    logger.exception("No se pudo guardar la atención en Supabase.")
                    st.error("No se pudo guardar la atención en Supabase. El análisis está disponible, pero no se guardó el registro.")
                    save_error = True
                else:
                    st.session_state["pending_toast"] = "Atención guardada en tu historial de Supabase."
                    st.session_state["clear_patient"] = True
                    st.rerun()

    result = st.session_state.get("last_result")
    with result_col:
        if result is None:
            st.info("Completa los signos vitales y presiona Calcular prioridad para ver el resultado.")
        else:
            render_result(result)

    if result is not None:
        render_findings(result)
        with st.expander("Ver curvas de prioridad del modelo difuso"):
            render_curves(result["score"])
    if not user_id:
        st.caption("Puedes usar todas las mediciones sin iniciar sesión. Para guardar atenciones, inicia sesión.")
    elif not save_enabled:
        st.caption("Esta atención no se guardará; puedes activarlo antes de calcular la siguiente.")
    elif not save_error and not patient_name.strip():
        st.caption("Escribe el nombre del paciente para poder guardar una atención.")


def main() -> None:
    if "patient_name" not in st.session_state:
        st.session_state["patient_name"] = ""
    if st.session_state.pop("clear_patient", False):
        st.session_state["patient_name"] = ""

    pending = st.session_state.pop("pending_toast", None)
    if pending:
        st.toast(pending, icon="✅")

    st.markdown(
        '<div class="topbar"><div class="cross"></div><div><p class="brand">TriageAI</p>'
        '<p class="brand-sub">Prioridad de atención a partir de signos vitales, con lógica difusa</p></div></div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        client, user_id = render_auth_controls()
        st.header("Paciente")
        patient_name = st.text_input("Nombre del paciente", key="patient_name")
        save_enabled = False
        if user_id:
            save_enabled = st.checkbox("Guardar esta atención en mi historial", value=True)
        else:
            st.caption("Sin sesión, el cálculo y el análisis están disponibles; no se guardan datos.")

    if client is not None and user_id is not None:
        tab_triage, tab_history = st.tabs(["Triaje", "Historial"])
        with tab_triage:
            render_triage_form(patient_name, save_enabled, client, user_id)
        with tab_history:
            st.subheader("Últimas 10 atenciones")
            render_history_table(client, user_id)
    else:
        render_triage_form(patient_name, False, None, None)


if __name__ == "__main__":
    main()
