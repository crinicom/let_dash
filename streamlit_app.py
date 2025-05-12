import streamlit as st
import pandas as pd
import numpy as np
from streamlit_auth import add_auth
#from extrae import generar_dataset
from descarga_st import rescata_dataset
from calcula_aux import aplicar_formulas_kpi, prueba
from calcula import grafica_meses, grafica_ultimo_mes
from grafica import grafica_atributo, grafica_atributo_mes, grafica_atributo_evolutivo


st.title('LET Inspecciones')


DATE_COLUMN = 'date/time'
#DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            #'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

#@st.cache_data
def load_data(nrows):
     # Ejecutar generación de dataset
    dataset = rescata_dataset() #generar_dataset()
    prueba()
    try:
        #print("entro al try")
        df = aplicar_formulas_kpi(dataset)
        #print(df.columns)
    except Exception as e:
        print("entro al except")
        print("🔴 Error:", e)
        traceback.print_exc()
        st.error("Error al aplicar fórmulas KPI")
        return None
    #df = pd.read_csv(DATA_URL, nrows=nrows)
    #st.write(df.columns)
    return df


#print("pre login", st.experimental_user.is_logged_in)
#add_auth()

st.write("Congrats, you are logged in!")
#st.write('the email of the user is ' + str(st.session_state.login_user["email"]))

data_load_state = st.text('Loading data...')
df = load_data(10000)

data_load_state.text("Done! (using st.cache)")

data_load_state.text("Data desde: " + str(df["fecha_emision"].min()) + " hasta: " + str(df["fecha_emision"].max()))

tab1, tab2 = st.tabs(["📅 Mes actual", "📈 Evolutivo"])

#st.text(df.columns.T)
#if st.checkbox('Show raw data'): #FUNCIONA (pero no lo quiero)!!!
    #st.subheader('Raw data')
    #st.write(data)
with tab1:
    st.subheader('Tiempo de respuesta de backoffice')
    plot0 = grafica_atributo(df,'KPI resp BO DOM CEILING OK', "Tiempo de backoffice, inspecciones a domicilio" )
    st.pyplot(plot0.get_figure())

    st.subheader('Tiempo de respuesta de backoffice último mes cerrado')
    plot1 = grafica_atributo_mes(df,'KPI resp BO DOM CEILING OK', "Tiempo de backoffice, inspecciones a domicilio" )
    st.pyplot(plot1.get_figure())

with tab2:
    st.subheader('Evolución del tiempo de respuesta por mes')
    plot_evo = grafica_atributo_evolutivo(df, 'KPI resp BO DOM CEILING OK', "Evolución del % de respuestas ≤ 30 min")
    if plot_evo:
        st.pyplot(plot_evo.get_figure())#plot = grafica_meses(df)
    #st.pyplot(plot.get_figure())
    #hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
    #st.bar_chart(hist_values)

    # Some number in the range 0-23
    #hour_to_filter = st.slider('hour', 0, 23, 17)
    #filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

    st.subheader('Tiempos de respuesta último mes')
    #plot1 = grafica_ultimo_mes(df)
    #st.pyplot(plot1.get_figure())

    # streamlit run streamlit_app.py  