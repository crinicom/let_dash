#Contiene las funciones para graficar los resultados de la consulta a la API

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime as dt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.dates as mdates


def grafica_atributo(df_calc, atributo, title):
    print(df_calc.columns)
    col_interes = ['KPI resp BO DOM CEILING OK']
    col_interes = [atributo]

    for col in col_interes:
        valid_values = df_calc[col][~df_calc[col].isin(["error", "n/a"])]

        if valid_values.empty:
            continue

        def convertir_a_minutos(valor):
            if isinstance(valor, str) and ":" in valor:
                horas, minutos = map(int, valor.split(":"))
                return horas * 60 + minutos
            elif valor == "9+":
                return 540
            return None

        valid_values_minutos = valid_values.apply(convertir_a_minutos).dropna()

        max_minutos = valid_values_minutos.max()
        bins = list(range(0, int(max_minutos) + 30, 30))
        labels = [f"{i}-{i+30}" for i in bins[:-1]]

        binned_values = pd.cut(valid_values_minutos, bins=bins, labels=labels, right=False)

        percent = binned_values.value_counts(normalize=True).reindex(labels, fill_value=0) * 100
        acumulado_percent = percent.cumsum()

        fig, ax1 = plt.subplots(figsize=(8, 4))  # un poco más ancho para dar espacio a la leyenda

        sns.barplot(x=percent.index, y=percent.values, order=labels, ax=ax1, color="skyblue")
        ax1.set_title(f"{title}\nDistribución de {col} (en intervalos de 30 minutos)")
        ax1.set_xlabel("Intervalos de tiempo (minutos)")
        ax1.set_ylabel("Porcentaje (%)")
        ax1.tick_params(axis="x", rotation=45)

        for p in ax1.patches:
            height = p.get_height()
            ax1.annotate(f'{height:.1f}%', 
                        (p.get_x() + p.get_width() / 2., height), 
                        ha='center', va='bottom', fontsize=8)

        ax2 = ax1.twinx()
        ax2.plot(labels, acumulado_percent.values, color="red", marker="o", linestyle="-", label="Acumulado (%)")
        ax2.set_ylabel("Acumulado porcentual (%)")
        ax2.set_ylim(0, 105)

        # Mover leyenda fuera del gráfico
        ax2.legend(loc="upper left", bbox_to_anchor=(1.02, -0.1), borderaxespad=0)

        plt.tight_layout()
        plt.show()

        
        return fig
    


def grafica_atributo_mes(df_calc, atributo, title):
    # Filtrar por el último mes cerrado
    today = pd.Timestamp.today()
    primero_del_mes = today.replace(day=1)
    ultimo_mes = primero_del_mes - pd.DateOffset(days=1)
    inicio_ultimo_mes = ultimo_mes.replace(day=1)
    fin_ultimo_mes = ultimo_mes.replace(day=ultimo_mes.days_in_month)

    df_mes = df_calc[
        (df_calc["fecha_emision"] >= inicio_ultimo_mes) &
        (df_calc["fecha_emision"] <= fin_ultimo_mes)
    ]

    # Validar si hay datos suficientes
    if df_mes.empty:
        print("⚠️ No hay datos para el mes cerrado anterior.")
        return None

    col_interes = [atributo]

    for col in col_interes:
        valid_values = df_mes[col][~df_mes[col].isin(["error", "n/a"])]

        if valid_values.empty:
            print(f"⚠️ No hay valores válidos para el atributo '{col}' en el último mes cerrado.")
            return None

        def convertir_a_minutos(valor):
            if isinstance(valor, str) and ":" in valor:
                horas, minutos = map(int, valor.split(":"))
                return horas * 60 + minutos
            elif valor == "9+":
                return 540
            return None

        valid_values_minutos = valid_values.apply(convertir_a_minutos).dropna()

        max_minutos = valid_values_minutos.max()
        bins = list(range(0, int(max_minutos) + 30, 30))
        labels = [f"{i}-{i+30}" for i in bins[:-1]]

        binned_values = pd.cut(valid_values_minutos, bins=bins, labels=labels, right=False)
        percent = binned_values.value_counts(normalize=True).reindex(labels, fill_value=0) * 100
        acumulado_percent = percent.cumsum()

        fig, ax1 = plt.subplots(figsize=(8, 4))

        sns.barplot(x=percent.index, y=percent.values, order=labels, ax=ax1, color="skyblue")
        ax1.set_title(f"{title} - {inicio_ultimo_mes.strftime('%B %Y')}")
        ax1.set_xlabel("Intervalos de tiempo (minutos)")
        ax1.set_ylabel("Porcentaje (%)")
        ax1.tick_params(axis="x", rotation=45)

        for p in ax1.patches:
            height = p.get_height()
            ax1.annotate(f'{height:.1f}%', 
                         (p.get_x() + p.get_width() / 2., height), 
                         ha='center', va='bottom', fontsize=8)

        ax2 = ax1.twinx()
        ax2.plot(labels, acumulado_percent.values, color="red", marker="o", linestyle="-", label="Acumulado (%)")
        ax2.set_ylabel("Acumulado porcentual (%)")
        ax2.set_ylim(0, 105)
        ax2.legend(loc="upper left", bbox_to_anchor=(1.02, -0.1), borderaxespad=0)

        plt.tight_layout()
        plt.show()

        return fig


def grafica_atributo_evolutivo(df_calc, atributo, title):
    df = df_calc.copy()

    # Asegurarse de que fecha_emision sea datetime
    df["fecha_emision"] = pd.to_datetime(df["fecha_emision"], errors="coerce")
    df = df.dropna(subset=["fecha_emision"])

    # Crear columna con año-mes
    df["mes"] = df["fecha_emision"].dt.to_period("M").dt.to_timestamp()

    # Limpiar valores no válidos
    df = df[~df[atributo].isin(["error", "n/a"])]

    def convertir_a_minutos(valor):
        if isinstance(valor, str) and ":" in valor:
            horas, minutos = map(int, valor.split(":"))
            return horas * 60 + minutos
        elif valor == "9+":
            return 540
        return None

    df["minutos"] = df[atributo].apply(convertir_a_minutos)

    # Filtrar filas con minutos válidos
    df = df.dropna(subset=["minutos"])

    # Agrupar por mes y calcular porcentaje de <= 30 minutos
    resumen = df.groupby("mes").agg(
        total=("minutos", "count"),
        menor_igual_30=("minutos", lambda x: (x <= 30).sum())
    )
    resumen["porcentaje_0_30"] = 100 * resumen["menor_igual_30"] / resumen["total"]

    # Graficar
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.lineplot(data=resumen, x=resumen.index, y="porcentaje_0_30", marker="o", ax=ax, color="green")
    ax.set_title(title)
    ax.set_ylabel(f"{atributo}\nPorcentaje de respuestas ≤ 30 min (%)")
    ax.set_xlabel("Mes")
    ax.set_ylim(0, 100)
    ax.grid(True)

    # Formatear el eje X para mostrar solo los meses presentes en los datos
    meses_presentes = resumen.index.strftime('%Y-%m')  # Obtener los meses como strings 'YYYY-MM'
    ax.set_xticks(resumen.index) # Establecer las ubicaciones de las ticks
    ax.set_xticklabels(meses_presentes, rotation=45, ha="right") # Establecer las etiquetas y rotarlas

    for i, valor in enumerate(resumen["porcentaje_0_30"]):
        ax.text(resumen.index[i], valor + 1, f"{valor:.1f}%", ha="center", fontsize=8)

    plt.tight_layout()
    return fig
