# Importamos pandas
import pandas as pd


def limpiar_datos(df):
    """
    Limpia el DataFrame eliminando ruido y preparando los datos para análisis.
    """

    # Copiamos el DataFrame original para no modificarlo directamente
    df_clean = df.copy()

    # Eliminamos filas completamente vacías
    df_clean = df_clean.dropna(how="all")

    # Eliminamos columnas que son metadatos (no útiles para análisis)
    columnas_utiles = [
        col for col in df_clean.columns
        if not col.startswith("_") and not col.startswith("__")
    ]

    df_clean = df_clean[columnas_utiles]

    # Rellenamos valores nulos con texto controlado
    df_clean = df_clean.fillna("Sin dato")

    return df_clean


def generar_insights(df):
    """
    Genera insights automáticos a partir de los datos limpios.
    """

    insights = []

    # Limpiamos los datos antes de analizarlos
    df = limpiar_datos(df)

    # Total de registros
    total = len(df)
    insights.append(f"Total de registros analizados: {total}")

    # Analizamos columnas categóricas
    for col in df.columns:

        # Solo analizamos columnas tipo texto
        if df[col].dtype == "object":

            # Contamos valores
            conteo = df[col].value_counts()

            # Valor más frecuente
            top_valor = conteo.idxmax()
            top_count = conteo.max()

            insights.append(
                f"La categoría más frecuente en '{col}' es '{top_valor}' con {top_count} registros."
            )

            # Detectamos valores "Sin dato"
            if "Sin dato" in conteo:
                vacios = conteo["Sin dato"]
                insights.append(
                    f"La variable '{col}' tiene {vacios} registros sin información."
                )

    return insights

# =========================
# SECCIÓN: EXCLUIR DATOS NO NECESARIOS
# =========================
def filtrar_columnas_relevantes(df):
    """
    Filtra columnas útiles para análisis del dashboard.
    """

    columnas_excluir = [
        "_id",
        "_system",
        "meta",
        "end",
        "today"
    ]

    columnas_utiles = []

    for col in df.columns:

        # Excluir metadata
        if any(col.startswith(pref) for pref in columnas_excluir):
            continue

        # Excluir columnas vacías (más del 80% vacío)
        porcentaje_vacio = df[col].isna().mean()

        if porcentaje_vacio > 0.8:
            continue

        columnas_utiles.append(col)

    return df[columnas_utiles]

