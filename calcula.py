import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# kpi_formulas_aplicadas.py

import pandas as pd
import numpy as np
from math import ceil
from datetime import datetime

# =====================
# FUNCIONES AUXILIARES
# =====================

def to_datetime_safe(val):
    try:
        if val in ["NULL", "", None, np.nan]:
            return pd.NaT
        return pd.to_datetime(val, dayfirst=False, errors='coerce')
    except:
        return pd.NaT

def safe_subtract_days(date1, date2):
    if pd.isna(date1) or pd.isna(date2):
        return np.nan
    return (date1 - date2).days

def redondear_5_minutos(valor):
    if valor in [np.nan, 'error'] or pd.isna(valor):
        return np.nan
    try:
        minutos = valor * 24 * 60
        minutos_redondeados = ceil(minutos / 5) * 5
        return minutos_redondeados / (24 * 60)
    except:
        return np.nan

def bucket_15_mas(x):
    if x in ['error', np.nan]:
        return x
    try:
        if x >= 15:
            return '15+'
        return x
    except:
        return 'error'

# ============================
# APLICACIÓN DE KPI EN DATOS
# ============================
# Informe Autoinspeccion     79
#Informe Normal             77
#Informe asistida            2

def aplicar_formulas_kpi(df):
    # Conversión de columnas a datetime
    for col in ['fecha_emision', 'fecha_entrega_informe', 'fecha_inicio_inspeccion']:
        df[col] = df[col].apply(to_datetime_safe)

    # === KPI RESP BO ===
    def calcular_resp_bo(row):
        if pd.isna(row['fecha_entrega_informe']):
            return np.nan
        if row['informe_final'] == "Informe Normal":
            return safe_subtract_days(row['fecha_inicio_inspeccion'], row['fecha_emision'])
        else:
            return safe_subtract_days(row['fecha_entrega_informe'], row['fecha_emision'])

    df['kpi_resp_bo'] = df.apply(calcular_resp_bo, axis=1)
    df['kpi_resp_bo_ceiling'] = df['kpi_resp_bo'].apply(lambda x: redondear_5_minutos(x) if isinstance(x, (int, float)) else x)
    df['kpi_resp_bo_bucket'] = df['kpi_resp_bo'].apply(bucket_15_mas)

    # === KPI DÍAS EN COORDINAR (DC y DH) ===
    def dias_en_coordinar(row, tipo):
        if row['informe_final'] != tipo:
            return np.nan
        if pd.isna(row['fecha_inicio_inspeccion']) or pd.isna(row['fecha_emision']):
            return np.nan
        return safe_subtract_days(row['fecha_inicio_inspeccion'], row['fecha_emision'])

    df['kpi_dias_en_coordinar_dc'] = df.apply(lambda r: dias_en_coordinar(r, 'Informe Normal'), axis=1)
    df['kpi_dias_en_coordinar_dh'] = df.apply(lambda r: dias_en_coordinar(r, 'Informe asistida'), axis=1)

    # === KPI DÍAS EN INSPECCIONAR (DC y DH) ===
    def dias_en_inspeccionar(row, tipo):
        if row['informe_final'] != tipo:
            return np.nan
        if pd.isna(row['fecha_entrega_informe']) or pd.isna(row['fecha_inicio_inspeccion']):
            return np.nan
        return safe_subtract_days(row['fecha_entrega_informe'], row['fecha_inicio_inspeccion'])

    df['kpi_dias_en_inspeccionar_dc'] = df.apply(lambda r: dias_en_inspeccionar(r, 'Informe Normal'), axis=1)
    df['kpi_dias_en_inspeccionar_dh'] = df.apply(lambda r: dias_en_inspeccionar(r, 'Informe asistida'), axis=1)

    # === KPI GESTIÓN TOTAL (DC y DH) ===
    def gestion_total(row, tipo):
        if row['informe_final'] != tipo:
            return np.nan
        if pd.isna(row['fecha_entrega_informe']) or pd.isna(row['fecha_emision']):
            return np.nan
        return safe_subtract_days(row['fecha_entrega_informe'], row['fecha_emision'])

    df['kpi_gestion_total_dc'] = df.apply(lambda r: gestion_total(r, 'Informe Normal'), axis=1)
    df['kpi_gestion_total_dh'] = df.apply(lambda r: gestion_total(r, 'Informe asistida'), axis=1)

    return df

# ==================
# USO DE LA FUNCIÓN
# ==================
# df = pd.read_excel("first_row_dataset.xlsx")
#df = aplicar_formulas_kpi(df_input)
# df.to_excel("resultado_kpi.xlsx", index=False)


# Leer el dataset
""" def grafica_meses(df_input):
    
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
    return plot_meses """

def grafica_meses(df):
    plot_meses = df["kpi_resp_bo"].hist(bins=20, figsize=(15, 10))
    plt.tight_layout()
    plt.show()
    return plot_meses

""" def grafica_ultimo_mes(df_input):
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
    return plot_ultimo_mes """

def grafica_ultimo_mes(df):
    plot_ultimo_mes = df["kpi_resp_bo"].hist(bins=20, figsize=(15, 10))
    plt.tight_layout()
    plt.show()
    return plot_ultimo_mes