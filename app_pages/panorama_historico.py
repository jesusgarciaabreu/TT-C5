import streamlit as st
import os
import base64
from utils.carga_datos import cargar_incidentes, filtrar_incidentes
from utils.graficas import (
    serie_temporal,
    mapa_calor_dia_hora,
    ranking_colonias,
    distribucion_tipo_incidente,
    distribucion_por_hora,
    distribucion_mensual,
)
from utils.mapas import mapa_incidentes

st.html(
    """
    <style>
    [data-testid="stPopover"] button {
        transition: transform 160ms cubic-bezier(0.23, 1, 0.32, 1);
    }
    [data-testid="stPopover"] button:active {
        transform: scale(0.97);
    }
    </style>
    """
)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""

def titulo_estilizado(texto, color_texto="#1A365D"):
    html = f"""
    <div style="
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-left: 12px;
        border-left: 6px solid #9F2241; /* Acento estructural guinda */
        color: {color_texto};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-size: 1.6rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    ">
        {texto}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


#st.title("Panorama histórico")

banner_html = """
<style>
    .hero-banner {
        background: linear-gradient(135deg, #9F2241 0%, #1A365D 100%);
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
        color: white;
        text-align: left;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin: 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 0.5px;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        margin-top: 8px;
        opacity: 0.9;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
</style>

<div class="hero-banner">
    <div class="hero-title">Panorama Histórico</div>
    <div class="hero-subtitle">Análisis espaciotemporal de siniestros viales en Iztapalapa</div>
</div>
"""

st.markdown(banner_html, unsafe_allow_html=True)

df = cargar_incidentes()

anios_disponibles = sorted(df["anio"].dropna().unique().astype(int))
dias_disponibles = df["dia_semana"].dropna().unique().tolist()
franjas_disponibles = df["franja_horaria"].dropna().unique().tolist()
tipos_disponibles = sorted(df["incidente_c4"].dropna().unique().tolist())


with st.sidebar:
    st.header("Filtros de Análisis")
    
    solo_confirmados = st.toggle(
        "Solo confirmados",
        value=True,
        help="Excluye reportes que no se confirmaron como incidente real."
    )
    
    st.divider() 
    
    anios_sel = st.pills("Año", anios_disponibles, selection_mode="multi")
    
    dias_sel = st.multiselect(
        "Día de la semana", 
        dias_disponibles, 
        placeholder="Todos los días"
    )
    
    franjas_sel = st.multiselect(
        "Franja horaria", 
        franjas_disponibles, 
        placeholder="Todas las franjas"
    )
    
    tipos_sel = st.multiselect(
        "Tipo de incidente", 
        tipos_disponibles, 
        placeholder="Todos los tipos"
    )

# Si el usuario no elige nada (lista vacía), pasamos todos los datos
anios_filtro = anios_sel if anios_sel else anios_disponibles
dias_filtro = dias_sel if dias_sel else dias_disponibles
franjas_filtro = franjas_sel if franjas_sel else franjas_disponibles
tipos_filtro = tipos_sel if tipos_sel else tipos_disponibles


df_filtrado = filtrar_incidentes(
    df,
    anios=anios_filtro,
    dias_semana=dias_filtro,
    franjas_horarias=franjas_filtro,
    tipos_incidente=tipos_filtro,
    solo_confirmados=solo_confirmados,
)

if df_filtrado.empty:
    st.warning("No hay registros con esta combinación de filtros.")
    st.stop()

dias_periodo = max((df_filtrado["fecha_hora"].max() - df_filtrado["fecha_hora"].min()).days, 1)
hora_pico = int(df_filtrado.groupby("hora").size().idxmax())


# --- INICIO DE TARJETAS (SIN st.container) ---
val_incidentes = f"{len(df_filtrado):,}"
val_porcentaje = f"{100 * len(df_filtrado) / len(df):.1f}%"
val_promedio = f"{len(df_filtrado) / dias_periodo:.1f}"
val_hora = f"{hora_pico:02d}:00"

icono_mapa = get_base64_image("icons/mapa.png")
icono_embudo = get_base64_image("icons/embudo.png")
icono_tendencias = get_base64_image("icons/tendencias.png")
icono_reloj = get_base64_image("icons/reloj.png")

css_tarjetas = """
<style>
    .kpi-wrapper {
        display: flex;
        flex-wrap: wrap;         
        gap: 16px;
        margin-bottom: 1.5rem;
        width: 100%;             
    }
    .kpi-card-guinda {
        flex: 1 1 calc(25% - 16px); 
        min-width: 210px;        
        background-color: #9F2241;
        border-radius: 8px;
        padding: 16px 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        display: flex;           
        align-items: center;     
        gap: 12px;
        min-height: 125px;       
        box-sizing: border-box;  
    }
    .kpi-icon {
        width: 36px;             
        height: 36px;
        flex-shrink: 0;          
        filter: brightness(0) invert(1); 
    }
    .kpi-text-container {
        display: flex;
        padding: 16px 0;
        flex-direction: column;  
        justify-content: center;
        overflow: hidden;        
    }
    .kpi-title-guinda {
        color: #E2E8F0;
        font-size: 1.1rem;
        font-weight: 500;
        margin: 0 0 4px 0;       
        line-height: 1.5;
        white-space: normal;     
    }
    .kpi-value-guinda {
        color: #FFFFFF;
        font-size: 2.2rem !important;       
        font-weight: 800;
        margin: 0;
        line-height: 1;
    }
</style>
"""

html_tarjetas = f"""
<div class="kpi-wrapper">
    <div class="kpi-card-guinda">
        <img src="data:image/png;base64,{icono_mapa}" class="kpi-icon">
        <div class="kpi-text-container">
            <div class="kpi-title-guinda">Incidentes</div>
            <div class="kpi-value-guinda">{val_incidentes}</div>
        </div>
    </div>
    <div class="kpi-card-guinda">
        <img src="data:image/png;base64,{icono_embudo}" class="kpi-icon">
        <div class="kpi-text-container">
            <div class="kpi-title-guinda">Del total cargado</div>
            <div class="kpi-value-guinda">{val_porcentaje}</div>
        </div>
    </div>
    <div class="kpi-card-guinda">
        <img src="data:image/png;base64,{icono_tendencias}" class="kpi-icon">
        <div class="kpi-text-container">
            <div class="kpi-title-guinda">Promedio diario</div>
            <div class="kpi-value-guinda">{val_promedio}</div>
        </div>
    </div>
    <div class="kpi-card-guinda">
        <img src="data:image/png;base64,{icono_reloj}" class="kpi-icon">
        <div class="kpi-text-container">
            <div class="kpi-title-guinda">Hora pico</div>
            <div class="kpi-value-guinda">{val_hora}</div>
        </div>
    </div>
</div>
"""

st.markdown(css_tarjetas + html_tarjetas, unsafe_allow_html=True)

#with st.container(horizontal=True):
#    st.metric("Incidentes en la selección", f"{len(df_filtrado):,}", border=True)
#    st.metric("Del total cargado", f"{100 * len(df_filtrado) / len(df):.1f}%", border=True)
#    st.metric("Promedio diario", f"{len(df_filtrado) / dias_periodo:.1f}", border=True)
#    st.metric("Hora pico", f"{hora_pico:02d}:00", border=True)

st.divider() 

# --- 1. ANÁLISIS ESPACIAL ---
titulo_estilizado("Análisis Espacial")
col_mapa, col_ranking = st.columns([6, 4]) 

with col_mapa:
    with st.container(border=True):
        st.markdown("**Ubicación de los incidentes**")
        st.plotly_chart(mapa_incidentes(df_filtrado), use_container_width=True)

with col_ranking:
    with st.container(border=True):
        st.markdown("**Top Colonias con más incidentes**")
        st.plotly_chart(ranking_colonias(df_filtrado), use_container_width=True)

# --- 2. TIPO DE INCIDENTE ---
titulo_estilizado("Clasificación de Incidentes")
with st.container(border=True):
    st.plotly_chart(distribucion_tipo_incidente(df_filtrado), use_container_width=True)

# --- 3. ANÁLISIS TEMPORAL (Agrupado en pestañas) ---
titulo_estilizado("Análisis Temporal")
tab1, tab2, tab3 = st.tabs(["Evolución histórica", "Mapa de calor (Día/Hora)", "Distribuciones (Hora y Mes)"])

with tab1:
    granularidad = st.segmented_control(
        "Agrupar por",
        ["Día", "Mes"],
        default="Día",
    ) or "Día"
    st.plotly_chart(serie_temporal(df_filtrado, granularidad), use_container_width=True)

with tab2:
    st.plotly_chart(mapa_calor_dia_hora(df_filtrado), use_container_width=True)

with tab3:
    col_hora, col_mes = st.columns(2)
    with col_hora:
        st.markdown("**Distribución por hora del día**")
        st.plotly_chart(distribucion_por_hora(df_filtrado), use_container_width=True)
    with col_mes:
        st.markdown("**Distribución por mes**")
        st.plotly_chart(distribucion_mensual(df_filtrado), use_container_width=True)