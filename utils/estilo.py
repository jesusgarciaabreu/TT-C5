"""
Paleta y estilo compartidos por gráficas y mapas. Los tonos son
aproximaciones de la identidad visual del IPN (guinda) y de ESCOM (azul),
no valores oficiales de manual de marca.
"""
import streamlit as st

PALETA = {
    "claro": {
        "principal": "#741B47",
        "secundario": "#1F6FA8",
        "categoricos": ["#741B47", "#1F6FA8", "#C9A227", "#5D6D7E", "#2E8B6E", "#A6ACB8"],
        "secuencial": ["#FBF3F6", "#E9B6C8", "#C8557A", "#741B47"],
    },
    "oscuro": {
        "principal": "#C9507A",
        "secundario": "#4FA3D9",
        "categoricos": ["#E06A8F", "#4FA3D9", "#E8C15A", "#8E9AB5", "#4FBF9A", "#B9BFCC"],
        "secuencial": ["#1B2038", "#5A2246", "#A93B66", "#F0A3BC"],
    },
}


def _tema() -> str:
    return "oscuro" if st.context.theme.type == "dark" else "claro"


def color_principal() -> str:
    return PALETA[_tema()]["principal"]


def mapa_estilo() -> str:
    return "carto-darkmatter" if _tema() == "oscuro" else "carto-positron"


def color_secundario() -> str:
    return PALETA[_tema()]["secundario"]


def paleta_categorica() -> list[str]:
    return PALETA[_tema()]["categoricos"]


def escala_secuencial() -> list[str]:
    return PALETA[_tema()]["secuencial"]


def aplicar_estilo(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0),
        hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.2)", zeroline=False)
    return fig
