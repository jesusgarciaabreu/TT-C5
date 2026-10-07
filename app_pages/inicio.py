from pathlib import Path

import streamlit as st

from utils.carga_datos import cargar_incidentes

RUTA_IMAGENES = Path(__file__).resolve().parents[1] / "static" / "inicio"

st.html(
    """
    <style>
    @keyframes entrada {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div:nth-child(-n+3) {
        animation: entrada 400ms cubic-bezier(0.23, 1, 0.32, 1) both;
    }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div:nth-child(2) { animation-delay: 60ms; }
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div:nth-child(3) { animation-delay: 120ms; }
    @media (prefers-reduced-motion: reduce) {
        [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > div { animation: none; }
    }
    </style>
    """
)


def seccion(titulo: str, texto: str, imagen: str | None = None, pie: str | None = None, invertir: bool = False) -> None:
    st.subheader(titulo)
    ruta = RUTA_IMAGENES / imagen if imagen else None
    if ruta is None or not ruta.exists():
        st.markdown(texto)
        return
    izquierda, derecha = st.columns([1, 1], gap="large", vertical_alignment="center")
    col_texto, col_imagen = (derecha, izquierda) if invertir else (izquierda, derecha)
    with col_texto:
        st.markdown(texto)
    with col_imagen:
        st.image(str(ruta), caption=pie, width="stretch")


try:
    df = cargar_incidentes()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

confirmados = int((df["target"] == 1).sum())

st.title("Siniestros viales en Iztapalapa")
st.markdown(
    "Herramienta prospectiva de análisis espacio-temporal para entender dónde y "
    "cuándo ocurren los siniestros viales en la alcaldía más poblada de la Ciudad de México."
)

hero = RUTA_IMAGENES / "hero.jpg"
if hero.exists():
    _, centro, _ = st.columns([1, 2, 1])
    with centro:
        st.image(str(hero), width="stretch")

st.markdown(
    """
    Iztapalapa concentra el mayor número de siniestros viales de la capital. Entre
    2014 y 2024, el C5 registró más de 340 mil incidentes viales en la alcaldía. La
    atención de estas emergencias suele reaccionar después del hecho: se despachan
    unidades cuando llega el reporte, sin una lectura previa de qué zonas y horas
    concentran el riesgo.
    """
)

with st.container(horizontal=True):
    st.metric("Registros del C5", f"{len(df):,}", border=True)
    st.metric(
        "Incidentes confirmados",
        f"{confirmados:,}",
        border=True,
        help="Código de cierre 'A' (afirmativo): incidente verificado en sitio.",
    )
    st.metric("Colonias con incidentes", f"{df['colonia_catalogo'].nunique():,}", border=True)
    st.metric(
        "Periodo",
        f"{df['fecha_hora'].min():%Y} – {df['fecha_hora'].max():%Y}",
        border=True,
        help=f"Datos hasta el {df['fecha_hora'].max():%d/%m/%Y}.",
    )

seccion(
    "Por qué Iztapalapa",
    """
    De los reportes que recibe el C5 en la alcaldía, solo alrededor de un tercio
    se confirma como incidente real en sitio. El resto son duplicados, falsas
    alarmas u otros códigos de cierre. Por eso este dashboard trabaja solo con los
    confirmados: son los que describen un siniestro verificado.
    """,
    imagen="figura_alcaldias.png",
    pie="Total histórico de siniestros viales por alcaldía (2014–2024).",
)

seccion(
    "El problema",
    """
    La incidencia no es uniforme. Se concentra en ciertas colonias, en franjas
    horarias específicas y en días de la semana concretos. Sin una vista
    espacio-temporal, cualquier decisión sobre dónde ubicar unidades o cuándo
    reforzar la vigilancia depende de la intuición. El objetivo de esta herramienta
    es poner esos patrones frente a quien toma decisiones.
    """,
)

st.subheader("Cómo funciona")
st.markdown(
    """
    Primero se limpian los reportes del C5: se descartan coordenadas inválidas y
    duplicados, y se conservan los incidentes confirmados. Después se mide la
    **autocorrelación espacial**, es decir, si las zonas con muchos incidentes están
    cerca de otras zonas con muchos incidentes. Para eso se usan Moran's I, LISA y
    Getis-Ord Gi\\*, sobre una **malla hexagonal H3** (celdas de unos 0.7 km²). La red
    de calles de OpenStreetMap define qué zonas son vecinas. El modelo GCN-LSTM
    estimaría el riesgo por zona y hora, pero está en pausa mientras se termina su
    entrenamiento.
    """
)
hoy = RUTA_IMAGENES / "flujo_actual.png"
if hoy.exists():
    st.image(str(hoy), caption="Qué existe hoy en el proyecto. El modelo está en pausa.", width="stretch")

seccion(
    "Qué encontrarás",
    """
    En **Panorama histórico** están los patrones descriptivos: dónde ocurren los
    incidentes, cómo cambian en el tiempo, qué colonias tienen más reportes, qué
    tipo son y a qué horas, días y meses se concentran. Un panel de filtros permite
    acotar por año, día, franja horaria y tipo de incidente.
    """,
    imagen="mapa_lisa.png",
    pie="Clusters LISA sobre la red vial de Iztapalapa.",
)

st.subheader("Alcance y limitaciones")
st.markdown(
    """
    Los datos son abiertos del C5 y llegan hasta el 28 de febrero de 2024. El
    análisis espacial usa solo incidentes confirmados, así que las cifras de esta
    página no son el total de reportes. Este es un prototipo: no se conecta a datos
    en vivo ni a despachos reales.
    """
)

st.caption("Trabajo Terminal 2027-A082 · ESCOM-IPN · Directores: Dr. César Jesús Núñez Prado y Dra. Fabiola Ocampo Botello.")
