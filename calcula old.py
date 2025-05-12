import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np



# Leer el dataset
def grafica_meses(df_input):
    
    df = df_input #pd.read_csv('tiempos_inspeccion_respuesta_2024.csv', sep=';')
    distribucion_por_mes = df.groupby('Mes')['Tiempo Bin'].value_counts(normalize=True).unstack() * 100
    print("\nDistribución de Tiempos de Respuesta por Mes (%):")
    print(distribucion_por_mes)
    # Tiempo promedio por mes
    tiempo_promedio_por_mes = df.groupby('Mes')['Tiempo inspección-respuesta (min)'].mean()
    print("\nTiempo Promedio de Respuesta por Mes:")
    print(tiempo_promedio_por_mes)


    # Visualización de distribución por mes
    plt.figure(figsize=(15, 8))
    plot_meses = distribucion_por_mes.plot(kind='bar', stacked=True)
    plt.title('Distribución de Tiempos de Respuesta por Mes')
    plt.xlabel('Mes')
    plt.ylabel('Porcentaje de Casos')
    plt.legend(title='Tiempo de Respuesta', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.show()
    plt.close()
    return plot_meses

def grafica_ultimo_mes(df_input):
        # Filtrar los datos para obtener solo el mes de diciembre
    df = df_input
    diciembre_data = df[df['Fecha'].dt.month == 12]

    # Calcular la distribución de tiempos de respuesta en diciembre
    distribucion_diciembre = diciembre_data['Tiempo Bin'].value_counts(normalize=True) * 100

    # Visualizar la distribución de tiempos de respuesta en diciembre
    plt.figure(figsize=(10, 6))
    plot_ultimo_mes = sns.barplot(x=distribucion_diciembre.index, y=distribucion_diciembre.values, palette='viridis')
    plt.title('Distribución de Tiempos de Respuesta en Diciembre')
    plt.xlabel('Tiempo de Respuesta')
    plt.ylabel('Porcentaje de Casos')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Mostrar la distribución en formato de tabla
    print("Distribución de Tiempos de Respuesta en Diciembre (%):")
    print(distribucion_diciembre)
    return plot_ultimo_mes
