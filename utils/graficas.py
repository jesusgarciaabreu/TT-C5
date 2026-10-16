"""
Funciones de graficación del dashboard (Plotly). Cada función recibe un
dataframe ya filtrado y regresa una figura lista para st.plotly_chart --
mantiene las páginas (app_pages/*.py) enfocadas en la composición de la
vista, no en el detalle de cómo se construye cada gráfica.
"""
import pandas as pd
import plotly.express as px

from utils.estilo import aplicar_estilo, color_principal, escala_secuencial, paleta_categorica

ORDEN_DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
ORDEN_MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
TOP_TIPOS = 5


def serie_temporal(df: pd.DataFrame, granularidad: str):
    """
    Agrega el conteo de incidentes según la granularidad elegida en la UI.
    'Día' y 'Mes' usan fecha_hora_rango (ya redondeada a la hora, la misma
    columna usada para construir el panel del modelo); 'Hora del día' y
    'Día de la semana' muestran el patrón agregado sobre todo el periodo
    filtrado (útil para ver la estacionalidad diaria/semanal).
    """
    regla = "D" if granularidad == "Día" else "MS"
    serie = df.set_index("fecha_hora_rango").sort_index().resample(regla).size()
    datos = serie.rename_axis("periodo").reset_index(name="incidentes")
    fig = px.line(datos, x="periodo", y="incidentes")
    fig.update_traces(line_color=color_principal(), line_width=2)
    fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Incidentes")
    return aplicar_estilo(fig)


def mapa_calor_dia_hora(df: pd.DataFrame):
    """Intensidad de incidentes por día de la semana y hora del día."""
    tabla = (
        df.groupby(["dia_semana", "hora"]).size()
        .unstack(fill_value=0)
        .reindex(index=ORDEN_DIAS, columns=range(24), fill_value=0)
    )
    fig = px.imshow(
        tabla.values,
        x=list(range(24)),
        y=ORDEN_DIAS,
        color_continuous_scale=escala_secuencial(),
        aspect="auto",
        labels=dict(x="Hora del día", y="", color="Incidentes"),
    )
    fig.update_xaxes(dtick=2, showgrid=False)
    fig.update_yaxes(showgrid=False)
    fig.update_coloraxes(colorbar=dict(thickness=12, title="Incidentes"))
    return aplicar_estilo(fig)


def ranking_colonias(df: pd.DataFrame, top_n: int = 15):
    """Top-N colonias con más incidentes en la selección actual."""
    conteo = (
        df["colonia_catalogo"]
        .value_counts()
        .head(top_n)
        .sort_values(ascending=True)  # ascendente: en un bar horizontal, queda de mayor a menor arriba
        .rename_axis("colonia")
        .reset_index(name="incidentes")
    )
    fig = px.bar(conteo, x="incidentes", y="colonia", orientation="h")
    fig.update_traces(marker_color=color_principal())
    fig.update_layout(showlegend=False, yaxis_title=None, xaxis_title="Incidentes")
    return aplicar_estilo(fig)


def distribucion_tipo_incidente(df: pd.DataFrame):
    """
    Distribución por tipo (incidente_c4). Los tipos fuera del top se agrupan
    en 'Otros' para que pocas categorías no compitan por color con muchas.
    """
    conteo = df["incidente_c4"].value_counts()
    if len(conteo) > TOP_TIPOS:
        otros = pd.Series({"Otros": conteo.iloc[TOP_TIPOS:].sum()})
        conteo = pd.concat([conteo.iloc[:TOP_TIPOS], otros])
    fig = px.pie(
        names=conteo.index,
        values=conteo.values,
        hole=0.55,
        color_discrete_sequence=paleta_categorica(),
    )
    fig.update_traces(textinfo="percent", textposition="inside", sort=False)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=-0.02, xanchor="left", x=0),
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def distribucion_por_hora(df: pd.DataFrame):
    """Distribución de incidentes por hora del día (0-23), estacionalidad diurna."""
    serie = (
        df.groupby("hora").size()
        .reindex(range(24), fill_value=0)
        .rename_axis("hora_dia")
        .reset_index(name="incidentes")
    )
    fig = px.bar(serie, x="hora_dia", y="incidentes")
    fig.update_traces(marker_color=color_principal())
    fig.update_layout(showlegend=False, xaxis_title="Hora del día", yaxis_title="Incidentes")
    return aplicar_estilo(fig)


def distribucion_mensual(df: pd.DataFrame):
    """Incidentes por mes del año (estacionalidad anual, suma de todos los años de la selección)."""
    serie = (
        df.groupby("mes").size()
        .reindex(range(1, 13), fill_value=0)
        .rename_axis("mes_num")
        .reset_index(name="incidentes")
    )
    serie["mes"] = ORDEN_MESES
    fig = px.bar(serie, x="mes", y="incidentes", category_orders={"mes": ORDEN_MESES})
    fig.update_traces(marker_color=color_principal())
    fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title="Incidentes")
    return aplicar_estilo(fig)
