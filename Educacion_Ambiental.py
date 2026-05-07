import streamlit as st

st.set_page_config(
    page_title="Dashboard EcoUAM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# PALETA GLOBAL
# =========================

COLOR_PRIMARIO = "#1565C0"
COLOR_SECUNDARIO = "#64B5F6"
COLOR_EXITO = "#26A69A"
COLOR_ALERTA = "#FFA726"
COLOR_PELIGRO = "#EF5350"

PALETA = [
    COLOR_PRIMARIO,
    COLOR_SECUNDARIO,
    COLOR_EXITO,
    COLOR_ALERTA,
    COLOR_PELIGRO
]

# =========================
# CSS
# =========================

st.markdown("""
<style>

/* TEXTO GENERAL */
html, body, [class*="css"] {
    font-size: 16px !important;
}

/* KPI */
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 1px solid #e6e6e6;
    padding: 18px;
    border-radius: 14px;
    text-align: center;
}

/* TITULO KPI */
div[data-testid="metric-container"] label {
    font-size: 18px !important;
    font-weight: 600 !important;
}

/* NUMERO KPI */
[data-testid="stMetricValue"] {
    font-size: 34px !important;
    font-weight: bold !important;
    color: #1565C0 !important;
    white-space: normal !important;
    overflow-wrap: break-word !important;
    line-height: 1.1 !important;
}
/* TITULOS */
h1 {
    font-size: 38px !important;
}

h2 {
    font-size: 28px !important;
}

h3 {
    font-size: 22px !important;
}

</style>
""", unsafe_allow_html=True)

import plotly.express as px
import pandas as pd

from odk_client import obtener_submissions

from ai_analysis import (
    generar_insights,
    filtrar_columnas_relevantes
)

from column_mapping import (
    COLUMN_MAPPING,
    COLUMN_LABELS
)


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
# =========================
# FORMULARIO EDUCACIÓN AMBIENTAL
# =========================

PROJECT_ID = "3"

FORM_ID = "Educacio%CC%81n%20ambiental%203"
df = obtener_submissions(PROJECT_ID, FORM_ID)
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

# =========================
# LIMPIEZA VISUAL
# =========================

SEXO = {
    "masculino": "Masculino",
    "femenino": "Femenino"
}

SECTOR = {
    "primaria": "Primaria",
    "secundaria": "Secundaria",
    "hogar": "Hogar",
    "publico": "Público",
    "prepa": "Preparatoria",
    "universidad": "Universidad"
}

if "Sexo" in df.columns:
    df["Sexo"] = df["Sexo"].replace(SEXO)

if "Sector" in df.columns:
    df["Sector"] = df["Sector"].replace(SECTOR)

REEMPLAZOS = {

    # =========================
    # SEXO
    # =========================

    "f": "Femenino",
    "m": "Masculino",

    # =========================
    # NIVEL EDUCATIVO
    # =========================

    "uni": "Universidad",
    "prepa": "Preparatoria",

    # =========================
    # RESPUESTAS BINARIAS
    # =========================

    "si": "Sí",
    "sí": "Sí",
    "no": "No",
    "talvez": "Tal vez",

    # =========================
    # RESIDUOS
    # =========================

    "rsu": "RSU",
    "raee": "RAEE",
    "rp": "RP",

    "rsu raee": "RSU + RAEE",
    "rsu rp": "RSU + RP",
    "raee rp": "RAEE + RP",
    "rsu raee rp": "RSU + RAEE + RP",

    # =========================
    # PROBLEMAS AMBIENTALES
    # =========================

    "corrupcion": "Corrupción",
    "educacion": "Educación",
    "quema": "Quema",
    "rio": "Río",
    "tiradero": "Tiradero",
    "contaminacion": "Contaminación",

    # =========================
    # RESIDUOS ELECTRÓNICOS
    # =========================

    "guardo": "Guardo",
    "acopio": "Centro de acopio",
    "basura": "Basura común",

    # =========================
    # ACCIONES ILEGALES
    # =========================

    "quema rio cascajo": "Quema + Río + Cascajo",

    # =========================
    # OTROS
    # =========================

    "depende": "Depende"
}

# Aplicar reemplazos visuales
df = df.replace(REEMPLAZOS)

if df.empty:
    st.warning("Sin datos disponibles")
    st.stop()




# =========================
#  EXCLUSIÓN DE COLUMNAS
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
#  RENDER KPIs EN 2 FILAS
# =========================

# 🔹 FILA 1
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total encuestas",
    len(df)
)

col2.metric(
    "Edad promedio",
    edad_prom
)

col3.metric(
    "Estado API",
    estado_api
)

# 🔹 FILA 2
col4, col5, col6 = st.columns(3)

col4.metric(
    "Última actualización",
    ultima_actualizacion
)

# =========================
# KPI 1
# =========================

if kpi_1 is not None:

    col5.metric(
        label_1[:30],
        f"{kpi_1}%"
    )

else:

    col5.metric(
        "Indicador 1",
        "N/A"
    )

# =========================
# KPI 2
# =========================

if kpi_2 is not None:

    col6.metric(
        label_2.split(" sobre ")[0],
        f"{kpi_2}%"
    )

else:

    col6.metric(
        "Indicador 2",
        "N/A"
    )

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
# FUNCIÓN GRÁFICAS 
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

        # =========================
        # USO DE LABELS
        # =========================

        titulo_grafica = COLUMN_LABELS.get(col, col)

        # =========================
        # PIE CHART
        # =========================

        if len(conteo) <= 3:

            fig = px.pie(
                conteo,
                names=col,
                values="conteo",
                title=titulo_grafica,
                hole=0.5,
                color_discrete_sequence=PALETA
            )

            fig.update_layout(
                template="plotly_white"
            )

        # =========================
        # BAR CHART
        # =========================

        else:

            fig = px.bar(
                conteo,
                x=col,
                y="conteo",
                color=col,
                color_discrete_sequence=PALETA,
                title=titulo_grafica,
                text="conteo",
                template="plotly_white"
            )

            fig.update_layout(
                showlegend=False,
                height=400
            )

            fig.update_traces(
                textposition="outside",
                cliponaxis=False
            )

        # =========================
        # RENDER
        # =========================

        with cols[i % 3]:

            st.plotly_chart(
                fig,
                use_container_width=True,
                key=f"{titulo}_{col}_{i}",
                config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                    "doubleClick": False,
"showTips": False,
"staticPlot": True
                }
            )

        i += 1

    if i == 0:
        st.warning("No hay preguntas con datos suficientes")


# =========================
# GENERAL (SIN TABS)
# =========================

st.markdown("## Análisis general")
# st.markdown("### Distribución general")

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
            hole=0.5,
            color_discrete_sequence=PALETA
        )

        fig.update_layout(
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            key="sector",
            config={
                "displayModeBar": False,
                "scrollZoom": False,
                "doubleClick": False,
"showTips": False,
"staticPlot": True
            }
        )

# =========================
# EDAD
# =========================

with col2:

    if cols_edad:

        edad = df[cols_edad].bfill(axis=1).iloc[:, 0]

        edad = pd.to_numeric(
            edad,
            errors="coerce"
        ).dropna()

        if not edad.empty:

            conteo = (
                edad.value_counts()
                .sort_index()
                .reset_index()
            )

            conteo.columns = [
                "Edad",
                "conteo"
            ]

            fig = px.pie(
                conteo,
                names="Edad",
                values="conteo",
                title="Edad",
                hole=0.5,
                color_discrete_sequence=PALETA
            )

            fig.update_layout(
                template="plotly_white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key="edad",
                config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                    "doubleClick": False,
"showTips": False,
"staticPlot": True
                }
            )

# =========================
# SEXO
# =========================

with col3:

    cols_sexo = [
        c for c in df.columns
        if "Sexo" in c
    ]

    if cols_sexo:

        sexo = (
            df[cols_sexo]
            .bfill(axis=1)
            .iloc[:, 0]
        )

        sexo = sexo.astype(str)

        sexo = sexo[
            ~sexo.isin([
                "None",
                "nan",
                ""
            ])
        ]

        if not sexo.empty:

            conteo = (
                sexo.value_counts()
                .reset_index()
            )

            conteo.columns = [
                "Sexo",
                "conteo"
            ]

            fig = px.pie(
                conteo,
                names="Sexo",
                values="conteo",
                title="Sexo",
                hole=0.5,
                color_discrete_sequence=PALETA
            )

            fig.update_layout(
                template="plotly_white"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                key="sexo",
                config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                    "doubleClick": False,
"showTips": False,
"staticPlot": True
                }
            )

st.markdown("---")

graficar_por_sector(
    df,
    "",
    "Resultados"
)


# =========================
# FILTROS
# =========================

df["Sector"] = df["Sector"].astype(str)

df_primaria = df[df["Sector"].str.lower().str.strip() == "primaria"]
df_secundaria = df[df["Sector"].str.lower().str.strip() == "secundaria"]
df_prepa = df[df["Sector"].str.lower().str.contains("prepa")]
df_hogar = df[df["Sector"].str.lower().str.strip() == "hogar"]
df_publico = df[
    df["Sector"]
    .str.lower()
    .str.strip()
    == "público"
]


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
#  DATA LIMPIA PARA IA
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

# ahora sí IA limpia
insights = generar_insights(df_insights)

# =========================
#  FILTRO DE INSIGHTS 
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
