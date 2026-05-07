import streamlit as st
import pandas as pd
import plotly.express as px

from collections import Counter

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
# CONFIG
# =========================

st.set_page_config(
    page_title="Percepción Ambiental",
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
COLOR_MORADO = "#7E57C2"

PALETA = [
    COLOR_PRIMARIO,
    COLOR_SECUNDARIO,
    COLOR_EXITO,
    COLOR_ALERTA,
    COLOR_MORADO
]

# =========================
# CSS
# =========================

st.markdown("""
<style>

/* TEXTO GENERAL */
html, body, [class*="css"] {
    font-size: 18px !important;
}

/* KPI */
div[data-testid="metric-container"] {
    background-color: #f8f9fa;
    border: 2px solid #e6e6e6;
    padding: 25px;
    border-radius: 16px;
    text-align: center;
}

div[data-testid="metric-container"] label {
    font-size: 22px !important;
    font-weight: bold !important;
}

[data-testid="stMetricValue"] {
    font-size: 55px !important;
    font-weight: bold !important;
    color: #1565C0 !important;
}

/* TITULOS */
h1 {
    font-size: 48px !important;
}

h2 {
    font-size: 36px !important;
    margin-top: 20px !important;
}

h3 {
    font-size: 28px !important;
}

</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================

col1, col2 = st.columns([1, 6])

with col1:
    st.image("logo.jpeg", width=180)

with col2:
    st.title("Dashboard Percepción Ambiental")
    st.caption(
        "Encuesta de percepción sobre residuos y servicios ambientales"
    )

st.markdown("---")

# =========================
# OBTENER DATA
# =========================

PROJECT_ID_PERCEPCION = "4"

FORM_ID_PERCEPCION = "Encuesta%20de%20Percepcion"

df = obtener_submissions(
    PROJECT_ID_PERCEPCION,
    FORM_ID_PERCEPCION
)

# =========================
# LIMPIEZA
# =========================

df = filtrar_columnas_relevantes(df)

df = df.rename(columns=COLUMN_MAPPING)

REGIONES = {
    "r1": "Huitzizilapan",
    "r2": "Tlalmimilolpan",
    "r3": "Atarasquillo",
    "r4": "Ameyalco",
    "r5": "Lerma",
    "r6": "Tultepec",
    "r7": "Xochicuautla",
    "r8": "Parque Industrial"
}

df["Region"] = df["Region"].replace(REGIONES)

# =========================
# LIMPIEZA VISUAL
# =========================

NIVELES_EDUCATIVOS = {
    "secundaria": "Secundaria",
    "licenciatura": "Licenciatura",
    "preparatoria": "Bachillerato",
    "primaria": "Primaria",
    "prefiero_no": "Reservado"
}

df["Nivel educativo"] = df[
    "Nivel educativo"
].replace(NIVELES_EDUCATIVOS)

SEXO = {
    "femenino": "Femenino",
    "masculino": "Masculino"
}

df["Sexo"] = df["Sexo"].replace(SEXO)

RESIDUOS = {
    "organicos": "Orgánicos",
    "plasticos": "Plásticos",
    "carton_papel": "Cartón/Papel",
    "sanitarios": "Sanitarios",
    "vidrio": "Vidrio",
    "metalicos": "Metálicos",
    "electronicos": "Electrónicos",
    "otro": "Otros"
}

RESPUESTAS = {
    "si": "Sí",
    "no": "No",
    "nosabe": "Desconoce"
}

COLUMNAS_RESPUESTAS = [
    "¿Hay tiraderos clandestinos?",
    "¿Es común la quema de basura?",
    "¿Separan residuos en el hogar?",
    "¿La comunidad colabora?"
]

for col in COLUMNAS_RESPUESTAS:

    if col in df.columns:

        df[col] = df[col].replace(RESPUESTAS)

# =========================
# VALIDACIÓN
# =========================

if df.empty:
    st.warning("Sin datos disponibles")
    st.stop()

# =========================
# KPIs
# =========================

def calcular_porcentaje_si(df, columna):

    if columna not in df.columns:
        return 0

    serie = df[columna].astype(str)

    serie = serie[
        ~serie.isin(["nan", "None", "", "Sin dato"])
    ]

    if len(serie) == 0:
        return 0

    si = serie.str.lower().str.contains("si|sí").sum()

    return int((si / len(serie)) * 100)

edad_promedio = pd.to_numeric(
    df["Edad"],
    errors="coerce"
).mean()

separacion = calcular_porcentaje_si(
    df,
    "¿Separan residuos en el hogar?"
)

confianza = pd.to_numeric(
    df["Confianza servicio municipal"],
    errors="coerce"
).mean()

# =========================
# KPIs RENDER
# =========================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total encuestas",
    len(df)
)

col2.metric(
    "Edad promedio",
    int(edad_promedio)
)

col3.metric(
    "Separan residuos",
    f"{separacion}%"
)

col4.metric(
    "Confianza servicio",
    f"{round(confianza,1)} / 5"
)

st.markdown("---")

# =========================
# DEMOGRAFÍA
# =========================

st.markdown("## Demografía")

col1, col2, col3 = st.columns(3)

# SEXO
with col1:

    conteo = df["Sexo"].value_counts().reset_index()

    conteo.columns = ["Sexo", "conteo"]

    fig = px.pie(
        conteo,
        names="Sexo",
        values="conteo",
        title="Sexo",
        hole=0.5,
        color_discrete_sequence=[
            COLOR_PRIMARIO,
            COLOR_SECUNDARIO
        ]
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# REGIÓN
with col2:

    conteo = df["Region"].value_counts().reset_index()

    conteo.columns = ["Region", "conteo"]

    fig = px.bar(
        conteo,
        x="Region",
        y="conteo",
        color="Region",
        title="Región territorial",
        color_discrete_sequence=PALETA,
        text="conteo",
        template="plotly_white"
    )

    fig.update_layout(
        xaxis_tickangle=-20,
        showlegend=False,
        height=420
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# NIVEL EDUCATIVO
with col3:

    conteo = df["Nivel educativo"].value_counts().reset_index()

    conteo.columns = [
        "Nivel educativo",
        "conteo"
    ]

    fig = px.pie(
        conteo,
        names="Nivel educativo",
        values="conteo",
        title="Nivel educativo",
        hole=0.5,
        color_discrete_sequence=PALETA
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.markdown("---")

# =========================
# MANEJO DE RESIDUOS
# =========================

st.markdown("## Manejo de residuos")

col1, col2 = st.columns(2)

# SEPARACIÓN
with col1:

    conteo = df[
        "¿Separan residuos en el hogar?"
    ].value_counts().reset_index()

    conteo.columns = [
        "Respuesta",
        "conteo"
    ]

    fig = px.pie(
        conteo,
        names="Respuesta",
        values="conteo",
        title="Separación de residuos",
        hole=0.5,
        color="Respuesta",
        color_discrete_map={
            "Sí": COLOR_PRIMARIO,
            "No": COLOR_SECUNDARIO
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# RESIDUOS
with col2:

    residuos = []

    for fila in df[
        "Residuos más frecuentes"
    ].dropna():

        partes = str(fila).replace(",", " ").split()

        partes = [
            RESIDUOS.get(p, p)
            for p in partes
        ]

        residuos.extend(partes)

    conteo = pd.DataFrame(
        Counter(residuos).items(),
        columns=["Residuo", "conteo"]
    )

    conteo = conteo.sort_values(
        by="conteo",
        ascending=False
    )

    fig = px.bar(
        conteo,
        x="Residuo",
        y="conteo",
        color="Residuo",
        title="Residuos más frecuentes",
        color_discrete_sequence=PALETA,
        text="conteo",
        template="plotly_white"
    )

    fig.update_layout(
        showlegend=False,
        height=420
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.markdown("---")

# =========================
# PROBLEMÁTICAS
# =========================

st.markdown("## Problemáticas ambientales")

col1, col2 = st.columns(2)

# TIRADEROS
with col1:

    conteo = df[
        "¿Hay tiraderos clandestinos?"
    ].value_counts().reset_index()

    conteo.columns = [
        "Respuesta",
        "conteo"
    ]

    fig = px.pie(
        conteo,
        names="Respuesta",
        values="conteo",
        title="Tiraderos clandestinos",
        hole=0.5,
        color="Respuesta",
        color_discrete_map={
            "Sí": COLOR_PELIGRO,
            "No": COLOR_EXITO,
            "Desconoce": COLOR_ALERTA
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# QUEMA
with col2:

    conteo = df[
        "¿Es común la quema de basura?"
    ].value_counts().reset_index()

    conteo.columns = [
        "Respuesta",
        "conteo"
    ]

    fig = px.pie(
        conteo,
        names="Respuesta",
        values="conteo",
        title="Quema de basura",
        hole=0.5,
        color="Respuesta",
        color_discrete_map={
            "Sí": COLOR_PELIGRO,
            "No": COLOR_EXITO,
            "Desconoce": COLOR_ALERTA
        }
    )

    fig.update_layout(
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.markdown("---")

# =========================
# SERVICIO MUNICIPAL
# =========================

st.markdown("## Servicio municipal")

col1, col2 = st.columns(2)

# CALIFICACIÓN
with col1:

    promedio_servicio = round(
        pd.to_numeric(
            df["Calificación servicio"],
            errors="coerce"
        ).mean(),
        1
    )

    st.metric(
        "Calificación promedio",
        f"{promedio_servicio} / 5"
    )

    conteo = df[
        "Calificación servicio"
    ].value_counts().sort_index()

    fig = px.bar(
        x=["1", "2", "3", "4", "5"],
        y=conteo.values,
        text=conteo.values,
        color=["1", "2", "3", "4", "5"],
        color_discrete_sequence=PALETA,
        template="plotly_white"
    )

    fig.update_layout(
        height=400,
        margin=dict(
            t=80,
            b=40,
            l=40,
            r=20
        ),
        showlegend=False,
        xaxis_title="Calificación",
        yaxis_title="Respuestas"
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# CONFIANZA
with col2:

    promedio_confianza = round(
        pd.to_numeric(
            df["Confianza servicio municipal"],
            errors="coerce"
        ).mean(),
        1
    )

    st.metric(
        "Confianza promedio",
        f"{promedio_confianza} / 5"
    )

    conteo = df[
        "Confianza servicio municipal"
    ].value_counts().sort_index()

    fig = px.bar(
        x=[
            "Muy baja",
            "Baja",
            "Regular",
            "Alta",
            "Muy alta"
        ],
        y=conteo.values,
        text=conteo.values,
        color=[
            "Muy baja",
            "Baja",
            "Regular",
            "Alta",
            "Muy alta"
        ],
        color_discrete_sequence=PALETA,
        template="plotly_white"
    )

    fig.update_layout(
        height=400,
        margin=dict(
            t=80,
            b=40,
            l=40,
            r=20
        ),
        showlegend=False,
        xaxis_title="Nivel de confianza",
        yaxis_title="Respuestas"
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

st.markdown("---")

# =========================
# PROBLEMAS ASOCIADOS
# =========================

st.markdown("## Problemas asociados a la basura")

problemas = []

for fila in df[
    "Problemas asociados basura"
].dropna():

    partes = str(fila).replace(",", " ").split()

    problemas.extend(partes)

conteo_problemas = pd.DataFrame(
    Counter(problemas).items(),
    columns=["Problema", "conteo"]
)

conteo_problemas = conteo_problemas.sort_values(
    by="conteo",
    ascending=False
)

fig_problemas = px.bar(
    conteo_problemas,
    x="conteo",
    y="Problema",
    orientation="h",
    text="conteo",
    color="Problema",
    color_discrete_sequence=PALETA,
    title="Problemas asociados",
    template="plotly_white"
)

fig_problemas.update_layout(
    height=500,
    yaxis_title="",
    xaxis_title="Número de respuestas",
    showlegend=False
)

fig_problemas.update_traces(
    textposition="outside",
    cliponaxis=False
)

st.plotly_chart(
    fig_problemas,
    use_container_width=True
)

# =========================
# MAPA
# =========================

st.markdown("---")
st.markdown("## Ubicación de encuestas")

df_mapa = df.copy()

df_mapa["lat"] = df_mapa["Ubicacion"].apply(
    lambda x: x[1] if isinstance(x, list) else None
)

df_mapa["lon"] = df_mapa["Ubicacion"].apply(
    lambda x: x[0] if isinstance(x, list) else None
)

df_mapa = df_mapa.dropna(
    subset=["lat", "lon"]
)

st.map(
    df_mapa[["lat", "lon"]],
    zoom=11
)

# =========================
# DATOS
# =========================

with st.expander("Ver datos completos"):

    st.dataframe(
        df,
        use_container_width=True
    )