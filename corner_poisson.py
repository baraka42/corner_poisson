import streamlit as st
import math
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
def calcular_odds_por_minuto(total_escanteios, diferenca_gols, minutos_totais):
    taxa_base = total_escanteios / 74

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

escanteios_total = st.number_input("Total de escanteios até o minuto 84:", min_value=0, step=1, value=0)
diferenca_gols = st.number_input("Diferença de gols até o minuto 84 (time da casa - visitante):", value=0, step=1)
acrescimos = st.number_input("Minutos de acréscimo:", min_value=0, max_value=10, step=1, value=5)

if st.button("Calcular Odds"):
    try:
        minutos_totais = 15 + acrescimos  # Ajustar o total de minutos conforme o acréscimo inserido
        resultados = calcular_odds_por_minuto(escanteios_total, diferenca_gols, minutos_totais)

        df = pd.DataFrame(resultados)
        df = df[(df['Minuto'] >= 84) & (df['Minuto'] <= 90)]

        st.markdown(f"### CORNER ODDS - Total de Escanteios: {escanteios_total}", unsafe_allow_html=True)
        st.dataframe(df.reset_index(drop=True))  # Remove a coluna de índice ao exibir

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
