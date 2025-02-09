# -*- coding: utf-8 -*-
"""corner_poisson.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1K_FzNeEK20iNwvg1517gGBhq3G8G-Rlk
"""

import math
import streamlit as st
import pandas as pd

# Função para calcular a distribuição de Poisson
def poisson(k, lambda_):
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

# Função para ajustar a taxa de escanteios no final do jogo
def ajustar_taxa_final_jogo(minuto, taxa_base, diferenca_gols):
    aumento = 0.0333 + 0.0037 * (minuto - 75)
    if diferenca_gols < 0:
        aumento += 0.05
    elif diferenca_gols == 0:
        aumento += 0.03
    else:
        aumento -= 0.02
    return taxa_base * (1 + aumento)

# Função para calcular odds por minuto
def calcular_odds_por_minuto(total_escanteios, diferenca_gols):
    taxa_base = total_escanteios / 74
    minutos_totais = 15 + 5

    resultados = []
    for minuto in range(75, 75 + minutos_totais + 1):
        tempo_restante = (75 + minutos_totais) - minuto
        taxa_ajustada = ajustar_taxa_final_jogo(minuto, taxa_base, diferenca_gols)
        lambda_ = taxa_ajustada * tempo_restante

        p0 = poisson(0, lambda_)
        p1 = poisson(1, lambda_)
        p2 = poisson(2, lambda_)

        p_menos_0_5 = p0
        p_menos_1_5 = p0 + p1
        p_menos_2_5 = p0 + p1 + p2

        def calcular_odd(prob):
            return round(1 / prob, 2) if prob > 0 else float('inf')

        resultados.append({
            'Minuto': minuto,
            'Esc. Proj.': round(lambda_, 1),
            '-0.5': calcular_odd(p_menos_0_5),
            '-1.5': calcular_odd(p_menos_1_5),
            '-2.5': calcular_odd(p_menos_2_5),
            '+0.5': calcular_odd(1 - p0),
            '+1.5': calcular_odd(1 - p0 - p1),
            '+2.5': calcular_odd(1 - p0 - p1 - p2)
        })
    return resultados

# Interface do Streamlit
st.title("Corner Odds")
st.markdown("### Insira os dados para o cálculo:")

escanteios_total = st.number_input("Total de escanteios até o minuto 74:", min_value=0, step=1, value=0)
diferenca_gols = st.number_input("Diferença de gols até o minuto 75 (time da casa - visitante):", value=0, step=1)

if st.button("Calcular Odds"):
    try:
        resultados = calcular_odds_por_minuto(escanteios_total, diferenca_gols)

        df = pd.DataFrame(resultados)

        # Formatar valores para HTML
        def format_value(val, minuto, coluna):
            if coluna == "-0.5" and minuto >= 84:
                return f"<b>{val:.2f}</b>"
            return f"{val:.2f}"

        df_html = df.to_html(index=False, escape=False, formatters={
    col: (lambda x, col=col: format_value(x, df.loc[df[col] == x, "Minuto"].values[0], col)) for col in df.columns if col != "Minuto"
})


        st.markdown("### CORNER ODDS", unsafe_allow_html=True)
        st.markdown(df_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")