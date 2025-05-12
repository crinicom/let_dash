
# calcula2.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from math import ceil


from datetime import datetime, timedelta


def aplicar_formulas_kpi(df):
    # Convertir las columnas de fecha a datetime
    df["fecha_emision"] = pd.to_datetime(df["fecha_emision"], errors='coerce')
    df["fecha_entrega_informe"] = pd.to_datetime(df["fecha_entrega_informe"], errors='coerce')

    # Calcular la diferencia en días entre "fecha_emision" y "fecha_entrega_informe"
    df["diferencia_dias"] = (df["fecha_entrega_informe"] - df["fecha_emision"]).dt.days

    # Calcular el promedio de días por mes
    df["promedio_dias_mes"] = df.groupby(df["fecha_emision"].dt.to_period("M"))["diferencia_dias"].transform("mean")

    # Calcular el promedio de días por año
    df["promedio_dias_anio"] = df.groupby(df["fecha_emision"].dt.to_period("Y"))["diferencia_dias"].transform("mean")

    # Add a new column "añomes emisión" to df_calc
    df["añomes emisión"] = df["fecha_emision"].apply(
        lambda fecha: f"{fecha.year:04d}{fecha.month:02d}" if pd.notnull(fecha) else "n/a"
    )

    # Ensure "fecha_entrega_informe" is in datetime format
    df["fecha_entrega_informe"] = pd.to_datetime(df["fecha_entrega_informe"], errors='coerce')

    # Add a new column "añomes entrega informe" to df_calc
    df["añomes entrega informe"] = df["fecha_entrega_informe"].apply(
        lambda fecha: f"{fecha.year:04d}{fecha.month:02d}" if pd.notnull(fecha) else "n/a"
    )

    return df

def calcular_ai_con_error(row):
    # USO DE LA FUNCIÓN
    # df_calc["AI con error N° veces"] = df_calc.apply(calcular_ai_con_error, axis=1)
    informe_final = row["informe_final"]
    fecha_tercera_correccion = row["fecha_3_correccion"]
    fecha_segunda_correccion = row["fecha_2_correccion"]
    fecha_primera_correccion = row["fecha_1_correccion"]
    ai_con_error = ""

    if informe_final in ["", "Informe Normal", "Informe asistida"]:
        ai_con_error = "n/a"
    elif pd.notnull(fecha_tercera_correccion) or pd.notnull(fecha_segunda_correccion):
        ai_con_error = "2+"
    elif pd.notnull(fecha_primera_correccion):
        ai_con_error = 1
    else:
        ai_con_error = "AI sin error"

    return ai_con_error

# AUX #
def calcular_diferencia_en_dias(fecha1, fecha2):
    # Ensure both dates are converted to datetime
    if pd.notnull(fecha1) and pd.notnull(fecha2):
        fecha1 = pd.to_datetime(fecha1, errors='coerce')
        fecha2 = pd.to_datetime(fecha2, errors='coerce')
        if pd.notnull(fecha1) and pd.notnull(fecha2):
            return (fecha1 - fecha2).days
    return None

def calcular_dias_en_coordinar_dc(row):
    # USO DE LA FUNCIÓN
    # df_calc["Días en coordinar DC"] = df_calc.apply(calcular_dias_en_coordinar_dc, axis=1)
    informe_final = row["informe_final"]
    fecha_cita = row["fecha_cita_conreta_inspeccion"]
    fecha_agendamiento = row["fecha_1_agendamiento"]
    fecha_emision = row["fecha_emision"]
    calculo_dias_dc = ""

    if informe_final == "" or pd.isnull(fecha_cita) or fecha_cita == "" or pd.isnull(fecha_agendamiento) or fecha_agendamiento == "":
        calculo_dias_dc = "n/a"
    else:
        dias_cita_emision = calcular_diferencia_en_dias(fecha_cita, fecha_emision)
        dias_agendamiento_emision = calcular_diferencia_en_dias(fecha_agendamiento, fecha_emision)

        if dias_cita_emision is not None and dias_agendamiento_emision is not None:
            if dias_cita_emision <= dias_agendamiento_emision:
                calculo_dias_dc = dias_cita_emision
            else:
                calculo_dias_dc = dias_agendamiento_emision
        else:
            calculo_dias_dc = "n/a"

    return calculo_dias_dc

def calcular_kpi_dias_dc(row):
    calculo_dias_dc = row["cálculo días en coordinar DC"]
    if calculo_dias_dc == "n/a" or calculo_dias_dc == "error" or calculo_dias_dc < 0:
        return "error"
    return calculo_dias_dc

def calcular_kpi_dias_dc_ok(row):
    kpi_dias_dc = row["KPI DÍAS EN COORDINAR DC"]
    if kpi_dias_dc == "error":
        return "error"
    elif kpi_dias_dc == "n/a":
        return "n/a"
    elif isinstance(kpi_dias_dc, (int, float)) and kpi_dias_dc >= 15:
        return "15+"
    else:
        return kpi_dias_dc


# Lista de feriados
feriados = [
    datetime(2025, 1, 1),  # Año Nuevo
    datetime(2025, 5, 1),  # Día del Trabajador
    datetime(2025, 9, 18),  # Fiestas Patrias
    datetime(2025, 12, 25)  # Navidad
]

# Función auxiliar para calcular días laborables
def calcular_dias_laborables(fecha_inicio, fecha_fin, lista_feriados):
    if pd.isnull(fecha_inicio) or pd.isnull(fecha_fin):
        return None
    # Convertir fechas a datetime si no lo son
    fecha_inicio = pd.to_datetime(fecha_inicio, errors='coerce')
    fecha_fin = pd.to_datetime(fecha_fin, errors='coerce')
    if pd.isnull(fecha_inicio) or pd.isnull(fecha_fin):
        return None
    dias_laborables = 0
    fecha_actual = fecha_inicio
    while fecha_actual <= fecha_fin:
        if fecha_actual.weekday() < 5 and fecha_actual not in lista_feriados:  # Día laborable
            dias_laborables += 1
        fecha_actual += timedelta(days=1)
    return dias_laborables

# Aplicar la lógica a cada fila del DataFrame
def calcular_dias_en_coordinar_dh(row):
    fecha_cita = row["fecha_cita_conreta_inspeccion"]
    fecha_agendamiento = row["fecha_1_agendamiento"]
    fecha_emision = row["fecha_emision"]
    informe_final = row["informe_final"]
    calculo_dias_dh = ""

    if fecha_cita == fecha_emision or fecha_agendamiento == fecha_emision:
        calculo_dias_dh = "cero"
    elif pd.isnull(fecha_cita) and pd.isnull(fecha_agendamiento):
        calculo_dias_dh = "n/a"
    elif informe_final == "Informe Normal":
        calculo_dias_dh = calcular_dias_laborables(fecha_emision, fecha_cita, feriados)
    else:
        calculo_dias_dh = calcular_dias_laborables(fecha_emision, fecha_agendamiento, feriados)

    return calculo_dias_dh

def calcular_kpi_dias_dh(row):
    calculo_dias_dh = row["cálculo días en coordinar DH"]
    kpi_dias_dh = ""

    if calculo_dias_dh == "error":
        kpi_dias_dh = "error"
    elif calculo_dias_dh == "cero" or calculo_dias_dh == 0:
        kpi_dias_dh = 0
    elif calculo_dias_dh == "n/a":
        kpi_dias_dh = "n/a"
    elif isinstance(calculo_dias_dh, (int, float)) and calculo_dias_dh < 0:
        kpi_dias_dh = "error"
    elif isinstance(calculo_dias_dh, (int, float)):
        kpi_dias_dh = calculo_dias_dh - 1

    return kpi_dias_dh

def calcular_kpi_dias_dh_ok(row):
    kpi_dias_dh = row["KPI DÍAS EN COORDINAR DH"]
    if kpi_dias_dh == "error":
        return "error"
    elif kpi_dias_dh == "n/a":
        return "n/a"
    elif isinstance(kpi_dias_dh, (int, float)) and kpi_dias_dh >= 15:
        return "15+"
    else:
        return kpi_dias_dh

def calcular_dias_inspeccion_dc(row):
    fecha_termino_inspeccion = row["fecha_termino_inspeccion"]
    fecha_entrega_informe = row["fecha_entrega_informe"]
    fecha_emision_oi = row["fecha_emision"]
    informe_final = row["informe_final"]
    calculo_dias_inspeccion_dc = ""

    if pd.isnull(fecha_entrega_informe):
        calculo_dias_inspeccion_dc = "n/a"
    else:
        if informe_final == "Informe Normal":
            dias_termino_emision = calcular_diferencia_en_dias(fecha_termino_inspeccion, fecha_emision_oi)
            calculo_dias_inspeccion_dc = dias_termino_emision
        else:
            dias_entrega_emision = calcular_diferencia_en_dias(fecha_entrega_informe, fecha_emision_oi)
            calculo_dias_inspeccion_dc = dias_entrega_emision

    return calculo_dias_inspeccion_dc

def calcular_kpi_dias_inspeccion_dc(row):
    calculo_dias_inspeccion_dc = row["cálculo días en inspeccionar DC"]
    if calculo_dias_inspeccion_dc == "error" or (isinstance(calculo_dias_inspeccion_dc, (int, float)) and calculo_dias_inspeccion_dc < 0):
        return "error"
    return calculo_dias_inspeccion_dc

def calcular_kpi_dias_inspeccion_dc_ok(row):
    kpi_dias_inspeccion_dc = row["KPI DÍAS EN INSPECCIONAR DC"]
    if kpi_dias_inspeccion_dc == "error":
        return "error"
    elif kpi_dias_inspeccion_dc == "n/a":
        return "n/a"
    elif isinstance(kpi_dias_inspeccion_dc, (int, float)) and kpi_dias_inspeccion_dc >= 15:
        return "15+"
    else:
        return kpi_dias_inspeccion_dc

def calcular_dias_inspeccion_dh(row):
    fecha_termino_inspeccion = row["fecha_termino_inspeccion"]
    fecha_entrega_informe = row["fecha_entrega_informe"]
    fecha_emision_oi = row["fecha_emision"]
    informe_final = row["informe_final"]
    calculo_dias_inspeccion_dh = ""

    if pd.isnull(fecha_entrega_informe):
        calculo_dias_inspeccion_dh = "n/a"
    else:
        if informe_final == "Informe Normal":
            calculo_dias_inspeccion_dh = calcular_dias_laborables(fecha_emision_oi, fecha_termino_inspeccion, feriados)
        else:
            calculo_dias_inspeccion_dh = calcular_dias_laborables(fecha_emision_oi, fecha_entrega_informe, feriados)

    return calculo_dias_inspeccion_dh

def calcular_kpi_dias_inspeccion_dh(row):
    calculo_dias_inspeccion_dh = row["cálculo días en inspeccionar DH"]
    kpi_dias_inspeccion_dh = ""

    if calculo_dias_inspeccion_dh == "error":
        kpi_dias_inspeccion_dh = "error"
    elif calculo_dias_inspeccion_dh == "cero":
        kpi_dias_inspeccion_dh = 0
    elif isinstance(calculo_dias_inspeccion_dh, (int, float)) and calculo_dias_inspeccion_dh < 0:
        kpi_dias_inspeccion_dh = "error"
    elif calculo_dias_inspeccion_dh == "n/a":
        kpi_dias_inspeccion_dh = "n/a"
    elif isinstance(calculo_dias_inspeccion_dh, (int, float)) and calculo_dias_inspeccion_dh - 1 == -1:
        kpi_dias_inspeccion_dh = 0
    elif isinstance(calculo_dias_inspeccion_dh, (int, float)):
        kpi_dias_inspeccion_dh = calculo_dias_inspeccion_dh - 1

    return kpi_dias_inspeccion_dh

def calcular_kpi_dias_inspeccion_dh_ok(row):
    kpi_dias_inspeccion_dh = row["KPI DÍAS EN INSPECCIONAR DH"]
    if kpi_dias_inspeccion_dh == "error":
        return "error"
    elif kpi_dias_inspeccion_dh == "n/a":
        return "n/a"
    elif isinstance(kpi_dias_inspeccion_dh, (int, float)) and kpi_dias_inspeccion_dh >= 15:
        return "15+"
    else:
        return kpi_dias_inspeccion_dh

from math import floor

# Function to combine date and time into a datetime object
def combinar_fecha_hora(fecha, hora):
    if pd.isnull(fecha) or pd.isnull(hora):
        return None
    return pd.to_datetime(f"{fecha} {hora}", errors='coerce')

# Function to calculate the median of three values
def mediana(a, b, c):
    lista = [a, b, c]
    lista.sort()
    return lista[1]

# Define upper and lower bounds (in fraction of a day)
upper = 18 / 24
lower = 9 / 24

# Apply the logic to each row in the dataset
def calcular_resp_bo_dom(row):
    fecha_termino_insp = row["fecha_termino_inspeccion"]
    hora_termino_insp = row["hora_termino_inspeccion"]
    fecha_transmision = row["fecha_transmision_inspeccion"]
    hora_transmision = row["hora_transmision_inspeccion"]
    calculo_resp_bo_dom = ""

    fecha_hora_termino_dom = combinar_fecha_hora(fecha_termino_insp, hora_termino_insp)
    fecha_hora_entrega_dom = combinar_fecha_hora(fecha_transmision, hora_transmision)

    if pd.isnull(fecha_hora_termino_dom) or pd.isnull(fecha_hora_entrega_dom) or fecha_hora_entrega_dom < fecha_hora_termino_dom:
        calculo_resp_bo_dom = "n/a"
    else:
        dias_laborables = calcular_dias_laborables(fecha_hora_termino_dom, fecha_hora_entrega_dom, feriados) - 1
        residuo_termino = (fecha_hora_termino_dom - pd.Timestamp(fecha_hora_termino_dom.date())).total_seconds() / (24 * 3600)
        residuo_entrega = (fecha_hora_entrega_dom - pd.Timestamp(fecha_hora_entrega_dom.date())).total_seconds() / (24 * 3600)

        dias_laborables_hasta_entrega = calcular_dias_laborables(fecha_hora_termino_dom, fecha_hora_entrega_dom, feriados)
        dias_laborables_hasta_termino = calcular_dias_laborables(fecha_hora_termino_dom, fecha_hora_termino_dom, feriados)

        parte_entrega = mediana(residuo_entrega, upper, lower) if dias_laborables_hasta_entrega > 0 else upper
        parte_termino = mediana(dias_laborables_hasta_termino * residuo_termino, upper, lower)

        resultado = (dias_laborables * (upper - lower)) + parte_entrega - parte_termino

        if resultado < 0:
            calculo_resp_bo_dom = "error"
        else:
            calculo_resp_bo_dom = resultado

    return calculo_resp_bo_dom



# Function to convert "HH:MM:SS" to a fraction of a day
def tiempo_a_fraccion_dia(tiempo_str):
    if tiempo_str is None or tiempo_str == "":
        return None
    horas, minutos, segundos = map(int, tiempo_str.split(":"))
    return (horas * 3600 + minutos * 60 + segundos) / (24 * 3600)

# Function to round up to the nearest multiple
def redondear_arriba_al_multiplo(numero, multiplo):
    if multiplo == 0:
        return numero
    return ceil(numero / multiplo) * multiplo

# Value of 5 minutes in fraction of a day
cinco_minutos_en_fraccion = tiempo_a_fraccion_dia("00:05:00")

# Apply the logic to each row in the dataset
def calcular_kpi_resp_bo_dom_ceiling(row):
    calculo_resp_bo_dom = row["cálculo resp BO DOM"]
    if calculo_resp_bo_dom in ["n/a", "error"]:
        return calculo_resp_bo_dom
    else:
        return redondear_arriba_al_multiplo(calculo_resp_bo_dom, cinco_minutos_en_fraccion)

# Iterate over each row in the dataset
def calcular_kpi_resp_bo_dom_ceiling(row):
    calculo_resp_bo_dom = row["cálculo resp BO DOM"]
    if calculo_resp_bo_dom in ["n/a", "error"]:
        return calculo_resp_bo_dom
    else:
        return redondear_arriba_al_multiplo(calculo_resp_bo_dom, cinco_minutos_en_fraccion)

# Define the value for 9 hours in fraction of a day
nueve_horas_en_fraccion = 0.375

# Function to calculate "KPI resp BO DOM CEILING OK" for each row
def calcular_kpi_resp_bo_dom_ceiling_ok(row):
    kpi_resp_bo_dom_ceiling = row["KPI resp BO DOM CEILING"]
    if kpi_resp_bo_dom_ceiling == "n/a":
        return "n/a"
    elif isinstance(kpi_resp_bo_dom_ceiling, (int, float)) and kpi_resp_bo_dom_ceiling > nueve_horas_en_fraccion:
        return "9+"
    else:
        return kpi_resp_bo_dom_ceiling

# Apply the function to the dataset

# Define the value for 9 hours in fraction of a day
nueve_horas_en_fraccion = 0.375

# Function to calculate "KPI resp BO DOM CEILING OK" for each row
def calcular_kpi_resp_bo_dom_ceiling_ok(row):
    kpi_resp_bo_dom_ceiling = row["KPI resp BO DOM CEILING"]
    if kpi_resp_bo_dom_ceiling == "n/a":
        return "n/a"
    elif isinstance(kpi_resp_bo_dom_ceiling, (int, float)) and kpi_resp_bo_dom_ceiling > nueve_horas_en_fraccion:
        return "9+"
    elif isinstance(kpi_resp_bo_dom_ceiling, (int, float)):
        # Convert the fraction of a day to hours and minutes
        total_minutes = int(kpi_resp_bo_dom_ceiling * 24 * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    else:
        return kpi_resp_bo_dom_ceiling

# Apply the logic to calculate "cálculo resp BO AI" for each row in the dataset
def calcular_resp_bo_ai(row):
    fecha_inicio_ai = row["fecha_ultimo_inicio_AI"]
    hora_inicio_ai = row["hora_ultimo_inicio_AI"]
    fecha_recepcion_ai = row["fecha_recepcion_AI"]
    hora_recepcion_ai = row["hora_recepcion_AI"]
    calculo_resp_bo_ai = ""

    fecha_hora_inicio_ai = combinar_fecha_hora(fecha_inicio_ai, hora_inicio_ai)
    fecha_hora_recepcion_ai = combinar_fecha_hora(fecha_recepcion_ai, hora_recepcion_ai)

    if pd.isnull(fecha_hora_inicio_ai) or pd.isnull(fecha_hora_recepcion_ai) or fecha_hora_recepcion_ai < fecha_hora_inicio_ai:
        calculo_resp_bo_ai = "n/a"
    else:
        dias_laborables = calcular_dias_laborables(fecha_hora_inicio_ai, fecha_hora_recepcion_ai, feriados) - 1
        residuo_inicio_ai = (fecha_hora_inicio_ai - pd.Timestamp(fecha_hora_inicio_ai.date())).total_seconds() / (24 * 3600)
        residuo_recepcion_ai = (fecha_hora_recepcion_ai - pd.Timestamp(fecha_hora_recepcion_ai.date())).total_seconds() / (24 * 3600)

        dias_laborables_hasta_recepcion_ai = calcular_dias_laborables(fecha_hora_inicio_ai, fecha_hora_recepcion_ai, feriados)
        dias_laborables_hasta_inicio_ai = calcular_dias_laborables(fecha_hora_inicio_ai, fecha_hora_inicio_ai, feriados)

        parte_recepcion_ai = mediana(residuo_recepcion_ai, upper, lower) if dias_laborables_hasta_recepcion_ai > 0 else upper
        parte_inicio_ai = mediana(dias_laborables_hasta_inicio_ai * residuo_inicio_ai, upper, lower)

        resultado_ai = (dias_laborables * (upper - lower)) + parte_recepcion_ai - parte_inicio_ai

        if resultado_ai < 0:
            calculo_resp_bo_ai = "error"
        else:
            calculo_resp_bo_ai = resultado_ai * 24

    return calculo_resp_bo_ai

# Apply the logic to calculate "KPI resp BO AI CEILING" for each row in the dataset
def calcular_kpi_resp_bo_ai_ceiling(row):
    calculo_resp_bo_ai = row["cálculo resp BO AI"]
    if calculo_resp_bo_ai in ["n/a", "error"]:
        return calculo_resp_bo_ai
    else:
        return redondear_arriba_al_multiplo(calculo_resp_bo_ai, cinco_minutos_en_fraccion)

# Function to calculate "KPI resp BO AI CEILING OK" for each row
def calcular_kpi_resp_bo_ai_ceiling_ok(row):
    kpi_resp_bo_ai_ceiling = row["KPI resp BO AI CEILING"]
    if kpi_resp_bo_ai_ceiling == "n/a":
        return "n/a"
    elif isinstance(kpi_resp_bo_ai_ceiling, (int, float)) and kpi_resp_bo_ai_ceiling > nueve_horas_en_fraccion:
        return "9+"
    else:
        return kpi_resp_bo_ai_ceiling

# Apply the logic to calculate "cálculo resp BO AI sin error" for each row in the dataset
def calcular_resp_bo_ai_sin_error(row):
    ai_sin_error_n_veces = row["AI con error N° veces"]
    calculo_resp_bo_ai_sin_error = ""

    if ai_sin_error_n_veces == "AI sin error":
        # Obtener las fechas y horas
        fecha_inicio_ai = row["fecha_ultimo_inicio_AI"]
        hora_inicio_ai = row["hora_ultimo_inicio_AI"]
        fecha_recepcion_ai = row["fecha_recepcion_AI"]
        hora_recepcion_ai = row["hora_recepcion_AI"]

        fecha_hora_inicio_ai = combinar_fecha_hora(fecha_inicio_ai, hora_inicio_ai)
        fecha_hora_recepcion_ai = combinar_fecha_hora(fecha_recepcion_ai, hora_recepcion_ai)

        if pd.isnull(fecha_hora_inicio_ai) or pd.isnull(fecha_hora_recepcion_ai) or fecha_hora_recepcion_ai < fecha_hora_inicio_ai:
            calculo_resp_bo_ai_sin_error = "n/a"
        else:
            # Realizar el cálculo
            dias_laborables = calcular_dias_laborables(fecha_hora_inicio_ai, fecha_hora_recepcion_ai, feriados) - 1
            residuo_inicio_ai = (fecha_hora_inicio_ai - pd.Timestamp(fecha_hora_inicio_ai.date())).total_seconds() / (24 * 3600)
            residuo_recepcion_ai = (fecha_hora_recepcion_ai - pd.Timestamp(fecha_hora_recepcion_ai.date())).total_seconds() / (24 * 3600)

            dias_laborables_hasta_recepcion_ai = calcular_dias_laborables(fecha_hora_inicio_ai, fecha_hora_recepcion_ai, feriados)
            dias_laborables_hasta_inicio_ai = calcular_dias_laborables(fecha_hora_inicio_ai, fecha_hora_inicio_ai, feriados)

            parte_recepcion_ai = mediana(residuo_recepcion_ai, upper, lower) if dias_laborables_hasta_recepcion_ai > 0 else upper
            parte_inicio_ai = mediana(dias_laborables_hasta_inicio_ai * residuo_inicio_ai, upper, lower)

            resultado_sin_error = (dias_laborables * (upper - lower)) + parte_recepcion_ai - parte_inicio_ai

            if resultado_sin_error < 0:
                calculo_resp_bo_ai_sin_error = "error"
            else:
                calculo_resp_bo_ai_sin_error = resultado_sin_error
    else:
        calculo_resp_bo_ai_sin_error = "n/a"

    return calculo_resp_bo_ai_sin_error

# Apply the logic to calculate "KPI resp BO AI sin error CEILING" for each row in the dataset
def calcular_kpi_resp_bo_ai_sin_error_ceiling(row):
    calculo_resp_bo_ai_sin_error = row["cálculo resp BO AI sin error"]
    if calculo_resp_bo_ai_sin_error in ["n/a", "error"]:
        return calculo_resp_bo_ai_sin_error
    else:
        return redondear_arriba_al_multiplo(calculo_resp_bo_ai_sin_error, cinco_minutos_en_fraccion)


# Function to calculate "KPI resp BO AI sin error CEILING OK" for each row
def calcular_kpi_resp_bo_ai_sin_error_ceiling_ok(row):
    kpi_resp_bo_ai_sin_error_ceiling = row["KPI resp BO AI sin error CEILING"]
    if kpi_resp_bo_ai_sin_error_ceiling == "n/a":
        return "n/a"
    elif isinstance(kpi_resp_bo_ai_sin_error_ceiling, (int, float)) and kpi_resp_bo_ai_sin_error_ceiling > nueve_horas_en_fraccion:
        return "9+"
    else:
        return kpi_resp_bo_ai_sin_error_ceiling


# Define a function to calculate the difference in days between two datetime values
def calcular_diferencia_en_dias(fecha_mayor, fecha_menor):
    if pd.isnull(fecha_mayor) or pd.isnull(fecha_menor):
        return None
    fecha_mayor = pd.to_datetime(fecha_mayor, errors='coerce')
    fecha_menor = pd.to_datetime(fecha_menor, errors='coerce')
    if pd.isnull(fecha_mayor) or pd.isnull(fecha_menor):
        return None
    return (fecha_mayor - fecha_menor).days

# Apply the logic to each row in the dataset
def calcular_resp_bo_gral(row):
    fecha_termino = pd.to_datetime(row["fecha_termino_inspeccion"], errors='coerce')
    fecha_entrega = pd.to_datetime(row["fecha_entrega_informe"], errors='coerce')
    resp_bo_gral = ""

    if pd.isnull(fecha_termino) or pd.isnull(fecha_entrega) or fecha_entrega < fecha_termino:
        resp_bo_gral = "n/a"
    else:
        diferencia = calcular_diferencia_en_dias(fecha_entrega, fecha_termino)
        if diferencia is None:
            resp_bo_gral = "error"
        else:
            resp_bo_gral = diferencia

    return resp_bo_gral

# Define the value for 9 hours in fraction of a day
nueve_horas_en_fraccion = 0.375

# Apply the logic to calculate "resp BO GRAL EXCLUYE 0 y 9+" for each row in the dataset
def calcular_resp_bo_gral_excluye(row):
    resp_bo_gral = row["resp BO GRAL"]
    resp_bo_gral_excluye = ""

    if resp_bo_gral == "n/a":
        resp_bo_gral_excluye = "n/a"
    elif isinstance(resp_bo_gral, (int, float)) and resp_bo_gral <= 0:
        resp_bo_gral_excluye = "0"
    elif isinstance(resp_bo_gral, (int, float)) and resp_bo_gral > nueve_horas_en_fraccion:
        resp_bo_gral_excluye = "9+"
    elif isinstance(resp_bo_gral, (int, float)):
        resp_bo_gral_excluye = resp_bo_gral

    return resp_bo_gral_excluye

