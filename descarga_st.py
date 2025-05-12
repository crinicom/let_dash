import aiohttp
import pandas as pd
import json
import asyncio
import streamlit as st
import datetime as dt




#PRIVADO

async def consulta(compania, corredora):
    url = "https://www.let.cl/wslet/consulta/reporteConsultorExterno"
    headers = {
        #"authorization": "l37ch1l3_c0nsult0r"
        "authorization": st.secrets["api_auth"],
        "fecha_inicial": "2024-03-01",
        "fecha_final": "2025-05-10",
        "compania": compania, #"9",
        "corredora": corredora #"SANTANDER"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_text = await response.text()
                with open("consulta_resultado.txt", "w", encoding='cp1252') as file:
                    file.write(f"{dt.datetime.now()}\n{response_text}")
                print("Success: Result saved to consulta_resultado.txt", dt.datetime.now())
                return 200
            else:
                print("Failed:", response.status, await response.text())
                return 404
            


async def carga_dataset():
    try:
        # Abre el archivo y carga el contenido JSON
        with open("consulta_resultado.txt", "r", encoding='cp1252') as file:
            next(file) #salteo la primera fila que tengo con timestamp de extracción
            data = json.load(file)

        # Transforma el JSON en un dataframe
        df = pd.DataFrame(data)
        print(df.columns)
        df["fecha_emision"] = pd.to_datetime(df["fecha_emision"], format="%d-%m-%Y") 
        print("min fecha emisión", df["fecha_emision"].min(), "\nmax fecha emisión", df["fecha_emision"].max())
        return df
    except Exception as e:
        print("Algún error ocurrió:", e)
        return None

async def dataset_cargado(hs_validez=4): #No la hago asincrónica porque no es necesario
    # Verifica si el archivo existe y tiene contenido cargado dentro de las 4 hs anteriores
    try:
        # Abre el archivo y carga el contenido JSON
        with open("consulta_resultado.txt", "r", encoding='cp1252') as file:
            first_line = file.readline().strip()  # Lee la primera línea y elimina espacios en blanco
            timestamp = dt.datetime.strptime(first_line, "%Y-%m-%d %H:%M:%S.%f")  # Convierte a formato timestamp
            
            file.close() #cierra el archivo
        # Transforma el JSON en un dataframe
        if (dt.datetime.now() - timestamp).total_seconds() < hs_validez * 3600:
            return True
        else:
            print(f"El dataset tiene más de {hs_validez} horas de antigüedad. Consultando API...")
            return False
    except Exception as e:
        print("Dataset de OIs no disponible", e)
        return False

# Función asíncrona que ejecuta consulta() y luego carga el dataset
async def consulta_api(compania, corredora, validez):
    # Espera a que la consulta se complete antes de proceder a cargar el dataset
    print(f"Consultando API... compania={compania}, corredora={corredora}")
    ds_cargado = await dataset_cargado(validez) #999 para que no vuelva a cargar verifico si el dataset ya está cargado antes de consultar
    #ds_cargado = False #forzar a que siempre se consulte la API (para pruebas)
    if ds_cargado:
        print("Dataset ya cargado, no se vuelve a consultar")
    else: 
        await consulta(compania=compania, corredora=corredora)
    #await consulta_usuarios()
    
    df = await carga_dataset()
    
    #print(df.head())
    return df

# PUBLICO

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        # Este camino puede ser necesario en entornos como Jupyter o Streamlit
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(coro)
    else:
        return loop.run_until_complete(coro)


# Ejecuta la función main
def rescata_dataset(compania="9", corredora="SANTANDER"):
    #df = asyncio.run(consulta_api())
    #loop = asyncio.get_event_loop()
    #df = loop.run_until_complete(consulta_api(compania=compania, corredora=corredora))
    #df = await consulta_api(compania=compania, corredora=corredora)    
    #df = asyncio.run(consulta_api(compania=compania, corredora=corredora))
    df = run_async(consulta_api(compania, corredora, 999))
    return df
    