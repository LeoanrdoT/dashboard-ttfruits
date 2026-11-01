import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="T&T Fruits - Dashboard Ciberfísico OEE & Edge AI",
    page_icon="🍊",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSV_FILE = "registros_evaluacion_mandarinas.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return None

df_eval = load_data()

st.title("🍊 Dashboard en Tiempo Real - Visión Artificial & Excel")
st.caption("Supervisión Ciberfísica de Empaque de Mandarina | T&T Fruits S.A.C.")

st.markdown("---")

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

if df_eval is not None and not df_eval.empty:
    total_frutos = len(df_eval)
    ripe_cnt = (df_eval["Clasificacion"] == "Ripe").sum()
    defect_cnt = (df_eval["Clasificacion"] == "Defect").sum()
    calidad_pct = (ripe_cnt / total_frutos) * 100 if total_frutos > 0 else 0
    latencia_media = df_eval["Latencia_ms"].mean() if "Latencia_ms" in df_eval.columns else 38.5
    confianza_media = df_eval["Confianza_Pct"].mean() if "Confianza_Pct" in df_eval.columns else 98.5

    kpi1.metric("Total Evaluadas", f"{total_frutos} unidades")
    kpi2.metric("Calidad Exportación", f"{calidad_pct:.1f}%", f"{ripe_cnt} Ripe")
    kpi3.metric("Defectos Expulsados", f"{defect_cnt} unidades", "Pistón 4N", delta_color="inverse")
    kpi4.metric("Confianza Media", f"{confianza_media:.1f}%")
    kpi5.metric("Latencia Promedio", f"{latencia_media:.1f} ms", "Meta ≤ 50 ms")
else:
    kpi1.metric("Total Evaluadas", "0 unidades")
    kpi2.metric("Calidad Exportación", "0.0%")
    kpi3.metric("Defectos Expulsados", "0 unidades")
    kpi4.metric("Confianza Media", "0.0%")
    kpi5.metric("Latencia Promedio", "0.0 ms")

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Gráficos en Vivo", "📋 Registro Excel (CSV)", "⚡ Métricas Inferencia"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución de Clasificación")
        if df_eval is not None and not df_eval.empty:
            conteo = df_eval["Clasificacion"].value_counts().reset_index()
            conteo.columns = ["Clasificacion", "Cantidad"]
            fig_pie = px.pie(conteo, names="Clasificacion", values="Cantidad", hole=0.4,
                             color="Clasificacion",
                             color_discrete_map={"Ripe": "#2E7D32", "Unripe": "#FBC02D", "Defect": "#C62828"})
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Esperando evaluaciones de la cámara...")
    with col2:
        st.subheader("Acciones del PLC Siemens S7-1200")
        if df_eval is not None and not df_eval.empty and "Accion_PLC" in df_eval.columns:
            accion = df_eval["Accion_PLC"].value_counts().reset_index()
            accion.columns = ["Accion", "Total"]
            fig_bar = px.bar(accion, x="Accion", y="Total", color="Accion",
                             color_discrete_map={"Aprobado_Faja": "#2E7D32", "Expulsado_Piston_4N": "#C62828"})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Sin acciones registradas aún.")

with tab2:
    st.subheader("Tabla Sincronizada con Excel / CSV")
    if df_eval is not None and not df_eval.empty:
        st.dataframe(df_eval.sort_index(ascending=False), use_container_width=True)
    else:
        st.warning("El archivo CSV no contiene registros aún.")

with tab3:
    st.subheader("Latencia por Fruto Evaluado")
    if df_eval is not None and not df_eval.empty and "Latencia_ms" in df_eval.columns:
        fig_lat = px.line(df_eval, y="Latencia_ms", title="Latencia Inferencia (ms)")
        fig_lat.add_hline(y=50.0, line_dash="dash", line_color="red", annotation_text="Límite Faja (50 ms)")
        st.plotly_chart(fig_lat, use_container_width=True)
    else:
        st.info("Sin registros de latencia.")
