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
        "fecha_inicial": "2025-04-09",
        "fecha_final": "2025-04-10",
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
        print("min fecha emisión", df["fecha_emision"].min(), "\nmax fecha emisión", df["fecha_emision"].max())
        return df
    except Exception as e:
        print("Algún error ocurrió:", e)
        return None
    

# Función asíncrona que ejecuta consulta() y luego carga el dataset
async def consulta_api(compania, corredora):
    # Espera a que la consulta se complete antes de proceder a cargar el dataset
    print(f"Consultando API... compania={compania}, corredora={corredora}")
    
    await consulta(compania=compania, corredora=corredora)
    #await consulta_usuarios()
    df = await carga_dataset()
    
    #print(df.head())
    return df

# PUBLICO

# Ejecuta la función main
async def rescata_dataset(compania="9", corredora="SANTANDER"):
    #df = asyncio.run(consulta_api())
    loop = asyncio.get_event_loop()
    #df = loop.run_until_complete(consulta_api(compania=compania, corredora=corredora))
    df = await consulta_api(compania=compania, corredora=corredora)
    return df
    

