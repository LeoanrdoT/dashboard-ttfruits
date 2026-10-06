import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="T&T Fruits - Dashboard Ciberfísico OEE & Edge AI",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    .stMetric {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #E9ECEF;
    }
    /* Forzar color oscuro en etiquetas y valores para evitar conflicto con modo oscuro */
    [data-testid="stMetricLabel"] p {
        color: #555555 !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] div {
        color: #111111 !important;
        font-weight: 700;
    }
    .status-badge {
        background-color: #28A745;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 14px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# GENERACIÓN DE DATOS SIMULADOS EN TIEMPO REAL (TURNO OPERATIVO)
# -----------------------------------------------------------------------------
@st.cache_data
def load_realtime_data():
    np.random.seed(42)
    horas = [f"{h:02d}:00" for h in range(6, 14)] # Turno de 06:00 a 14:00
    
    # Producción y OEE por hora
    df_linea = pd.DataFrame({
        "Hora": horas,
        "Throughput_t_h": [11.2, 12.1, 12.8, 12.6, 12.9, 13.1, 12.7, 12.8],
        "Disponibilidad_%": [92.0, 90.5, 88.0, 91.5, 89.0, 90.0, 87.5, 89.6],
        "Rendimiento_%": [93.5, 94.8, 96.0, 95.2, 96.5, 97.0, 94.8, 95.1],
        "Calidad_%": [98.5, 99.1, 99.2, 98.9, 99.4, 99.1, 98.8, 99.0],
    })
    df_linea["OEE_%"] = (df_linea["Disponibilidad_%"] * df_linea["Rendimiento_%"] * df_linea["Calidad_%"]) / 10000

    # Telemetría IoT - Vibración RMS en rodamientos
    tiempos_iot = [datetime.now() - timedelta(minutes=i*5) for i in range(60)][::-1]
    vibracion_rms = np.random.normal(loc=1.8, scale=0.3, size=60)
    vibracion_rms[35:40] += 0.8  # Simulación de pequeña variación de carga
    
    df_iot = pd.DataFrame({
        "Tiempo": tiempos_iot,
        "Vibracion_RMS_mm_s": vibracion_rms,
        "Temperatura_C": np.random.normal(loc=42.0, scale=1.2, size=60),
        "Limite_ISO_10816": 2.8
    })

    # Clasificación por Visión Artificial (Custom CNN)
    df_ia = pd.DataFrame({
        "Clase": ["Ripe (Apto Exportación)", "Unripe (Verde / Tría)", "Overripe (Descarte Neumático)"],
        "Cantidad_Frutos": [128450, 9720, 6980],
        "Porcentaje_%": [88.5, 6.7, 4.8]
    })

    return df_linea, df_iot, df_ia

df_linea, df_iot, df_ia = load_realtime_data()

# -----------------------------------------------------------------------------
# SIDEBAR - PANEL DE NAVEGACIÓN Y ESTADO DE DISPOSITIVOS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://tytfruits.com/wp-content/uploads/2023/08/Logo-jpeg18085.jpg", width=300)
    st.subheader("Sistema Ciberfísico - Mandarina")
    st.markdown("---")
    
    st.selectbox("Planta:", ["Planta Principal - Huaral"], index=0)
    st.selectbox("Línea de Proceso:", ["Línea 01 - Mandarina Satsuma / W. Murcott"], index=0)
    st.radio("Turno:", ["Turno 1 (06:00 - 14:00)", "Turno 2 (14:00 - 22:00)"])
    
    st.markdown("---")
    st.markdown("**Estado de Dispositivos Edge:**")
    st.markdown("🟢 **PLC Siemens S7-1200:** Conectado")
    st.markdown("🟢 **Cámara Borde (Custom CNN):** 42 ms/fruto")
    st.markdown("🟢 **Broker MQTT (Mosquitto):** Activo")
    st.markdown("🟢 **Actuador Neumático:** Regulado ≤ 4.0 N")
    
    st.markdown("---")
    if st.button("🔄 Actualizar Datos en Vivo"):
        st.cache_data.clear()
        st.rerun()

# -----------------------------------------------------------------------------
# ENCABEZADO
# -----------------------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🍊 Monitoreo en Tiempo Real 🍊")
    st.caption("Línea de Empaque de Mandarina | Estándar RAMI 4.0 & Industria 4.0")
with col_h2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<span class='status-badge'>● EN LÍNEA - TURNO ACTIVO</span>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------------------------------------------------
# KPIS PRINCIPALES DE LA JORNADA
# -----------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

oee_actual = df_linea["OEE_%"].iloc[-1]
tp_actual = df_linea["Throughput_t_h"].iloc[-1]
vib_actual = df_iot["Vibracion_RMS_mm_s"].iloc[-1]

kpi1.metric("OEE Acumulado Turno", f"{oee_actual:.2f}%", f"+{(oee_actual - 57.53):.1f}% vs. Base As-Is")
kpi2.metric("Capacidad (Throughput)", f"{tp_actual:.2f} t/h", f"+{(tp_actual - 11.0):.1f} t/h (Meta: 12.5)")
kpi3.metric("Precisión Edge AI", "99.0 %", "Custom CNN (42 ms)")
kpi4.metric("Vibración RMS Faja", f"{vib_actual:.2f} mm/s", "ISO 10816 (< 2.8)", delta_color="normal" if vib_actual < 2.8 else "inverse")
kpi5.metric("Tiempo Setup (SMED)", "24.5 min", "-45.5% vs Histórico")

st.markdown("<br>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PESTAÑAS DE ANÁLISIS
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Performance OEE & Producción", 
    "👁️ Inferencia Edge AI (Visión)", 
    "⚡ Telemetría IoT & Mantenimiento TPM", 
    "⏱️ Registro SMED & Eventos"
])

# TAB 1: OEE Y PRODUCCIÓN
with tab1:
    col_t1_a, col_t1_b = st.columns([2, 1])
    with col_t1_a:
        st.subheader("Evolución Horaria del OEE y Componentes (%)")
        fig_oee = go.Figure()
        fig_oee.add_trace(go.Scatter(x=df_linea["Hora"], y=df_linea["OEE_%"], name="OEE Total (%)", line=dict(color="#1B365D", width=4)))
        fig_oee.add_trace(go.Scatter(x=df_linea["Hora"], y=df_linea["Disponibilidad_%"], name="Disponibilidad (%)", line=dict(dash="dash", color="#2E7D32")))
        fig_oee.add_trace(go.Scatter(x=df_linea["Hora"], y=df_linea["Rendimiento_%"], name="Rendimiento (%)", line=dict(dash="dash", color="#1976D2")))
        fig_oee.add_trace(go.Scatter(x=df_linea["Hora"], y=df_linea["Calidad_%"], name="Calidad (%)", line=dict(dash="dash", color="#E65100")))
        fig_oee.update_layout(height=380, margin=dict(l=20, r=20, t=30, b=20), legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_oee, use_container_width=True)

    with col_t1_b:
        st.subheader("Throughput (t/h) vs Meta")
        fig_tp = px.bar(df_linea, x="Hora", y="Throughput_t_h", color="Throughput_t_h", color_continuous_scale="Blues")
        fig_tp.add_hline(y=12.5, line_dash="dash", line_color="red", annotation_text="Meta: 12.5 t/h")
        fig_tp.update_layout(height=380, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_tp, use_container_width=True)

# TAB 2: INSPECCIÓN EDGE AI
with tab2:
    col_t2_a, col_t2_b = st.columns([1, 1])
    with col_t2_a:
        st.subheader("Distribución de Selección de Mandarinas")
        fig_pie = px.pie(
            df_ia, names="Clase", values="Cantidad_Frutos",
            color="Clase",
            color_discrete_map={
                "Ripe (Apto Exportación)": "#2E7D32",
                "Unripe (Verde / Tría)": "#FBC02D",
                "Overripe (Descarte Neumático)": "#C62828"
            },
            hole=0.45
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_t2_b:
        st.subheader("Parámetros del Sistema de Inferencia Borde")
        st.info("**Modelo Activo:** Custom CNN (3 Capas Convolucionales)")
        st.markdown("""
        * **Accuracy Global de Prueba:** 99.0%
        * **Latencia Promedio por Fruto:** 42 ms (> 24 frutos/segundo)
        * **Explicabilidad Visual (XAI):** Módulo LIME activo (Superpíxeles de croma)
        * **Fuerza de Expulsión Neumática:** 3.8 N (Límite de seguridad ≤ 4.0 N)
        * **Deformación Máxima en Pericarpio:** 0.068 mm (Previene *Penicillium digitatum*)
        """)
        st.success("✅ **Lazo Ciberfísico:** Inferencia en Python ➔ MQTT ➔ PLC Siemens S7-1200 ➔ Actuador Neumático")




# TAB 3: TELEMETRÍA IOT Y TPM
with tab3:
    st.subheader("Monitoreo de Vibración RMS en Rodamientos de Faja (ISO 10816)")
    fig_iot = go.Figure()
    fig_iot.add_trace(go.Scatter(
        x=df_iot["Tiempo"], y=df_iot["Vibracion_RMS_mm_s"],
        mode="lines+markers", name="Vibración RMS (mm/s)",
        line=dict(color="#D32F2F" if vib_actual >= 2.8 else "#1976D2", width=2)
    ))
    fig_iot.add_hline(y=2.8, line_dash="dash", line_color="red", annotation_text="Límite Alerta TPM ISO 10816 (2.8 mm/s RMS)")
    fig_iot.update_layout(height=350, xaxis_title="Hora/Minuto", yaxis_title="Vibración RMS (mm/s)", margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig_iot, use_container_width=True)

# TAB 4: SMED Y EVENTOS
with tab4:
    st.subheader("Registro de Cambios de Lote / Calibre (Estandarización SMED)")
    df_smed = pd.DataFrame({
        "Evento / Lote": ["Lote 01 (Mandarina Satsuma Medium)", "Lote 02 (Mandarina W. Murcott Large)", "Lote 03 (Mandarina W. Murcott Jumbo)"],
        "Tiempo Cambio Histórico (min)": [45.0, 48.0, 42.0],
        "Tiempo Cambio Con SMED (min)": [24.5, 25.0, 23.8],
        "Reducción (%)": ["45.5%", "47.9%", "43.3%"],
        "Estado": ["Completado", "Completado", "Programado 13:30"]
    })


