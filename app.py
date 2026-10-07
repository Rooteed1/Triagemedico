from __future__ import annotations

import csv
import os
from datetime import datetime
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
import streamlit as st
from dotenv import load_dotenv
from skfuzzy import control as ctrl

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None

load_dotenv()
LOCAL_HISTORY_PATH = Path(__file__).resolve().parent / "data" / "triage_history.csv"

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


# ---------- Historial ----------
def get_supabase_client():
    url, key = os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
    if not url or not key or create_client is None:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def save_to_csv(record: dict) -> None:
    LOCAL_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    exists = LOCAL_HISTORY_PATH.exists()
    with LOCAL_HISTORY_PATH.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(record.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(record)


def save_record_to_history(record: dict) -> bool:
    client = get_supabase_client()
    if client:
        try:
            payload = {**record, "temperature": float(record["temperature"]),
                       "heart_rate": int(record["heart_rate"]), "pain": int(record["pain"]),
                       "urgency_score": float(record["urgency_score"])}
            client.table("triage_records").insert(payload).execute()
            return True
        except Exception:
            pass
    save_to_csv(record)
    return False


def load_local_history() -> list[dict]:
    if not LOCAL_HISTORY_PATH.exists():
        return []
    with LOCAL_HISTORY_PATH.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def render_history_table() -> None:
    history = load_local_history()
    if not history:
        st.info("Aún no hay registros. Calcula una prioridad con el historial activado y aparecerá aquí.")
        return
    rows = [
        {"Fecha": r.get("timestamp", "-"), "Paciente": r.get("patient_name", "-"),
         "Temp. (°C)": r.get("temperature", "-"), "FC (ppm)": r.get("heart_rate", "-"),
         "Dolor": r.get("pain", "-"), "Urgencia (%)": r.get("urgency_score", "-"),
         "Nivel": r.get("priority_label", "-")}
        for r in reversed(history[-10:])
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)


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
def main() -> None:
    with st.sidebar:
        st.header("Paciente")
        patient_name = st.text_input("Nombre o identificador", value="Paciente demo")
        save_enabled = st.checkbox("Guardar en historial", value=True)
        st.caption("Si Supabase está configurado se guarda ahí; si no, en un archivo local.")

    st.markdown(
        '<div class="topbar"><div class="cross"></div><div><p class="brand">TriageAI</p>'
        '<p class="brand-sub">Prioridad de atención a partir de signos vitales, con lógica difusa</p></div></div>',
        unsafe_allow_html=True,
    )

    tab_triage, tab_history = st.tabs(["Triaje", "Historial"])

    with tab_triage:
        form_col, result_col = st.columns([1, 1.15], gap="large")

        with form_col:
            with st.form("triage_form"):
                st.markdown('<p class="card-title">Signos vitales</p>', unsafe_allow_html=True)
                temperature = st.number_input("Temperatura (°C)", 30.0, 45.0, 36.8, 0.1,
                                              help="Valor entre 30 y 45 °C. Normal: 36.0 a 37.4 °C.")
                heart_rate = st.number_input("Frecuencia cardíaca (ppm)", 30, 220, 72, 1, format="%d",
                                             help="Valor entre 30 y 220. Normal en reposo: 60 a 100 ppm.")
                pain = st.slider("Dolor (0 a 10)", 0, 10, 2,
                                 help="0 es ausencia de dolor; 10 es el máximo imaginable.")
                submitted = st.form_submit_button("Calcular prioridad", use_container_width=True)
            st.caption("En menores de 3 meses, una temperatura de 38 °C o más requiere valoración urgente.")

        if submitted:
            result = calculate_triage(temperature, int(heart_rate), int(pain))
            st.session_state["last_result"] = result
            if save_enabled:
                record = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "patient_name": patient_name,
                    "temperature": temperature,
                    "heart_rate": int(heart_rate),
                    "pain": int(pain),
                    "urgency_score": f"{result['score']:.2f}",
                    "priority_label": result["label"],
                    "summary": result["summary"],
                }
                if save_record_to_history(record):
                    st.toast("Resultado guardado en Supabase.", icon="✅")
                else:
                    st.toast("Resultado guardado en el historial local.", icon="✅")

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

    with tab_history:
        st.subheader("Últimos 10 registros")
        render_history_table()


if __name__ == "__main__":
    main()
