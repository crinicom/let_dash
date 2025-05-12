import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from descarga import rescata_dataset
import nest_asyncio
nest_asyncio.apply()


def extrae_dataset():
    df = rescata_dataset()
    return df

# Ejecutar solo si dataset no existe o está vacío
try:
    if dataset.empty:
        print("Dataset está vacío. Recalculando...")
        dataset = extrae_dataset()
except NameError:
    print("Dataset no existe. Recalculando...")
    dataset = extrae_dataset()

print(dataset.head())




















# OBSOLETO
def generar_tiempo_respuesta(mes):
    """
    Genera tiempos de respuesta según el histograma dado, con variaciones por mes.
    Septiembre tendrá un 30% más de tiempo de respuesta.
    """
    # Definir pesos base del histograma original
    pesos = [
        0.620,  # 0-30 min
        0.059,  # 30-60 min
        0.037,  # 60-90 min
        0.020,  # 90-120 min
        0.028,  # 120-150 min
        0.018,  # 150-180 min
        0.010,  # 180-210 min
        0.016,  # 210-240 min
        0.010,  # 240-270 min
        0.012,  # 270-300 min
        0.003,  # 300-330 min
        0.009,  # 330-360 min
        0.007,  # 360-390 min
        0.004,  # 390-420 min
        0.003,  # 420-450 min
        0.002,  # 450-480 min
        0.003,  # 480-510 min
        0.139,  # 510+ min
    ]
    
    # Rangos de tiempo en minutos
    rangos = [
        (0, 30), (30, 60), (60, 90), (90, 120), (120, 150), 
        (150, 180), (180, 210), (210, 240), (240, 270), (270, 300),
        (300, 330), (330, 360), (360, 390), (390, 420), (420, 450),
        (450, 480), (480, 510), (510, 1440)
    ]
    
    # Factor de ajuste para septiembre (30% más lento)
    factor_mes = 1.3 if mes == 9 else 1.0
    
    # Seleccionar rango basado en los pesos
    indice = np.random.choice(len(rangos), p=pesos)
    rango = rangos[indice]
    
    # Generar tiempo dentro del rango, ajustado por factor de mes
    tiempo_base = np.random.uniform(rango[0], rango[1])
    tiempo = tiempo_base * factor_mes
    
    return timedelta(minutes=tiempo)

def generar_dataset():
    # Inicializar dataset
    datos = []
    
    # Generar 10,000 casos
    for id_caso in range(1, 10001):
        # Generar fecha aleatoria en 2024
        mes = np.random.randint(1, 13)
        dia = np.random.randint(1, 29)  # Usando 28 para simplicidad
        fecha = datetime(2024, mes, dia)
        
        # Generar tiempo de respuesta
        tiempo_respuesta = generar_tiempo_respuesta(mes)
        
        datos.append({
            'ID caso': id_caso,
            'Fecha': fecha.strftime('%d/%m/%Y'),
            'Tiempo inspección-respuesta (min)': tiempo_respuesta.total_seconds() / 60
        })
    
    # Convertir a DataFrame
    df = pd.DataFrame(datos)
    
    # Guardar como CSV
    #df.to_csv('tiempos_inspeccion_respuesta_2024.csv', sep=';', index=False)
    
    # Imprimir estadísticas por mes
    print("Estadísticas por mes:")
    estadisticas_mes = df.groupby(pd.to_datetime(df['Fecha'], format='%d/%m/%Y').dt.month)['Tiempo inspección-respuesta (min)'].agg(['mean', 'median'])
    print(estadisticas_mes)
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')

    

    # Convertir la fecha a datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'], format='%d/%m/%Y')

    # Crear bins de tiempo
    tiempo_bins = [0, 30, 60, 120, 180, 240, 300, 360, 420, 480, np.inf]
    tiempo_labels = ['0-30 min', '30-60 min', '1-2 h', '2-3 h', '3-4 h', 
                    '4-5 h', '5-6 h', '6-7 h', '7-8 h', '8+ h']

    # Añadir columna de bins de tiempo
    df['Tiempo Bin'] = pd.cut(df['Tiempo inspección-respuesta (min)'], 
                            bins=tiempo_bins, 
                            labels=tiempo_labels)

    # Análisis de distribución general
    distribucion_general = df['Tiempo Bin'].value_counts(normalize=True) * 100
    print("Distribución General de Tiempos de Respuesta:")
    print(distribucion_general)

    # Análisis por mes
    df['Mes'] = df['Fecha'].dt.month
    

    return df