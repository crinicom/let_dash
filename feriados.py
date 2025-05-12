import requests
import pandas as pd

def obtener_feriados():
    # URL del API
    url = "https://api.boostr.cl/feriados/en.json"

    # Obtener los datos desde la API
    response = requests.get(url)
    data = response.json()

    # Extraer la parte relevante del JSON
    feriados = data['data']

    # Crear el DataFrame
    df = pd.DataFrame(feriados)

    # Mostrar los primeros registros
    print(df.head())
    return df