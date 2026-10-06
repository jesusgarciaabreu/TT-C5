"""
Página: Pronóstico (GCN + LSTM)

Depende de artefactos que se exportan DESPUÉS de entrenar el modelo
(ver scripts/exportar_despues_de_entrenar.py). Mientras no existan,
esta página solo explica qué falta -- no simula un pronóstico con
pesos sin entrenar, porque eso mostraría un resultado sin sustento.
"""
import streamlit as st

from utils.carga_datos import cargar_incidentes
from utils.mapas import mapa_riesgo
from utils.modelo import (
    RUTA_DATA,
    artefactos_disponibles,
    cargar_artefactos,
    construir_ventana_reciente,
    predecir_riesgo,
)

st.set_page_config(page_title="Pronóstico", page_icon="🔮", layout="wide")
st.title("🔮 Pronóstico de riesgo por nodo (GCN + LSTM)")

if not artefactos_disponibles():
    st.warning(
        "Esta sección todavía no tiene un modelo entrenado disponible.\n\n"
        f"Se espera encontrar en `{RUTA_DATA}`:\n"
        "- `modelo_gcn_lstm.pt`\n"
        "- `nodos_grafo.csv`\n"
        "- `edge_index.npy`\n"
        "- `metadatos_modelo.json`\n\n"
        "Estos archivos se generan pegando y corriendo "
        "`scripts/exportar_despues_de_entrenar.py` como celda final de "
        "`modelo_gcn_lstm.ipynb`, en el mismo kernel donde se entrenó el modelo."
    )
    st.stop()

modelo, nodos_df, edge_index, metadatos = cargar_artefactos()
df_incidentes = cargar_incidentes()

st.info(
    "**Importante sobre esta versión preliminar**: la ventana de entrada usa "
    "las últimas horas disponibles en los datos históricos cargados, no un "
    "feed en vivo. Como se discutió en el TT, C5 no publica los incidentes con "
    "una latencia compatible con pronóstico en tiempo real -- esta vista es "
    "una prueba de concepto de la tubería de inferencia, no un sistema "
    "operando sobre datos de hoy."
)

T = metadatos.get("T", 24)
matriz_ventana = construir_ventana_reciente(df_incidentes, nodos_df, T)
probabilidades = predecir_riesgo(modelo, matriz_ventana, edge_index)

hora_pronosticada = df_incidentes["fecha_hora_rango"].max()
st.subheader(f"Riesgo pronosticado para la hora siguiente a {hora_pronosticada}")
st.plotly_chart(mapa_riesgo(nodos_df, probabilidades), use_container_width=True)

st.subheader("Nodos con mayor riesgo pronosticado")
top = (
    nodos_df.assign(probabilidad_riesgo=probabilidades)
    .sort_values("probabilidad_riesgo", ascending=False)
    .head(20)
)
st.dataframe(top[["nodo_id", "lat", "lon", "probabilidad_riesgo"]], use_container_width=True)
