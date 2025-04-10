import math
import streamlit as st
import pandas as pd
# import locale # Pode ser removido se não usar formatação específica de locale

# --- Funções de Cálculo (Todas as suas funções + a nova) ---

# Função Poisson (Existente - MANTIDA COMO ESTÁ)
def poisson(k, lambda_):
    # ... (seu código completo da função poisson) ...
    if lambda_ < 0 or not isinstance(k, int) or k < 0: return 0.0
    if lambda_ == 0 and k == 0: return 1.0
    if lambda_ == 0 and k > 0: return 0.0
    try:
        log_lambda = math.log(lambda_)
        log_fact_k = math.lgamma(k + 1)
        log_prob = -lambda_ + k * log_lambda - log_fact_k
        if log_prob < -708.3: return 0.0
        if log_prob > 709.7: return float('inf')
        return math.exp(log_prob)
    except (ValueError, OverflowError):
        try:
             if k > 170: return 0.0
             return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)
        except:
             return 0.0

# Função de ajuste para o FINAL do jogo (Existente - MANTIDA COMO ESTÁ)
def ajustar_taxa_final_jogo(minuto_calculo, taxa_base_pre75, diferenca_gols_75):
    # ... (seu código completo da função ajustar_taxa_final_jogo) ...
    if minuto_calculo < 75: return taxa_base_pre75
    aumento_percentual = (0.0333 + 0.0037 * max(0, minuto_calculo - 75))
    if diferenca_gols_75 < 0: aumento_percentual += 0.05
    elif diferenca_gols_75 == 0: aumento_percentual += 0.03
    else: aumento_percentual -= 0.02
    taxa_ajustada = taxa_base_pre75 * (1 + max(-0.95, aumento_percentual))
    return max(0.0001, taxa_ajustada)


# Função interna comum para calcular odds (Existente - MANTIDA COMO ESTÁ)
def calcular_odd(prob):
    # ... (seu código completo da função calcular_odd) ...
    if prob is None or prob <= 1e-9 or prob == float('inf'): return float('inf')
    if prob >= 0.9999: return 1.01
    try:
        odd = 1 / prob
        if odd > 9999: return float('inf')
        return max(1.01, round(odd, 2))
    except ZeroDivisionError:
        return float('inf')

# Função para calcular odds para o FINAL DO SEGUNDO TEMPO (Existente - MANTIDA COMO ESTÁ)
def calcular_odds_segundo_tempo_total_ate_74(acrescimos_2t, escanteios_totais_ate_74, diferenca_gols_75):
    # ... (seu código completo da função calcular_odds_segundo_tempo_total_ate_74) ...
    resultados = []
    if 74 <= 0: return []
    if escanteios_totais_ate_74 < 0: escanteios_totais_ate_74 = 0
    try:
        taxa_base_pre75 = escanteios_totais_ate_74 / 74 if escanteios_totais_ate_74 > 0 else 0.01
    except ZeroDivisionError: taxa_base_pre75 = 0.01
    taxa_base_pre75 = max(0.001, taxa_base_pre75)
    minutos_finais_regulamentares = 15
    acrescimos_validos = max(0, acrescimos_2t)
    minuto_final_real = 75 + minutos_finais_regulamentares + acrescimos_validos
    minuto_inicial_calculo = 75
    for minuto_loop in range(minuto_inicial_calculo, int(minuto_final_real) + 1):
        tempo_restante = minuto_final_real - minuto_loop
        if tempo_restante <= 0: continue
        taxa_ajustada = ajustar_taxa_final_jogo(minuto_loop, taxa_base_pre75, diferenca_gols_75)
        lambda_ = taxa_ajustada * tempo_restante
        if lambda_ < 0: lambda_ = 0
        p0 = poisson(0, lambda_)
        p1 = poisson(1, lambda_)
        p_mais_0_5 = max(0.0, 1.0 - p0)
        resultados.append({
            'minuto': minuto_loop, '-0.5': calcular_odd(p0), 'Exa 1': calcular_odd(p1), '+0.5': calcular_odd(p_mais_0_5)
        })
    return resultados

# --- Constante e Função para a calculadora Próximos 10 min (Existente - MANTIDA COMO ESTÁ) ---
ACRESCIMO_PADRAO_1T_PROX10 = 3.0

def calcular_probabilidades_e_odds_poisson_prox10(tempo_decorrido_min, escanteios_ocorridos, inicio_intervalo_min, fim_intervalo_min):
    """Calcula odds para os próximos 10 min (versão interna, com ajuste de tempo)."""
    # ... (código completo da função calcular_probabilidades_e_odds_poisson_prox10) ...
    tempo_efetivo_para_taxa = tempo_decorrido_min
    if tempo_decorrido_min >= 46.0:
        tempo_no_segundo_tempo = tempo_decorrido_min - 45.0
        tempo_efetivo_para_taxa = 45.0 + ACRESCIMO_PADRAO_1T_PROX10 + tempo_no_segundo_tempo
    if tempo_efetivo_para_taxa <= 0 or escanteios_ocorridos < 0 or fim_intervalo_min <= inicio_intervalo_min: return None
    if tempo_efetivo_para_taxa == 0: taxa_por_minuto = 0.0
    else: taxa_por_minuto = escanteios_ocorridos / tempo_efetivo_para_taxa
    duracao_intervalo = fim_intervalo_min - inicio_intervalo_min
    lambda_intervalo = taxa_por_minuto * duracao_intervalo
    if lambda_intervalo > 700: prob_0 = 0.0
    else: prob_0 = math.exp(-lambda_intervalo)
    prob_1_ou_mais = 1.0 - prob_0
    odds_0 = calcular_odd(prob_0) # Reutiliza sua função calcular_odd
    odds_1_ou_mais = calcular_odd(prob_1_ou_mais) # Reutiliza sua função calcular_odd
    resultados = {
        "odds_justas_0_escanteios": odds_0, "odds_justas_1_ou_mais_escanteios": odds_1_ou_mais
    }
    return resultados

# --- NOVA Função para Calculadora de EV ---
def calcular_ev(odd_apostada, odd_justa):
    """Calcula o Valor Esperado (EV) com base nas odds fornecidas."""
    # Validação básica para evitar erros e resultados sem sentido
    if odd_apostada <= 1 or odd_justa <= 1: # Odds devem ser maiores que 1
         return None
    try:
        # A divisão por zero não deve ocorrer se odd_justa > 1, mas o try/except é seguro
        valor = (odd_apostada / odd_justa) - 1
        return valor
    except ZeroDivisionError:
        return None # Caso algo inesperado ocorra
    except Exception: # Captura outras exceções potenciais
        return None

# --- Interface Streamlit ---

st.set_page_config(layout="centered", page_title="CORNER ODDS V2 & EV Calc") # Atualiza o título
st.title("CORNER ODDS V2 & EV Calculator") # Atualiza o título principal

# --- Cria as Abas (Adicionando a terceira) ---
tab_final_jogo, tab_prox_10, tab_calculadora_ev = st.tabs([
    "Final do Tempo",
    "Próximos 10 Minutos",
    "Calculadora de EV" # Nova aba
])

# --- Conteúdo da Aba 1: Final do Jogo (MANTIDO COMO ESTÁ) ---
with tab_final_jogo:
    st.markdown("#### Cálculo para o restante do jogo") # Descrição da aba

    # Inputs para a calculadora de final de jogo
    esc_totais_ate_74_tab1 = st.number_input(
        "Escanteios TOTAIS:", min_value=0, step=1, value=5, key="final_esc_74_tab1"
    )
    diff_gols_75_tab1 = st.number_input(
        "Diferença de Gols:", step=1, value=0, key="final_diff_gols_tab1"
    )
    acr_2t_tab1 = st.number_input(
        "Acréscimos Previstos:", min_value=0, step=1, value=3, key="final_acr_tab1"
    )

    # Botão para a calculadora de final de jogo
    calcular_button_final_tab1 = st.button("Calcular Odds FINAIS", key="final_calcular_tab1")

    st.divider()

    # Lógica de exibição da calculadora de final de jogo
    if calcular_button_final_tab1:
        resultados_final = calcular_odds_segundo_tempo_total_ate_74(acr_2t_tab1, esc_totais_ate_74_tab1, diff_gols_75_tab1)
        range_exibicao_2t = range(82, 88) # Exibe minutos 82 a 87

        if resultados_final is not None:
            resultados_para_exibir = [res for res in resultados_final if res['minuto'] in range_exibicao_2t]
            if resultados_para_exibir:
                data_for_df = []
                for res in resultados_para_exibir:
                    minuto_2t = res['minuto']
                    minuto_1t = minuto_2t - 45
                    minuto_display = f"{minuto_1t}'/{minuto_2t}'"
                    odd_menos_0_5 = '-' if res['-0.5'] == float('inf') else f"{res['-0.5']:.2f}"
                    odd_exa_1 = '-' if res['Exa 1'] == float('inf') else f"{res['Exa 1']:.2f}"
                    odd_mais_0_5 = '-' if res['+0.5'] == float('inf') else f"{res['+0.5']:.2f}"
                    data_for_df.append({
                        'Min(1T/2T)': minuto_display, '-0.5': odd_menos_0_5, 'Exa 1': odd_exa_1, '+0.5': odd_mais_0_5
                    })
                df = pd.DataFrame(data_for_df)
                if not df.empty:
                    st.table(df.set_index('Min(1T/2T)'))
                else:
                    st.warning(f"Nenhum dado calculado para exibir no intervalo {min(range_exibicao_2t)}'-{max(range_exibicao_2t)-1}'.")
            else:
                 st.warning(f"Nenhum dado calculado caiu no intervalo de exibição ({min(range_exibicao_2t)}'-{max(range_exibicao_2t)-1}').")
        else:
            st.error("Não foi possível calcular as odds finais. Verifique os inputs.")

# --- Conteúdo da Aba 2: Próximos 10 Minutos (MANTIDO COMO ESTÁ) ---
with tab_prox_10:
    st.markdown("#### Próximos 10 Min") # Descrição da aba

    # Inputs para a calculadora de próximos 10 minutos
    col_prox1_tab2, col_prox2_tab2 = st.columns(2) # Colunas para layout
    with col_prox1_tab2:
        tempo_passado_prox10_tab2 = st.number_input(
            "Tempo decorrido (min):",
            min_value=0.1, value=15.0, step=0.5, format="%.1f", key="prox10_tempo_tab2",
            help="Minuto atual do jogo (ex: 15.5, 60.0)"
        )
    with col_prox2_tab2:
        escanteios_ate_agora_prox10_tab2 = st.number_input(
            "Escanteios ocorridos (Total):",
            min_value=0, value=1, step=1, format="%d", key="prox10_escanteios_tab2",
            help="Total de escanteios na partida até o tempo informado."
        )

    # Botão para a calculadora de próximos 10 minutos
    calcular_button_prox10_tab2 = st.button("Calcular Próximos 10 min", key="prox10_calcular_tab2")

    st.divider()

    # Lógica de exibição da calculadora de próximos 10 minutos
    if calcular_button_prox10_tab2:
        intervalo_inicio_prox10 = tempo_passado_prox10_tab2
        intervalo_fim_prox10 = tempo_passado_prox10_tab2 + 10.0

        calculo_prox10 = calcular_probabilidades_e_odds_poisson_prox10(
            tempo_passado_prox10_tab2, escanteios_ate_agora_prox10_tab2, intervalo_inicio_prox10, intervalo_fim_prox10
        )

        if calculo_prox10:
            odd0 = calculo_prox10['odds_justas_0_escanteios']
            odd1mais = calculo_prox10['odds_justas_1_ou_mais_escanteios']
            odd0_display = "-" if odd0 == float('inf') else f"{odd0:.2f}"
            odd1mais_display = "-" if odd1mais == float('inf') else f"{odd1mais:.2f}"

            # Exibe a linha de odds formatada
            st.markdown(f"+0,5: {odd1mais_display} | -0,5:  {odd0_display} ")
        else:
             st.error("Erro no cálculo para próximos 10 min.")


# --- Conteúdo da Aba 3: Calculadora de EV (NOVA ABA) ---
with tab_calculadora_ev:
    st.markdown("#### Calculadora de Valor Esperado (EV)") # Descrição
    st.markdown("""
    Insira a odd em que você apostou e a sua estimativa da odd justa
    para calcular o valor esperado da aposta. Ideal para comparar as odds
    calculadas nas outras abas com as odds do mercado.
    """)

    # Inputs usando colunas
    col_ev1, col_ev2 = st.columns(2)
    with col_ev1:
        # Input para a Odd oferecida pelo mercado/casa de apostas
        odd_apostada_ev = st.number_input(
            "Odd Apostada (Mercado):", # Label mais claro
            min_value=1.01,
            step=0.01,
            format="%.2f",
            value=1.85, # Exemplo diferente
            key="ev_odd_apostada", # Chave única
            help="A odd que a casa de apostas está oferecendo."
        )
    with col_ev2:
         # Input para a Odd Justa (pode vir da outra aba ou sua estimativa)
        odd_justa_ev = st.number_input(
            "Odd Justa Estimada:",
            min_value=1.01,
            step=0.01,
            format="%.2f",
            value=1.70, # Exemplo diferente
            key="ev_odd_justa", # Chave única
            help="Sua estimativa da odd correta (pode ser a calculada em outra aba)."
        )

    # Botão de cálculo para consistência
    calcular_ev_button = st.button("Calcular EV", key="ev_calcular")
    st.divider()

    if calcular_ev_button:
         # Cálculo e Exibição
         # Verifica se os inputs são válidos antes de chamar a função
         if odd_apostada_ev > 1 and odd_justa_ev > 1:
             ev_calculado = calcular_ev(odd_apostada_ev, odd_justa_ev)

             if ev_calculado is not None:
                 ev_percentual = ev_calculado * 100

                 # Usando st.metric para destaque
                 st.metric(label="Valor Esperado (EV)", value=f"{ev_percentual:.2f}%")

                 # Interpretação do resultado
                 if ev_calculado > 0:
                     st.success(f"**EV Positivo ({ev_percentual:.2f}%)**: Esta aposta tem valor!")
                 elif ev_calculado < 0:
                     st.warning(f"**EV Negativo ({ev_percentual:.2f}%)**: Esta aposta NÃO tem valor.")
                 else:
                     st.info("**EV Neutro (0.00%)**: Sem vantagem/desvantagem teórica.")
             else:
                 # Mensagem de erro se o cálculo falhar internamente (improvável com as validações)
                 st.error("Erro ao calcular o EV. Verifique os valores das odds.")
         else:
             # Mensagem se os inputs não atenderem ao min_value (já protegidos pelo widget, mas bom ter)
             st.warning("Por favor, insira odds válidas (maiores que 1.00).")


# Legenda final fora das abas
st.caption("Selecione a aba acima para o tipo de cálculo desejado.")
