from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from dotenv import load_dotenv
from skfuzzy import control as ctrl
import skfuzzy as fuzz

try:
    from supabase import create_client
except Exception:  # pragma: no cover
    create_client = None


load_dotenv()

LOCAL_HISTORY_PATH = Path(__file__).resolve().parent / "data" / "triage_history.csv"


st.set_page_config(
    page_title="TriageAI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #f6f8fb 0%, #eef3f9 100%);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }
        div[data-testid="stSidebar"] {
            background: #f8fafc;
            border-right: 1px solid #e2e8f0;
        }
        .clean-card {
            background: rgba(255,255,255,0.88);
            border: 1px solid #e2e8f0;
            border-radius: 18px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 8px 24px rgba(15, 23, 42, 0.04);
        }
        .priority-badge {
            display: inline-block;
            font-weight: 700;
            font-size: 0.82rem;
            letter-spacing: 0.04em;
            padding: 0.48rem 0.9rem;
            border-radius: 999px;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }
        .priority-low {
            background: #dcfce7;
            color: #166534;
        }
        .priority-medium {
            background: #fef3c7;
            color: #92400e;
        }
        .priority-high {
            background: #fee2e2;
            color: #991b1b;
        }
        .metric-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #64748b;
            font-weight: 600;
        }
        .metric-value {
            font-size: 1.7rem;
            font-weight: 700;
            color: #0f172a;
        }
        .kpi-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.03);
        }
        .subtle-text {
            color: #475569;
            font-size: 0.92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()


@st.cache_data
def build_triage_system():
    temp_universe = np.arange(30.0, 45.1, 0.1)
    heart_rate_universe = np.arange(30, 221, 1)
    pain_universe = np.arange(0, 11, 1)
    urgency_universe = np.arange(0, 101, 1)

    temperature = ctrl.Antecedent(temp_universe, "temperatura")
    heart_rate = ctrl.Antecedent(heart_rate_universe, "frecuencia_cardiaca")
    pain = ctrl.Antecedent(pain_universe, "dolor")
    urgency = ctrl.Consequent(urgency_universe, "urgencia")

    temperature["baja"] = fuzz.trimf(temp_universe, [34, 35.5, 37.5])
    temperature["media"] = fuzz.trimf(temp_universe, [36.5, 38.5, 40.5])
    temperature["alta"] = fuzz.trimf(temp_universe, [38.0, 40.0, 42.0])

    heart_rate["baja"] = fuzz.trimf(heart_rate_universe, [40, 60, 90])
    heart_rate["media"] = fuzz.trimf(heart_rate_universe, [70, 100, 130])
    heart_rate["alta"] = fuzz.trimf(heart_rate_universe, [110, 150, 200])

    pain["bajo"] = fuzz.trimf(pain_universe, [0, 2, 4])
    pain["medio"] = fuzz.trimf(pain_universe, [3, 5, 7])
    pain["alto"] = fuzz.trimf(pain_universe, [6, 8, 10])

    urgency["baja"] = fuzz.trimf(urgency_universe, [0, 20, 40])
    urgency["media"] = fuzz.trimf(urgency_universe, [30, 50, 70])
    urgency["alta"] = fuzz.trimf(urgency_universe, [60, 80, 100])

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

    triage_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(triage_ctrl)


def classify_priority(score: float) -> str:
    if score >= 70:
        return "🔴 PRIORIDAD ALTA - Nivel 2"
    if score >= 40:
        return "🟠 PRIORIDAD MEDIA - Nivel 3"
    return "🟢 PRIORIDAD BAJA - Nivel 4"


def assess_clinical_ranges(temperature: float, heart_rate: int, pain: int) -> tuple[float, list[str]]:
    risk_floors: list[float] = []
    findings: list[str] = []
    critical_finding = False

    if temperature < 35.0:
        risk_floors.append(85.0)
        findings.append("Temperatura menor de 35 °C: hipotermia, requiere valoración médica inmediata")
        critical_finding = True
    elif temperature < 36.0:
        risk_floors.append(45.0)
        findings.append("Temperatura baja (35.0 a 35.9 °C): requiere vigilancia")
    elif temperature < 37.5:
        findings.append("Temperatura dentro del rango normal (36.0 a 37.4 °C)")
    elif temperature < 38.0:
        risk_floors.append(45.0)
        findings.append("Febrícula (37.5 a 37.9 °C): requiere vigilancia")
    elif temperature < 40.0:
        risk_floors.append(55.0)
        findings.append("Fiebre moderada (38.0 a 39.9 °C): requiere valoración según evolución y síntomas")
    else:
        risk_floors.append(85.0)
        findings.append("Temperatura de 40 °C o más: requiere valoración médica inmediata")
        critical_finding = True

    if heart_rate < 40:
        risk_floors.append(85.0)
        findings.append("Pulso menor de 40 ppm en reposo: requiere valoración médica inmediata")
        critical_finding = True
    elif heart_rate < 60:
        risk_floors.append(45.0)
        findings.append("Pulso bajo (40 a 59 ppm en reposo): requiere evaluación y vigilancia")
    elif heart_rate <= 100:
        findings.append("Pulso dentro del rango normal para adultos en reposo (60 a 100 ppm)")
    elif heart_rate <= 130:
        risk_floors.append(45.0)
        findings.append("Pulso elevado (101 a 130 ppm en reposo): requiere evaluación y vigilancia")
    else:
        risk_floors.append(85.0)
        findings.append("Pulso mayor de 130 ppm en reposo: requiere valoración médica inmediata")
        critical_finding = True

    if pain <= 3:
        findings.append("Dolor leve (0 a 3 de 10)")
    elif pain <= 6:
        risk_floors.append(40.0)
        findings.append("Dolor moderado (4 a 6 de 10)")
    else:
        risk_floors.append(70.0)
        findings.append("Dolor intenso (7 a 10 de 10): requiere valoración clínica")

    if not critical_finding and len(risk_floors) >= 2:
        risk_floors.append(65.0)

    return max(risk_floors, default=0.0), findings


def create_summary(temperature: float, heart_rate: int, pain: int, score: float) -> str:
    _, findings = assess_clinical_ranges(temperature, heart_rate, pain)
    return "Análisis orientativo para adulto en reposo: " + "; ".join(findings) + ". " + (
        f"Urgencia estimada: {score:.0f}% ({classify_priority(score).split(' - ')[0]}). "
        "No sustituye una valoración por personal de salud."
    )


def calculate_triage(temperature: float, heart_rate: int, pain: int) -> dict:
    model = build_triage_system()
    model.input["temperatura"] = temperature
    model.input["frecuencia_cardiaca"] = heart_rate
    model.input["dolor"] = pain
    model.compute()

    clinical_floor, _ = assess_clinical_ranges(temperature, heart_rate, pain)
    if "urgencia" not in model.output:
        fuzzy_score = 0.0
    else:
        output_value = model.output["urgencia"]
        if isinstance(output_value, (list, tuple, np.ndarray)):
            output_value = np.asarray(output_value).ravel()
            fuzzy_score = float(output_value[0]) if output_value.size else 0.0
        else:
            fuzzy_score = float(output_value)
    score = max(fuzzy_score, clinical_floor)
    return {
        "score": score,
        "priority_label": classify_priority(score),
        "summary": create_summary(temperature, heart_rate, pain, score),
    }


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key or create_client is None:
        return None
    try:
        return create_client(url, key)
    except Exception:
        return None


def save_to_csv(record: dict) -> None:
    LOCAL_HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    file_exists = LOCAL_HISTORY_PATH.exists()

    with LOCAL_HISTORY_PATH.open("a", encoding="utf-8", newline="") as csv_file:
        headers = [
            "timestamp",
            "patient_name",
            "temperature",
            "heart_rate",
            "pain",
            "urgency_score",
            "priority_label",
            "summary",
        ]
        writer = __import__("csv").DictWriter(csv_file, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)


def save_record_to_history(record: dict) -> bool:
    client = get_supabase_client()
    if client:
        try:
            payload = {
                "timestamp": record["timestamp"],
                "patient_name": record["patient_name"],
                "temperature": float(record["temperature"]),
                "heart_rate": int(record["heart_rate"]),
                "pain": int(record["pain"]),
                "urgency_score": float(record["urgency_score"]),
                "priority_label": record["priority_label"],
                "summary": record["summary"],
            }
            client.table("triage_records").insert(payload).execute()
            return True
        except Exception:
            pass

    save_to_csv(record)
    return False


def load_local_history() -> list[dict]:
    if not LOCAL_HISTORY_PATH.exists():
        return []

    import csv

    rows: list[dict] = []
    with LOCAL_HISTORY_PATH.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            rows.append(row)
    return rows


def render_history_table() -> None:
    history = load_local_history()
    if not history:
        st.info("Todavía no hay registros guardados.")
        return

    table = [
        {
            "Fecha": row.get("timestamp", "-"),
            "Paciente": row.get("patient_name", "-"),
            "Temp. °C": row.get("temperature", "-"),
            "FC": row.get("heart_rate", "-"),
            "Dolor": row.get("pain", "-"),
            "Urgencia": row.get("urgency_score", "-"),
            "Nivel": row.get("priority_label", "-"),
        }
        for row in history[-10:]
    ]
    st.dataframe(table, use_container_width=True)


def render_urgency_chart(score: float) -> None:
    urgency_universe = np.arange(0, 101, 1)
    baja = fuzz.trimf(urgency_universe, [0, 20, 40])
    media = fuzz.trimf(urgency_universe, [30, 50, 70])
    alta = fuzz.trimf(urgency_universe, [60, 80, 100])

    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor("#f8fafc")
    ax.set_facecolor("#f8fafc")
    ax.plot(urgency_universe, baja, label="Baja", linewidth=2, color="#16a34a")
    ax.plot(urgency_universe, media, label="Media", linewidth=2, color="#f59e0b")
    ax.plot(urgency_universe, alta, label="Alta", linewidth=2, color="#dc2626")
    ax.axvline(score, color="#0f172a", linestyle="--", linewidth=2, label=f"Resultado: {score:.0f}%")
    ax.set_title("Curvas de prioridad del triaje")
    ax.set_xlabel("Prioridad (%)")
    ax.set_ylabel("Grado de pertenencia")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    st.pyplot(fig)


def render_priority_banner(label: str, score: float) -> str:
    if score >= 70:
        return "priority-high"
    if score >= 40:
        return "priority-medium"
    return "priority-low"


def main() -> None:
    st.title("TriageAI")
    st.caption("Sistema de priorización clínica basado en lógica difusa")

    with st.sidebar:
        st.header("Datos del paciente")
        patient_name = st.text_input("Nombre o identificador", value="Paciente demo")
        save_enabled = st.checkbox("Guardar en historial", value=True)

    st.subheader("Signos vitales")
    st.caption(
        "Rangos orientativos para adultos en reposo. En menores de 3 meses, una temperatura de 38 °C o más requiere valoración urgente."
    )
    with st.form("triage_form"):
        temperature_col, heart_rate_col, pain_col = st.columns(3)
        with temperature_col:
            with st.container(border=True):
                st.markdown("#### Temperatura")
                st.caption("Temperatura corporal en °C")
                temperature = st.number_input(
                    "Temperatura (°C)",
                    min_value=30.0,
                    max_value=45.0,
                    value=36.8,
                    step=0.1,
                    help="Ingresa un valor entre 30 y 45 °C.",
                )
        with heart_rate_col:
            with st.container(border=True):
                st.markdown("#### Frecuencia cardíaca")
                st.caption("Pulsaciones por minuto")
                heart_rate = st.number_input(
                    "Frecuencia (ppm)",
                    min_value=30,
                    max_value=220,
                    value=72,
                    step=1,
                    format="%d",
                    help="Ingresa un valor entre 30 y 220 pulsaciones por minuto.",
                )
        with pain_col:
            with st.container(border=True):
                st.markdown("#### Dolor")
                st.caption("Escala de 0 a 10")
                pain = st.number_input(
                    "Nivel de dolor",
                    min_value=0,
                    max_value=10,
                    value=2,
                    step=1,
                    format="%d",
                    help="0 indica ausencia de dolor; 10, el máximo nivel.",
                )
        submitted = st.form_submit_button("Calcular prioridad", use_container_width=True)

    if submitted:
        result = calculate_triage(temperature, heart_rate, pain)

        st.markdown("<div class='clean-card'>", unsafe_allow_html=True)
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.markdown("<div class='kpi-box'><div class='metric-label'>Temperatura</div><div class='metric-value'>%.1f °C</div></div>" % temperature, unsafe_allow_html=True)
        with col_b:
            st.markdown("<div class='kpi-box'><div class='metric-label'>Frecuencia</div><div class='metric-value'>%d ppm</div></div>" % heart_rate, unsafe_allow_html=True)
        with col_c:
            st.markdown("<div class='kpi-box'><div class='metric-label'>Dolor</div><div class='metric-value'>%d / 10</div></div>" % pain, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='priority-badge {render_priority_banner(result['priority_label'], result['score'])}'>{result['priority_label']}</div>",
            unsafe_allow_html=True,
        )
        st.subheader("Resultado del triaje")
        st.metric(label="Nivel de urgencia", value=f"{result['score']:.0f}%")
        st.markdown("<div class='clean-card'><div class='subtle-text'>" + result["summary"] + "</div></div>", unsafe_allow_html=True)

        render_urgency_chart(result["score"])

        if save_enabled:
            record = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "patient_name": patient_name,
                "temperature": temperature,
                "heart_rate": heart_rate,
                "pain": pain,
                "urgency_score": f"{result['score']:.2f}",
                "priority_label": result["priority_label"],
                "summary": result["summary"],
            }
            save_result = save_record_to_history(record)
            if save_result:
                st.success("Resultado guardado en Supabase.")
            else:
                st.success("Resultado guardado en el historial local.")

        st.markdown("### Historial")
        render_history_table()

    else:
        st.info("Completa los datos del paciente y presiona el botón para calcular la prioridad del triaje.")

        preview = calculate_triage(36.8, 72, 2)
        st.markdown("<div class='clean-card'>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div class='kpi-box'><div class='metric-label'>Temperatura</div><div class='metric-value'>36.8 °C</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='kpi-box'><div class='metric-label'>Frecuencia</div><div class='metric-value'>72 ppm</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown("<div class='kpi-box'><div class='metric-label'>Dolor</div><div class='metric-value'>2 / 10</div></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='priority-badge {render_priority_banner(preview['priority_label'], preview['score'])}'>{preview['priority_label']}</div>",
            unsafe_allow_html=True,
        )
        st.metric(label="Urgencia de ejemplo", value=f"{preview['score']:.0f}%")
        st.markdown("<div class='clean-card'><div class='subtle-text'>" + preview["summary"] + "</div></div>", unsafe_allow_html=True)
        render_urgency_chart(preview["score"])


if __name__ == "__main__":
    main()
