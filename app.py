# Configuración de la página
import streamlit as st
st.set_page_config(page_title="Dashboard Encuestas", layout="wide")

import plotly.express as px
import pandas as pd
from odk_client import obtener_submissions
from ai_analysis import generar_insights, filtrar_columnas_relevantes
from column_mapping import COLUMN_MAPPING


# =========================
# HEADER
# =========================

col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.jpeg", width=280)

with col2:
    st.title("Dashboard Encuesta Educación Ambiental")
    st.caption("Visualización de resultados de encuestas ambientales - UAM Lerma")

st.markdown("---")


# =========================
# DATA
# =========================

df = obtener_submissions()
df = filtrar_columnas_relevantes(df)

# Fecha última actualización
ultima_actualizacion = "N/A"

if "start" in df.columns:
    try:
        fecha = pd.to_datetime(df["start"]).max()
        ultima_actualizacion = fecha.strftime("%Y-%m-%d %H:%M")
    except:
        ultima_actualizacion = "N/A"

# Mapping
df = df.rename(columns=COLUMN_MAPPING)

if df.empty:
    st.warning("Sin datos disponibles")
    st.stop()


# =========================
# MÉTRICAS
# =========================

col1, col2, col3 = st.columns(3)

col1.metric("Total encuestas", len(df))
col2.metric("Última actualización", ultima_actualizacion)
col3.metric("Sectores", df["Sector"].nunique())


# =========================
# TABLA DE DATOS
# =========================

st.markdown("---")
st.subheader("Datos de la encuesta")

st.dataframe(df, use_container_width=True)

st.markdown("---")


# =========================
# TABS
# =========================

tab_general, tab_primaria, tab_secundaria, tab_prepa, tab_hogar, tab_publico = st.tabs([
    "General", "Primaria", "Secundaria", "Prepa/Uni", "Hogar", "Público"
])


# =========================
# LIMPIEZA
# =========================

def limpiar_serie(serie):
    serie = serie.astype(str)
    return serie[~serie.isin(["Sin dato", "nan", "None", ""])]


# =========================
# FUNCIÓN INTELIGENTE
# =========================

def graficar_por_sector(df_seccion, keyword, titulo):

    st.markdown(f"### {titulo}")

    if df_seccion.empty:
        st.info("No hay datos en este sector")
        return

    cols = st.columns(3)
    i = 0

    for col in df_seccion.columns:

        # ❌ eliminar metadatos
        if col.startswith("_") or col.startswith("__"):
            continue

        if "submitter" in col.lower() or "system" in col.lower():
            continue

        # filtro por sector
        if keyword and keyword not in col:
            continue

        # evitar ruido
        if "Edad" in col or "Sexo" in col or "Fecha" in col:
            continue

        serie = limpiar_serie(df_seccion[col])

        if serie.empty or serie.nunique() <= 1:
            continue

        try:
            conteo = serie.value_counts().reset_index()
            conteo.columns = [col, "conteo"]
        except:
            continue

        if len(conteo) > 10:
            continue

        if len(conteo) <= 3:
            fig = px.pie(conteo, names=col, values="conteo", title=col[:40], hole=0.5)
        else:
            fig = px.bar(conteo, x=col, y="conteo", title=col[:40])

        with cols[i % 3]:
            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"{titulo}_{col}_{i}"
            )

        i += 1

    if i == 0:
        st.warning("No hay preguntas con datos suficientes")


# =========================
# GENERAL
# =========================

with tab_general:

    st.markdown("### Distribución general")

    col1, col2, col3 = st.columns(3)

    # =========================
    # SECTOR
    # =========================

    with col1:

        sector = df["Sector"].dropna()

        if not sector.empty:

            conteo = sector.value_counts().reset_index()
            conteo.columns = ["Sector", "conteo"]

            fig = px.pie(
                conteo,
                names="Sector",
                values="conteo",
                title="Sector",
                hole=0.5
            )

            st.plotly_chart(fig, use_container_width=True, key="sector_general")

    # =========================
    # EDAD (LIMPIA)
    # =========================

    with col2:

        cols_edad = [c for c in df.columns if "Edad" in c]

        if cols_edad:

            edad = df[cols_edad].bfill(axis=1).iloc[:, 0]
            edad = pd.to_numeric(edad, errors="coerce")
            edad = edad.dropna()

            if not edad.empty:

                conteo = edad.value_counts().sort_index().reset_index()
                conteo.columns = ["Edad", "conteo"]

                fig = px.pie(
                    conteo,
                    names="Edad",
                    values="conteo",
                    title="Edad",
                    hole=0.5
                )

                st.plotly_chart(fig, use_container_width=True, key="edad_general")

    # =========================
    # SEXO (LIMPIO)
    # =========================

    with col3:

        cols_sexo = [c for c in df.columns if "Sexo" in c]

        if cols_sexo:

            sexo = df[cols_sexo].bfill(axis=1).iloc[:, 0]
            sexo = sexo.astype(str)
            sexo = sexo[~sexo.isin(["None", "nan", ""])]
            sexo = sexo.dropna()

            if not sexo.empty:

                conteo = sexo.value_counts().reset_index()
                conteo.columns = ["Sexo", "conteo"]

                fig = px.pie(
                    conteo,
                    names="Sexo",
                    values="conteo",
                    title="Sexo",
                    hole=0.5
                )

                st.plotly_chart(fig, use_container_width=True, key="sexo_general")

    # =========================
    # RESTO DEL DASHBOARD
    # =========================

    st.markdown("---")

    graficar_por_sector(df, "", "General")


# =========================
# FILTROS
# =========================

df["Sector"] = df["Sector"].astype(str)

df_primaria = df[df["Sector"].str.lower().str.strip() == "primaria"]
df_secundaria = df[df["Sector"].str.lower().str.strip() == "secundaria"]
df_prepa = df[df["Sector"].str.lower().str.contains("prepa")]
df_hogar = df[df["Sector"].str.lower().str.strip() == "hogar"]
df_publico = df[df["Sector"].str.lower().str.strip() == "publico"]


# =========================
# TABS POR SECTOR
# =========================

with tab_primaria:
    graficar_por_sector(df_primaria, "Primaria", "Primaria")

with tab_secundaria:
    graficar_por_sector(df_secundaria, "Secundaria", "Secundaria")

with tab_prepa:
    graficar_por_sector(df_prepa, "Nivel educativo", "Prepa / Universidad")

with tab_hogar:
    graficar_por_sector(df_hogar, "Hogar", "Hogar")

with tab_publico:
    graficar_por_sector(df_publico, "Público", "Público")


# =========================
# IA
# =========================

st.markdown("---")
st.subheader("Insights automáticos")

insights = generar_insights(df)

for i in insights[:5]:
    st.markdown(f"- {i}")