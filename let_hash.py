import streamlit as st
import pandas as pd
from descarga_st import rescata_dataset
from calcula_aux import aplicar_formulas_kpi, prueba
from grafica import grafica_atributo, grafica_atributo_mes, grafica_atributo_evolutivo
import os
import json

st.title('LET Inspecciones')

# Función para cargar los datos
def load_data(dataset_config=None):
    """
    Carga los datos según la configuración proporcionada.

    Args:
        dataset_config: Un diccionario que especifica qué dataset cargar.
                        Si es None, se usa la configuración por defecto.
    """
    if dataset_config:
        #st.write(f"Cargando datos para {dataset_config['corredora']}")
        
        dataset = rescata_dataset(dataset_config['compania'], dataset_config['corredora'])
    else:
        dataset = rescata_dataset()
    prueba()
    
    try:
        df = aplicar_formulas_kpi(dataset)
    except Exception as e:
        print("🔴 Error:", e)
        st.error("Error al aplicar fórmulas KPI. Mira el log para detalles.")
        return None
    return df

# Obtener el hash ingresado por el usuario
hash_ingresado = st.text_input("Ingrese el hash de la compania:")
#hash_ingresado = "region1"
# Cargar la configuración de los datasets desde st.secrets
try:
    dataset_config = st.secrets.get("dataset_config")
    # Determinar qué dataset cargar basado en el hash ingresado
    if hash_ingresado in dataset_config:
        st.write(f"Cargando datos para {dataset_config[hash_ingresado]["corredora"]}")
        #st.write(f"{dataset_config}, {dataset_config[hash_ingresado]}")
        #st.write(f"{dataset_config[hash_ingresado]['compania']}, {dataset_config[hash_ingresado]['corredora']}")
        df = load_data(dataset_config[hash_ingresado])
        #st.write(f"{df.head()}")
    else:
        st.error("Hash no válido. Por favor, ingrese un hash válido.")
        st.stop()

    if df is None:
        st.stop()
except Exception as e:
    st.error(f"Ocurrió un error al cargar los datos: {e}")
    config_str= os.environ.get("dataset_config__"+hash_ingresado)
    st.write(f"{config_str=}")
    if config_str != None:
        dataset_config = json.loads(config_str)    
    else:
        st.error("No se encontró la configuración del dataset.")
        st.stop()
    

    if dataset_config != None:
        st.write(f"Cargando datos para {dataset_config["corredora"]}")
        df = load_data({"compania":dataset_config["compania"], "corredora":dataset_config["corredora"]})
    else:
        st.error("Hash no válido. Por favor, ingrese un hash válido.")
        st.stop()

    if df is None:
        st.stop()
# Determinar qué dataset cargar basado en el hash ingresado


# Mostrar información sobre los datos cargados
data_load_state = st.text("Datos desde: " + str(df["fecha_emision"].min()) + " hasta: " + str(df["fecha_emision"].max()))

# Mostrar los gráficos
tab1, tab2 = st.tabs(["📅 Mes actual", "📈 Evolutivo"])

with tab1:
    #st.subheader('Tiempo de respuesta de backoffice')
    #plot11 = grafica_atributo(df, 'KPI resp BO DOM CEILING OK', "Tiempo de backoffice, inspecciones a domicilio")
    #st.pyplot(plot11.get_figure())

    st.subheader('Tiempo de respuesta de backoffice último mes cerrado')
    plot12 = grafica_atributo_mes(df, 'KPI resp BO DOM CEILING OK', "Tiempo de backoffice, inspecciones a domicilio")
    st.pyplot(plot12.get_figure())

    st.subheader('Tiempo de respuesta de backoffice último mes cerrado')
    plot13 = grafica_atributo_mes(df, 'resp BO GRAL CEILING OK HMS', "Tiempo de backoffice, general")
    st.pyplot(plot13.get_figure())

with tab2:
    st.subheader('Evolución del tiempo de respuesta por mes')
    plot21 = grafica_atributo_evolutivo(df, 'KPI resp BO DOM CEILING OK',
                                         "Evolución del % de respuestas ≤ 30 min, domicilio")
    if plot21:
        st.pyplot(plot21.get_figure())

#streamlit run let_hash.py

# pipreqs . --encoding=utf-8 --ignore .venv,__pychache__ <- para crear el requirements.txt
# git add .
# git commit -m "avances"
# git push origin main