# Importamos Streamlit para la interfaz web
import streamlit as st

# Importamos Plotly para gráficas interactivas
import plotly.express as px

# Importamos pandas para manejo de datos
import pandas as pd

# Importamos función que trae datos desde ODK
from odk_client import obtener_submissions


# Título del dashboard
st.title("Dashboard Inteligente de Encuestas")


# Cargamos los datos desde ODK
df = obtener_submissions()

# VALIDACIÓN: si no hay datos, mostrar el mensaje:
if df.empty:
    st.error("No se pudieron cargar datos desde la API")
    st.stop()


# Mostramos los datos en tabla
st.subheader("Datos de la encuesta")
st.dataframe(df)


# FUNCIÓN PARA DETECTAR TIPO DE DATO
def detectar_tipo(columna):

    # Si es numérica
    if pd.api.types.is_numeric_dtype(columna):
        return "numerico"

    # Si es fecha
    try:
        pd.to_datetime(columna)
        return "fecha"
    except:
        pass

    # Si es texto o categórico
    return "categorico"


# Selector de columna
columnas = df.columns

variable = st.selectbox(
    "Selecciona una variable",
    columnas
)


# Detectamos tipo de dato
tipo = detectar_tipo(df[variable])


# Mostramos tipo detectado
st.write(f"Tipo detectado: {tipo}")


# 🎯 GENERACIÓN AUTOMÁTICA DE GRÁFICAS

if tipo == "numerico":

    # Histograma para datos numéricos
    fig = px.histogram(
        df,
        x=variable,
        title=f"Distribución de {variable}"
    )

elif tipo == "categorico":

    # Conteo de categorías
    conteo = df[variable].value_counts().reset_index()
    conteo.columns = [variable, "conteo"]

    fig = px.bar(
        conteo,
        x=variable,
        y="conteo",
        title=f"Frecuencia de {variable}"
    )

elif tipo == "fecha":

    # Convertimos a datetime
    df[variable] = pd.to_datetime(df[variable])

    conteo = df.groupby(variable).size().reset_index(name="conteo")

    fig = px.line(
        conteo,
        x=variable,
        y="conteo",
        title=f"Tendencia de {variable}"
    )


# Mostramos gráfica
st.plotly_chart(fig)