import streamlit as st

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

st.title("Panorama histórico")

df = cargar_incidentes()

anios_disponibles = sorted(df["anio"].dropna().unique().astype(int))
dias_disponibles = df["dia_semana"].dropna().unique().tolist()
franjas_disponibles = df["franja_horaria"].dropna().unique().tolist()
tipos_disponibles = sorted(df["incidente_c4"].dropna().unique().tolist())

with st.container(horizontal=True, vertical_alignment="center"):
    solo_confirmados = st.toggle(
        "Solo confirmados",
        value=True,
        help=(
            "Excluye reportes que no se confirmaron como incidente real -- "
            "el mismo filtro usado en el análisis de Moran's I del TT."
        ),
    )
    with st.popover("Filtros"):
        anios_sel = st.pills(
            "Año",
            anios_disponibles,
            selection_mode="multi",
            default=anios_disponibles,
        )
        dias_sel = st.multiselect("Día de la semana", dias_disponibles, default=dias_disponibles)
        franjas_sel = st.multiselect("Franja horaria", franjas_disponibles, default=franjas_disponibles)
        tipos_sel = st.multiselect("Tipo de incidente", tipos_disponibles, default=tipos_disponibles)

if not (anios_sel and dias_sel and franjas_sel and tipos_sel):
    st.warning("Sin selección no hay registros. Elige al menos un valor en cada filtro.")
    st.stop()

df_filtrado = filtrar_incidentes(
    df,
    anios=anios_sel,
    dias_semana=dias_sel,
    franjas_horarias=franjas_sel,
    tipos_incidente=tipos_sel,
    solo_confirmados=solo_confirmados,
)

if df_filtrado.empty:
    st.warning("No hay registros con esta combinación de filtros.")
    st.stop()

dias_periodo = max((df_filtrado["fecha_hora"].max() - df_filtrado["fecha_hora"].min()).days, 1)
hora_pico = int(df_filtrado.groupby("hora").size().idxmax())

#Estilo para las tarjetas de metricas 
st.markdown("""
<style>
    .kpi-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    .kpi-title {
        color: #64748B;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px; /* Espacio entre tu ícono y el texto */
    }
    /* Estilo para asegurar que tus SVGs no se deformen */
    .kpi-title svg, .kpi-title img {
        width: 18px;
        height: 18px;
        fill: currentColor;
    }
    .kpi-value {
        color: #0F172A;
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

with st.container(horizontal=True):
    val_incidentes = f"{len(df_filtrado):,}"
    val_porcentaje = f"{100 * len(df_filtrado) / len(df):.1f}%"
    val_promedio = f"{len(df_filtrado) / dias_periodo:.1f}"
    val_hora = f"{hora_pico:02d}:00"
    #st.metric("Incidentes en la selección", f"{len(df_filtrado):,}", border=True)
    #st.metric("Del total cargado", f"{100 * len(df_filtrado) / len(df):.1f}%", border=True)
    #st.metric("Promedio diario", f"{len(df_filtrado) / dias_periodo:.1f}", border=True)
    #st.metric("Hora pico", f"{hora_pico:02d}:00", border=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 5px solid #9F2241;">
        <div class="kpi-title">
            <!-- INSERTA TU ICONO AQUÍ -->
            Incidentes en la selección
        </div>
        <p class="kpi-value">{val_incidentes}</p>
    </div>
    """, unsafe_allow_html=True)
    with col2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left: 5px solid #235B4E;">
        <div class="kpi-title">
            <!-- INSERTA TU ICONO AQUÍ -->
            Del total cargado
        </div>
        <p class="kpi-value">{val_porcentaje}</p>
    </div>
    """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 5px solid #BC955C;">
            <div class="kpi-title">
                <!-- INSERTA TU ICONO AQUÍ -->
                Promedio diario
            </div>
            <p class="kpi-value">{val_promedio}</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left: 5px solid #1E3A8A;">
            <div class="kpi-title">
                <!-- INSERTA TU ICONO AQUÍ -->
                Hora pico
            </div>
            <p class="kpi-value">{val_hora}</p>
        </div>
        """, unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("Ubicación de los incidentes")
    st.plotly_chart(mapa_incidentes(df_filtrado))

with st.container(border=True):
    st.subheader("Evolución temporal")
    granularidad = st.segmented_control(
        "Agrupar por",
        ["Día", "Mes"],
        default="Día",
    ) or "Día"
    st.plotly_chart(serie_temporal(df_filtrado, granularidad))

with st.container(border=True):
    st.subheader("Día de la semana por hora")
    st.plotly_chart(mapa_calor_dia_hora(df_filtrado))

col_izq, col_der = st.columns(2)
with col_izq:
    with st.container(border=True):
        st.subheader("Colonias con más incidentes")
        st.plotly_chart(ranking_colonias(df_filtrado))
with col_der:
    with st.container(border=True):
        st.subheader("Tipo de incidente")
        st.plotly_chart(distribucion_tipo_incidente(df_filtrado))

col_hora, col_mes = st.columns(2)
with col_hora:
    with st.container(border=True):
        st.subheader("Distribución por hora del día")
        st.plotly_chart(distribucion_por_hora(df_filtrado))
with col_mes:
    with st.container(border=True):
        st.subheader("Distribución por mes")
        st.plotly_chart(distribucion_mensual(df_filtrado))
