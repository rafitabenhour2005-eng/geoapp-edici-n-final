import streamlit as st
import geopandas as gpd
import pandas as pd
import leafmap.foliumap as leafmap
import plotly.express as px

st.set_page_config(
    page_title="Reservas afectadas por incendios",
    layout="wide"
)

st.title("🔥 Reservas afectadas por incendios forestales")

#---------------------------------------------------
# Cargar datos
#---------------------------------------------------

@st.cache_data
def cargar_datos():

    reservas = gpd.read_file("datos/reservas.geojson")

    incendios = gpd.read_file("datos/incendios.geojson")

    estadisticas = pd.read_csv("datos/estadisticas.csv")

    return reservas, incendios, estadisticas

reservas, incendios, estadisticas = cargar_datos()

#---------------------------------------------------
# Barra lateral
#---------------------------------------------------

st.sidebar.header("Filtros")

lista = sorted(reservas["nombre"].unique())

reserva = st.sidebar.selectbox(
    "Seleccione una reserva",
    lista
)

anio = st.sidebar.slider(
    "Año",
    2010,
    2025,
    2020
)

#---------------------------------------------------
# Filtrar datos
#---------------------------------------------------

reserva_sel = reservas[
    reservas["nombre"] == reserva
]

incendios_sel = incendios[
    incendios["anio"] == anio
]

#---------------------------------------------------
# Mapa
#---------------------------------------------------

m = leafmap.Map()

m.add_basemap("HYBRID")

m.add_gdf(
    reserva_sel,
    layer_name="Reserva"
)

m.add_gdf(
    incendios_sel,
    layer_name="Incendios"
)

m.to_streamlit(height=600)

#---------------------------------------------------
# Estadísticas
#---------------------------------------------------

st.header("Estadísticas")

col1, col2, col3 = st.columns(3)

datos = estadisticas[
    estadisticas["reserva"] == reserva
]

if len(datos) > 0:

    col1.metric(
        "Incendios",
        int(datos["incendios"].sum())
    )

    col2.metric(
        "Área quemada (ha)",
        round(datos["ha_quemadas"].sum(),2)
    )

    col3.metric(
        "% afectado",
        round(datos["porcentaje"].mean(),2)
    )

#---------------------------------------------------
# Gráfico
#---------------------------------------------------

st.header("Área quemada por año")

fig = px.bar(
    datos,
    x="anio",
    y="ha_quemadas",
    color="ha_quemadas"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

#---------------------------------------------------
# Tabla
#---------------------------------------------------

st.header("Datos")

st.dataframe(datos)

#---------------------------------------------------
# Descargar CSV
#---------------------------------------------------

csv = datos.to_csv(index=False)

st.download_button(
    "Descargar estadísticas",
    csv,
    "estadisticas.csv",
    "text/csv"
)