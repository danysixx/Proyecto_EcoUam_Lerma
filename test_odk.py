# Importamos la función que creamos en odk_client.py
# Esta función se conecta a ODK y devuelve los datos en un DataFrame
from odk_client import obtener_submissions


# Llamamos a la función y guardamos el resultado en la variable df
# df significa DataFrame (tabla de datos)
df = obtener_submissions()


# Imprimimos las primeras 5 filas del DataFrame
# head() sirve para ver una muestra de los datos
print("Primeras filas del DataFrame:")
print(df.head())


# Imprimimos las columnas del DataFrame
# Esto nos permite ver todas las preguntas de la encuesta
print("\nColumnas disponibles:")
print(df.columns)


# Imprimimos el número total de registros
# Esto nos dice cuántas encuestas hay
print("\nNúmero total de registros:")
print(len(df))