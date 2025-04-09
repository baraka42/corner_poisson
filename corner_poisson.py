import math
import streamlit as st
import pandas as pd

# --- Funções de Cálculo (sem alterações na lógica interna) ---

# Função Poisson
def poisson(k, lambda_):
    # ... (código da função poisson sem alterações) ...
    if lambda_ < 0 or not isinstance(k, int) or k < 0: return 0.0
    if lambda_ == 0 and k > 0: return 0.0
    if lambda_ == 0 and k == 0: return 1.0
    try:
        if lambda_ <= 0: return 0.0
        # Usar lgamma para maior estabilidade
        log_lambda = math.log(lambda_)
        log_fact_k = math.lgamma(k + 1)
        log_prob = -lambda_ + k * log_lambda - log_fact_k
        if log_prob < -708.39: return 0.0
        if log_prob > 709.78: return float('inf')
        return math.exp(log_prob)
    except (ValueError, OverflowError):
        # Fallback para casos menores se logaritmo falhar
        try:
            if k > 170: return 0.0
            if lambda_ <= 0 and k > 0: return 0.0
            if lambda_ <= 0 and k == 0: return 1.0
            exp_neg_lambda = math.exp(-lambda_)
            if exp_neg_lambda == 0.0 and lambda_ > 0 : return 0.0
            # Adicionado tratamento para math.factorial com k grande
            if k > 170: # Aproximação comum para fatorial
                 return 0.0
            return (exp_neg_lambda * (lambda_ ** k)) / math.factorial(k)
        except (ValueError, OverflowError):
             return 0.0

# Função de ajuste para o FINAL do jogo
def ajustar_taxa_final_jogo(minuto_calculo, taxa_base_pre75, diferenca_gols_75):
    # ... (código da função ajustar_taxa_final_jogo sem alterações) ...
    if minuto_calculo < 75: return taxa_base_pre75
    aumento_percentual = (0.0333 + 0.0037 * max(0, minuto_calculo - 75))
    if diferenca_gols_75 < 0: aumento_percentual += 0.05
    elif diferenca_gols_75 == 0: aumento_percentual += 0.03
    else: aumento_percentual -= 0.02
    taxa_ajustada = taxa_base_pre75 * (1 + max(-0.95, aumento_percentual))
    return max(0.0001, taxa_ajustada)

# Função interna comum para calcular odds
def calcular_odd(prob):
    # ... (código da função calcular_odd sem alterações) ...
    if prob is None or prob <= 1e-9 or prob == float('inf'): return float('inf')
    if prob >= 0.9999: return 1.01
    try:
        odd = 1 / prob
        # Retornar inf se a odd calculada for extremamente alta
        if odd > 9999: return float('inf')
        return min(round(odd, 2), 1000.0)
    except ZeroDivisionError: return float('inf')


# Função para calcular odds para o FINAL DO SEGUNDO TEMPO
def calcular_odds_segundo_tempo_total_ate_74(acrescimos_2t, escanteios_totais_ate_74, diferenca_gols_75):
    # ... (código da função calcular_odds_segundo_tempo_total_ate_74 sem alterações) ...
    resultados = []
    if 74 <= 0: return []
    if escanteios_totais_ate_74 < 0: escanteios_totais_ate_74 = 0 # Garante não negativo
    if escanteios_totais_ate_74 == 0: taxa_base_pre75 = 0.01
    else:
        try: taxa_base_pre75 = escanteios_totais_ate_74 / 74
        except ZeroDivisionError: taxa_base_pre75 = 0.01
    taxa_base_pre75 = max(0.001, taxa_base_pre75)

    minutos_finais_regulamentares = 15
    acrescimos_validos = max(0, acrescimos_2t)
    minuto_final_real = 75 + minutos_finais_regulamentares + acrescimos_validos
    minuto_inicial_calculo = 75

    for minuto_loop in range(minuto_inicial_calculo, minuto_final_real + 1):
        tempo_restante = minuto_final_real - minuto_loop
        if tempo_restante <= 0: continue

        taxa_ajustada = ajustar_taxa_final_jogo(minuto_loop, taxa_base_pre75, diferenca_gols_75)
        lambda_ = taxa_ajustada * tempo_restante
        if lambda_ < 0: lambda_ = 0

        p0 = poisson(0, lambda_)
        p1 = poisson(1, lambda_)
        p_mais_0_5 = max(0.0, 1.0 - p0)

        resultados.append({
            'minuto': minuto_loop, # Minuto real do 2T
            '-0.5': calcular_odd(p0),
            'Exa 1': calcular_odd(p1),
            '+0.5': calcular_odd(p_mais_0_5)
        })
    return resultados

# --- Interface Streamlit ---

st.set_page_config(layout="centered") # Mudar para 'centered' pode ficar melhor sem sidebar

st.title("CORNER ODDS V2")

# *** ALTERAÇÃO AQUI: Inputs agora na página principal ***
st.subheader("Inserir Dados") # Adiciona um sub-cabeçalho

esc_totais_ate_74 = st.number_input(
    "Escanteios TOTAIS:",
    min_value=0,
    step=1,
    value=5 # Valor inicial de exemplo
)

diff_gols_75 = st.number_input(
    "Diferença de Gols:",
    step=1,
    value=0 # Valor inicial de exemplo
)

acr_2t = st.number_input(
    "Acréscimos Previstos:",
    min_value=0,
    step=1,
    value=3 # Valor inicial de exemplo
)

# Botão para calcular na página principal
calcular_button = st.button("Calcular Odds")

st.divider() # Linha separadora

# Lógica de cálculo e exibição (só executa após clicar no botão)
if calcular_button:
    resultados = calcular_odds_segundo_tempo_total_ate_74(acr_2t, esc_totais_ate_74, diff_gols_75)
    range_exibicao_2t = range(82, 88) # Minutos 82 a 87

    if resultados is not None:
        resultados_para_exibir = [res for res in resultados if res['minuto'] in range_exibicao_2t]

        if resultados_para_exibir:
            # Prepara dados para o DataFrame
            data_for_df = []
            for res in resultados_para_exibir:
                minuto_2t = res['minuto']
                minuto_1t = minuto_2t - 45
                minuto_display = f"{minuto_1t}'/{minuto_2t}'"

                odd_menos_0_5 = '-' if res['-0.5'] == float('inf') else f"{res['-0.5']:.2f}"
                odd_exa_1 = '-' if res['Exa 1'] == float('inf') else f"{res['Exa 1']:.2f}"
                odd_mais_0_5 = '-' if res['+0.5'] == float('inf') else f"{res['+0.5']:.2f}"

                data_for_df.append({
                    'Min(1T/2T)': minuto_display,
                    '-0.5': odd_menos_0_5,
                    'Exa 1': odd_exa_1,
                    '+0.5': odd_mais_0_5
                })

            df = pd.DataFrame(data_for_df)

            if not df.empty:
                min_vis = df['Min(1T/2T)'].iloc[0]
                max_vis = df['Min(1T/2T)'].iloc[-1]
                st.subheader(f"Odds Calculadas ({min_vis} a {max_vis})")

                # Exibe a tabela (usando st.table para compactação)
                st.table(df.set_index('Min(1T/2T)'))

               
            else:
                 min_range = min(range_exibicao_2t)
                 max_range = max(range_exibicao_2t)
                 st.warning(f"Nenhum dado calculado para exibir no intervalo {min_range}'-{max_range-1}'.")

        else:
             min_range = min(range_exibicao_2t)
             max_range = max(range_exibicao_2t)
             st.warning(f"Nenhum dado calculado caiu no intervalo de exibição desejado ({min_range}'-{max_range-1}').")
    else:
        st.error("Não foi possível calcular as odds com os dados fornecidos. Verifique os inputs.")

# Mensagem inicial removida, pois os inputs estão visíveis
# else:
#    st.info("Insira os dados acima e clique em 'Calcular Odds'.")
