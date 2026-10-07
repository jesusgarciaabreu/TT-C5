"""
Carga y filtrado de los datos de incidentes para el dashboard.

Centraliza el acceso a df_hour_clean.csv (generado en
EDA_Siniestros_Viales_Iztapalapa.ipynb) para que todas las páginas usen
exactamente los mismos datos y los mismos filtros de calidad. Usa
st.cache_data porque el archivo pesa ~56 MB y no cambia entre
interacciones del usuario con los widgets de la barra lateral.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

RUTA_DATOS = Path(__file__).resolve().parents[1] / "data" / "df_hour_clean.csv"

COLUMNAS_NECESARIAS = [
    "fecha_creacion", "hora_creacion", "dia_semana", "tipo_incidente_c4",
    "incidente_c4", "colonia_catalogo", "longitud", "latitud",
    "anio", "mes", "hora", "es_fin_de_semana", "franja_horaria",
    "coord_valida", "es_duplicado_c5", "target", "fecha_hora", "fecha_hora_rango",
]


@st.cache_data(show_spinner="Cargando datos históricos de incidentes...")
def cargar_incidentes(ruta: Path = RUTA_DATOS) -> pd.DataFrame:
    """
    Carga df_hour_clean.csv y aplica los mismos filtros de calidad usados
    en el análisis de autocorrelación espacial del TT:
      - coord_valida == True     : coordenadas geográficas válidas
      - es_duplicado_c5 == False : excluye reportes duplicados del propio C5

    No filtra por `target` aquí (queda como parámetro en filtrar_incidentes)
    porque algunas vistas necesitan comparar confirmados vs. no confirmados.
    """
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta}.\n"
            "Verifica que exista dashboard/data/df_hour_clean.csv."
        )

    df = pd.read_csv(
        ruta,
        usecols=COLUMNAS_NECESARIAS,
        parse_dates=["fecha_hora", "fecha_hora_rango"],
    )

    df = df[(df["coord_valida"] == True) & (df["es_duplicado_c5"] == False)].copy()
    return df


def filtrar_incidentes(
    df: pd.DataFrame,
    anios: list[int] | None = None,
    dias_semana: list[str] | None = None,
    franjas_horarias: list[str] | None = None,
    tipos_incidente: list[str] | None = None,
    solo_confirmados: bool = True,
) -> pd.DataFrame:
    """
    Aplica los filtros elegidos en la barra lateral. Cada filtro es
    opcional: None (o lista vacía, ya normalizada a None antes de llamar
    esta función) significa "sin restricción" en esa dimensión.
    """
    resultado = df.copy()

    if solo_confirmados:
        resultado = resultado[resultado["target"] == 1]
    if anios:
        resultado = resultado[resultado["anio"].isin(anios)]
    if dias_semana:
        resultado = resultado[resultado["dia_semana"].isin(dias_semana)]
    if franjas_horarias:
        resultado = resultado[resultado["franja_horaria"].isin(franjas_horarias)]
    if tipos_incidente:
        resultado = resultado[resultado["incidente_c4"].isin(tipos_incidente)]

    return resultado
