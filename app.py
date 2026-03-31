import streamlit as st

# =========================
# CONFIG HÍBRIDA (LOCAL + CLOUD)
# =========================

try:
    # 🌐 Streamlit Cloud
    ODK_URL = st.secrets["ODK_URL"]
    PROJECT_ID = st.secrets["PROJECT_ID"]
    FORM_ID = st.secrets["FORM_ID"]
    USERNAME = st.secrets["USERNAME"]
    PASSWORD = st.secrets["PASSWORD"]

except Exception:
    # 💻 Local
    from config import ODK_URL, PROJECT_ID, FORM_ID, USERNAME, PASSWORD

st.set_page_config(page_title="Dashboard Encuestas", layout="wide")

import plotly.express as px
import pandas as pd
from odk_client import obtener_submissions
from ai_analysis import generar_insights, filtrar_columnas_relevantes
from column_mapping import COLUMN_MAPPING, COLUMN_LABELS


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
# 🔥 EXCLUSIÓN DE COLUMNAS
# =========================

EXCLUDE_COLUMNS = [

    # TEXTOS ABIERTOS (_just)
    "Explica qué es GIRS",
    "Explica qué son los lixiviados",
    "Acciones para reducir microplásticos",
    "Influencia de la basura en inundaciones",
    "Tipo de participación",
    "Descripción de tiraderos",
    "Explicación del impacto en salud",
    "Explicación del impuesto",
    "Explicación de brigadas",
    "Opinión del servicio",
    "Explicación de inundaciones",
    "Explicación de acciones",
    "Descripción de problemas",
    "Destino de la basura",
    "Explica qué son los RSU",
    "Ejemplo de reciclaje",
    "Descripción de botes",
    "Cómo separan basura",
    "Dónde viste basura",
    "Explicación del impacto",

    # DATOS QUE YA USAS ARRIBA
    #"Edad",
    "Edad (Primaria)",
    "Edad (Secundaria)",
    "Edad (Hogar)",
    "Edad (Público)",

    #"Sexo",
    "Sexo (Primaria)",
    "Sexo (Secundaria)",

    #Ubicacion
    "Ubicacion",
    "Ubicacion_",

    #Carrera
    "Carrera",

    #salud
    "¿La contaminación afecta la salud?",
    
]

COLUMNAS_PROTEGIDAS = ["Sector"]

# eliminar columnas vacías
df = df.dropna(axis=1, how="all")

# aplicar filtro
columnas_validas = [
    col for col in df.columns
    if col not in EXCLUDE_COLUMNS or col in COLUMNAS_PROTEGIDAS
]

df = df[columnas_validas]


# =========================
# KPIs (MEJOR DISTRIBUCIÓN)
# =========================

def calcular_porcentaje_si(df, columna):
    if columna not in df.columns:
        return None

    serie = df[columna].astype(str)
    serie = serie[~serie.isin(["Sin dato", "nan", "None", ""])]

    if len(serie) < max(3, int(len(df) * 0.2)):
        return None

    si = serie.str.lower().str.contains("si|sí").sum()
    return int((si / len(serie)) * 100)


# Edad promedio
cols_edad = [c for c in df.columns if "Edad" in c]
edad = df[cols_edad].bfill(axis=1).iloc[:, 0] if cols_edad else None
edad = pd.to_numeric(edad, errors="coerce").dropna() if edad is not None else []
edad_prom = int(edad.mean()) if len(edad) > 0 else "N/A"


# KPIs dinámicos
kpi_1 = None
kpi_2 = None
label_1 = ""
label_2 = ""

preguntas_kpi = [
    "¿Conoces el concepto de GIRS?",
    "¿Sabes qué son los lixiviados y cómo afectan el agua?",
    "¿Qué tan grave es el problema de la basura?",
    "¿Cómo percibes el estado del Río Lerma?",
]

for pregunta in preguntas_kpi:
    valor = calcular_porcentaje_si(df, pregunta)

    if valor is not None:
        if kpi_1 is None:
            kpi_1 = valor
            label_1 = COLUMN_LABELS.get(pregunta, pregunta)
        elif kpi_2 is None:
            kpi_2 = valor
            label_2 = COLUMN_LABELS.get(pregunta, pregunta)
            break


# Estado API
estado_api = "🟢 Conectado" if not df.empty else "🔴 Sin conexión"


# =========================
# 🔥 RENDER KPIs EN 2 FILAS
# =========================

# 🔹 FILA 1
col1, col2, col3 = st.columns(3)

col1.metric("Total encuestas", len(df))
col2.metric("Edad promedio", edad_prom)
col3.metric("Estado API", estado_api)

# 🔹 FILA 2
col4, col5, col6 = st.columns(3)

col4.metric("Última actualización", ultima_actualizacion)

if kpi_1 is not None:
    col5.metric(label_1, f"{kpi_1}%")
else:
    col5.metric("Indicador 1", "N/A")

if kpi_2 is not None:
    col6.metric(label_2, f"{kpi_2}%")
else:
    col6.metric("Indicador 2", "N/A")

st.markdown("---")


# =========================
# TABS
# =========================

# tab_general, tab_primaria, tab_secundaria, tab_prepa, tab_hogar, tab_publico = st.tabs([
#     "General", "Primaria", "Secundaria", "Prepa/Uni", "Hogar", "Público"
# ])


# =========================
# LIMPIEZA
# =========================

def limpiar_serie(serie):
    serie = serie.astype(str)
    return serie[~serie.isin(["Sin dato", "nan", "None", ""])]


# =========================
# FUNCIÓN GRÁFICAS (AQUÍ ESTÁ EL CAMBIO CLAVE 🔥)
# =========================

def graficar_por_sector(df_seccion, keyword, titulo):

    st.markdown(f"### {titulo}")

    if df_seccion.empty:
        st.info("No hay datos en este sector")
        return

    cols = st.columns(3)
    i = 0

    for col in df_seccion.columns:

        if col == "Sector":
            continue

        if col.startswith("_") or col.startswith("__"):
            continue

        if "submitter" in col.lower() or "system" in col.lower():
            continue

        if keyword and keyword not in col:
            continue

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

        # 🔥 AQUÍ USAS LOS LABELS
        titulo_grafica = COLUMN_LABELS.get(col, col)

        if len(conteo) <= 3:
            fig = px.pie(
                conteo,
                names=col,
                values="conteo",
                title=titulo_grafica,
                hole=0.5
            )
        else:
            fig = px.bar(
                conteo,
                x=col,
                y="conteo",
                title=titulo_grafica
            )

        with cols[i % 3]:
            st.plotly_chart(fig, use_container_width=True, key=f"{titulo}_{col}_{i}")

        i += 1

    if i == 0:
        st.warning("No hay preguntas con datos suficientes")


# =========================
# GENERAL (SIN TABS)
# =========================

st.markdown("## 📊 Análisis general")
#st.markdown("### Distribución general")

col1, col2, col3 = st.columns(3)

with col1:
        sector = df["Sector"].dropna()
        if not sector.empty:
            conteo = sector.value_counts().reset_index()
            conteo.columns = ["Sector", "conteo"]
            fig = px.pie(conteo, names="Sector", values="conteo", title="Sector", hole=0.5)
            st.plotly_chart(fig, use_container_width=True, key="sector")

with col2:
        if cols_edad:
            edad = df[cols_edad].bfill(axis=1).iloc[:, 0]
            edad = pd.to_numeric(edad, errors="coerce").dropna()
            if not edad.empty:
                conteo = edad.value_counts().sort_index().reset_index()
                conteo.columns = ["Edad", "conteo"]
                fig = px.pie(conteo, names="Edad", values="conteo", title="Edad", hole=0.5)
                st.plotly_chart(fig, use_container_width=True, key="edad")

with col3:
        cols_sexo = [c for c in df.columns if "Sexo" in c]
        if cols_sexo:
            sexo = df[cols_sexo].bfill(axis=1).iloc[:, 0]
            sexo = sexo.astype(str)
            sexo = sexo[~sexo.isin(["None", "nan", ""])]
            if not sexo.empty:
                conteo = sexo.value_counts().reset_index()
                conteo.columns = ["Sexo", "conteo"]
                fig = px.pie(conteo, names="Sexo", values="conteo", title="Sexo", hole=0.5)
                st.plotly_chart(fig, use_container_width=True, key="sexo")

st.markdown("---")
graficar_por_sector(df, "", "Resultados")


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

# with tab_primaria:
#     graficar_por_sector(df_primaria, "Primaria", "Primaria")

# with tab_secundaria:
#     graficar_por_sector(df_secundaria, "Secundaria", "Secundaria")

# with tab_prepa:
#     graficar_por_sector(df_prepa, "Nivel educativo", "Prepa / Universidad")

# with tab_hogar:
#     graficar_por_sector(df_hogar, "Hogar", "Hogar")

# with tab_publico:
#     graficar_por_sector(df_publico, "Público", "Público")


# =========================
# IA
# =========================

st.markdown("---")
st.subheader("Principales hallazgos")


# =========================
# 🔥 DATA LIMPIA PARA IA
# =========================

df_insights = df.copy()

EXCLUDE_INSIGHTS = [
    "start",
    "Fecha",
    "Edad",
    "Edad (Primaria)",
    "Edad (Secundaria)",
    "Edad (Hogar)",
    "Edad (Público)",
    "Sexo",
    "Sector"
]

# eliminar columnas no útiles
df_insights = df_insights.drop(columns=[
    col for col in EXCLUDE_INSIGHTS if col in df_insights.columns
])

# eliminar columnas con puro "Sin dato"
df_insights = df_insights.loc[:, ~(df_insights == "Sin dato").all()]

# eliminar columnas con una sola categoría
df_insights = df_insights.loc[:, df_insights.nunique() > 1]

# 🔥 ahora sí IA limpia
insights = generar_insights(df_insights)

# =========================
# 🔥 FILTRO DE INSIGHTS (AQUÍ VA EL CAMBIO)
# =========================

INSIGHTS_NO_DESEADOS = [
    "sin información",
    "sin dato",
    "registros sin",
    "nan",
    "total de registros"
]

insights_filtrados = [
    i for i in insights
    if not any(palabra in i.lower() for palabra in INSIGHTS_NO_DESEADOS)
]

# mostrar solo útiles
for i in insights_filtrados[:5]:
    st.info(i)
# =========================
# CONCLUSIÓN
# =========================

st.markdown("### Conclusión general")

st.success("""
Se identifican áreas de oportunidad en educación ambiental, especialmente en la separación de residuos y conocimiento práctico del reciclaje.
El dashboard permite visualizar patrones clave para la toma de decisiones.
""")

st.markdown("---")
st.subheader("Datos completos")

st.dataframe(df, use_container_width=True)