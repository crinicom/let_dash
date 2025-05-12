import requests
import pandas as pd
import json

async def consulta():
    url = "https://www.let.cl/wslet/consulta/reporteConsultorExterno"
    headers = {
        "authorization": "l37ch1l3_c0nsult0r"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        with open("consulta_resultado.txt", "w") as file:
            file.write(response.text)
        print("Success: Result saved to consulta_resultado.txt")
        return 200
    else:
        print("Failed:", response.status_code, response.text)
        return 404

def carga_dataset():
    try:
        # Abre el archivo y carga el contenido JSON
        with open("consulta_resultado.txt", "r", encoding='cp1252') as file:
            data = json.load(file)

        # Transforma el JSON en un dataframe
        df = pd.DataFrame(data)
        #display(df.columns)
        print("min fecha ingreso", df["fecha_ingreso"].min(), "\nmax fecha ingreso", df["fecha_ingreso"].max())
        return df
    except:
        print("algun error ocurrió")
        return None

consulta()    
prueba = carga_dataset()
print(prueba.head())