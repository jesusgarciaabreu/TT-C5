import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="Consultando datos históricos en Neon PostgreSQL...", ttl="1d")
def cargar_incidentes() -> pd.DataFrame:
    # Conexión a Neon usando los secretos de Streamlit
    conn = st.connection("neon_db", type="sql")
    
    # Consulta SQL directa (PostgreSQL hace el filtrado pesado de nulos y duplicados)
    query = """
        SELECT fecha_creacion, hora_creacion, dia_semana, tipo_incidente_c4,
               incidente_c4, colonia_catalogo, longitud, latitud,
               anio, mes, hora, es_fin_de_semana, franja_horaria,
               target, fecha_hora, fecha_hora_rango
        FROM siniestros_historico
        WHERE coord_valida = TRUE AND es_duplicado_c5 = FALSE;
    """
    
    df = conn.query(query)
    
    # Aseguramos el formato datetime para que Streamlit y Plotly no fallen
    df["fecha_hora"] = pd.to_datetime(df["fecha_hora"])
    df["fecha_hora_rango"] = pd.to_datetime(df["fecha_hora_rango"])
    
    return df

def filtrar_incidentes(
    df: pd.DataFrame,
    anios: list[int] | None = None,
    dias_semana: list[str] | None = None,
    franjas_horarias: list[str] | None = None,
    tipos_incidente: list[str] | None = None,
    solo_confirmados: bool = True,
) -> pd.DataFrame:
    
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