#Este py es para que el cliente que se conecta a la API OData de ODK Central y convierte los datos en un DataFrame de Pandas,
# que luego usaremos en el dashboard de Streamlit.

# Importamos librerías necesarias
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
from config import *


def flatten_json(data, parent_key=''):
    """
    Esta función convierte JSON anidado en plano.

    Ejemplo:
    { "grp": { "edad": 10 } }
    →
    { "grp-edad": 10 }
    """

    items = []

    # Recorremos cada clave del JSON
    for key, value in data.items():

        # Creamos el nombre de la nueva columna
        new_key = f"{parent_key}-{key}" if parent_key else key

        # Si el valor es otro diccionario → seguimos desanidando
        if isinstance(value, dict):
            items.extend(flatten_json(value, new_key).items())

        else:
            # Si no es diccionario → guardamos el valor
            items.append((new_key, value))

    return dict(items)


def obtener_submissions():

    url = f"{ODK_URL}/v1/projects/{PROJECT_ID}/forms/{FORM_ID}.svc/Submissions"

    response = requests.get(
        url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),

        #IMPORTANTE: agregamos User-Agent para evitar bloqueos de Cloudflare
        headers={
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
    )

    # 🔍 DEBUG: mostramos status y respuesta cruda
    print("STATUS:", response.status_code)
    print("RESPUESTA RAW:", response.text[:500])  # solo primeros 500 caracteres


    # VALIDAMOS SI LA RESPUESTA ES EXITOSA
    if response.status_code != 200:
        print("ERROR: la API no respondió correctamente")
        return pd.DataFrame()


    # Intentamos convertir a JSON
    try:
        data = response.json()
    except Exception as e:
        print("ERROR al convertir a JSON:", e)
        return pd.DataFrame()


    # VALIDAMOS QUE EXISTA "value"
    if "value" not in data:
        print("ERROR: la respuesta no contiene 'value'")
        print("Respuesta completa:", data)
        return pd.DataFrame()


    registros = data["value"]

    # APLICAMOS EL FLATTEN
    registros_flat = []

    for registro in registros:
        registro_plano = flatten_json(registro)
        registros_flat.append(registro_plano)

    # Convertimos a DataFrame
    df = pd.DataFrame(registros_flat)

    return df