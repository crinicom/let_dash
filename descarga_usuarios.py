import aiohttp
import pandas as pd
import json
import asyncio
import streamlit as st




#PRIVADO
            
async def consulta_usuarios():
    url = "https://www.let.cl/wslet/consulta/usuariosConsultorExterno"
    headers = {
        #"authorization": "l37ch1l3_c0nsult0r"
        "authorization": st.secrets["api_users_auth"]
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                response_text = await response.text()
                with open("consulta_usuarios.txt", "w", encoding='cp1252') as file:
                    file.write(response_text)
                print("Success: Result saved to consulta_resultado.txt")
                return 200
            else:
                print("Failed:", response.status, await response.text())
                return 404
    
def carga_usuarios():
    try:
        # Abre el archivo y carga el contenido JSON
        with open("consulta_usuarios.txt", "r", encoding='cp1252') as file:
            data = json.load(file)

        # Transforma el JSON en un dataframe
        df = pd.DataFrame(data)
        #print("min fecha ingreso", df["fecha_ingreso"].min(), "\nmax fecha ingreso", df["fecha_ingreso"].max())
        return df
    except Exception as e:
        print("Algún error ocurrió:", e)
        return None

# Función asíncrona que ejecuta consulta() y luego carga el dataset
async def consulta_api_usuarios():
    # Espera a que la consulta se complete antes de proceder a cargar el dataset
    print("Consultando API Usuarios...")
    
    
    await consulta_usuarios()
    df = carga_usuarios()
    
    #print(df.head())
    return df

# PUBLICO

# Ejecuta la función main
def rescata_usuarios():
    #df = asyncio.run(consulta_api())
    loop = asyncio.get_event_loop()
    dfa = loop.run_until_complete(consulta_api_usuarios())
    
    return dfa
   

