"""
Funciones de mapas del dashboard, con Plotly Express (px.scatter_map,
basado en MapLibre -- no requiere token de Mapbox).

Nota de compatibilidad: px.scatter_map existe desde Plotly >= 5.24. Si
tu instalación es más vieja y da AttributeError, usa px.scatter_mapbox
en su lugar (misma firma; solo cambia 'map_style' por 'mapbox_style').
"""
import pandas as pd
import plotly.express as px

from utils.estilo import color_principal, mapa_estilo

# Centro aproximado de Iztapalapa -- así el mapa abre encuadrado aunque
# el filtro activo deje pocos puntos.
CENTRO_IZTAPALAPA = {"lat": 19.357, "lon": -99.06}


def mapa_incidentes(df: pd.DataFrame, muestra_max: int = 20000):
    """
    Mapa de puntos de los incidentes filtrados. Si hay más de
    `muestra_max` registros se toma una muestra (semilla fija, solo para
    no saturar el navegador) -- no afecta a las demás vistas, que usan
    el dataframe filtrado completo.
    """
    datos = df
    if len(df) > muestra_max:
        datos = df.sample(muestra_max, random_state=42)

    fig = px.scatter_map(
        datos,
        lat="latitud",
        lon="longitud",
        hover_data=["fecha_creacion", "hora_creacion", "incidente_c4", "colonia_catalogo"],
        color_discrete_sequence=[color_principal()],
        zoom=11,
        center=CENTRO_IZTAPALAPA,
        height=520,
    )
    fig.update_traces(marker=dict(size=6, opacity=0.55))
    fig.update_layout(map_style=mapa_estilo(), margin=dict(l=0, r=0, t=0, b=0))
    return fig


def mapa_riesgo(nodos_df: pd.DataFrame, probabilidades):
    """
    Mapa de riesgo por nodo del grafo vial (página de Pronóstico).
    `probabilidades` debe estar alineado por posición con nodos_df
    (mismo orden que la columna 'idx' de nodos_grafo.csv).
    """
    datos = nodos_df.copy()
    datos["probabilidad_riesgo"] = probabilidades

    fig = px.scatter_map(
        datos,
        lat="lat",
        lon="lon",
        color="probabilidad_riesgo",
        color_continuous_scale="YlOrRd",
        range_color=(0, max(float(datos["probabilidad_riesgo"].max()), 0.01)),
        zoom=11,
        center=CENTRO_IZTAPALAPA,
        height=550,
    )
    fig.update_layout(map_style="open-street-map", margin=dict(l=0, r=0, t=0, b=0))
    return fig
