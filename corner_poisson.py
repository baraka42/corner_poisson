# -*- coding: utf-8 -*-
import math
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURAÇÃO DA PÁGINA (EXISTENTE - SEM MUDANÇAS) ---
st.set_page_config(
    page_title="Corner Odds & EV Calc", # Título da aba do navegador
    page_icon="⚽",  # Ícone da aba (pode ser emoji ou path)
    layout="wide",   # Usar layout largo para um visual mais moderno
    initial_sidebar_state="auto" # Ou 'expanded'/'collapsed' se preferir
)

# --- CSS CUSTOMIZADO (EXISTENTE - SEM MUDANÇAS) ---
custom_css = """
<style>
    /* === GERAL === */
    .stApp { background-color: #1E1E1E; color: #D4D4D4; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    h1, h2, h3, h4, h5, h6 { color: #FFFFFF; }
    h1 { font-size: 2.5em; padding-bottom: 0.3em; }
    a { color: #9CDCFE; }
    /* --- COMPONENTES ESPECÍFICOS --- */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #444444; padding-bottom: 5px; }
    .stTabs [data-baseweb="tab"] { height: 40px; white-space: pre-wrap; background-color: #2D2D2D; color: #AAAAAA; border-radius: 4px 4px 0 0; border: none; transition: all 0.3s; padding: 0px 20px; }
    .stTabs [aria-selected="true"] { background-color: #3C3C3C; color: #FFFFFF; font-weight: bold; }
    .stTabs [data-baseweb="tab"]:hover { background-color: #3C3C3C; color: #FFFFFF; }
    .stButton>button { border: 1px solid #555555; border-radius: 5px; background-color: #3A3A3A; color: #E0E0E0; padding: 0.5em 1em; transition: all 0.2s ease-in-out; box-shadow: none; font-weight: 500; width: 100%; margin-top: 10px; }
    .stButton>button:hover { background-color: #4A4A4A; color: #FFFFFF; border-color: #777777; }
    .stButton>button:active { background-color: #2A2A2A; border-color: #555555; }
    .stButton>button:focus { outline: none !important; box-shadow: none !important; }
    .stNumberInput input, .stTextInput input { border: 1px solid #555555; background-color: #2D2D2D; color: #D4D4D4; border-radius: 5px; box-shadow: none; padding: 0.5em; }
    .stTable, .stDataFrame { border-collapse: collapse; width: 100%; background-color: #2D2D2D; border-radius: 5px; overflow: hidden; border: 1px solid #444444; margin-top: 1em; } /* Aplicado a st.dataframe também */
    .stTable th, .stDataFrame th { background-color: #3C3C3C; color: #FFFFFF; text-align: center; padding: 0.75em 0.5em; font-weight: 600; border-bottom: 1px solid #555555; }
    .stTable td, .stDataFrame td { color: #D4D4D4; padding: 0.6em 0.5em; border: none; text-align: center; border-bottom: 1px solid #444444; }
    .stTable tr:last-child td, .stDataFrame tr:last-child td { border-bottom: none; }
    .stTable tr:hover td, .stDataFrame tr:hover td { background-color: #383838; }
    .stTable td:first-child, .stTable th:first-child, .stDataFrame td:first-child, .stDataFrame th:first-child { text-align: left; padding-left: 15px; font-weight: 500; }
    [data-testid="stMetric"] { background-color: #2D2D2D; border: 1px solid #444444; border-radius: 5px; padding: 15px; text-align: center; }
    [data-testid="stMetricLabel"] { color: #AAAAAA; font-size: 0.9em; font-weight: 500; }
    [data-testid="stMetricValue"] { color: #FFFFFF; font-size: 1.8em; font-weight: 600; margin-top: 5px; margin-bottom: 5px; }
    [data-testid="stMetricDelta"] { font-size: 0.9em; font-weight: 500; }
    hr { border-top: 1px solid #444444; margin-top: 1.5em; margin-bottom: 1.5em; }
    .stCaption { color: #AAAAAA; font-size: 0.85em; text-align: center; margin-top: 2em; }
    .stAlert { border-radius: 5px; border: none; padding: 1em; box-shadow: none; }
    .stAlert[data-baseweb="alert"][kind="success"] { background-color: rgba(40, 167, 69, 0.2); color: #A8D5B3; }
    .stAlert[data-baseweb="alert"][kind="warning"] { background-color: rgba(255, 193, 7, 0.2); color: #FFE599; }
    .stAlert[data-baseweb="alert"][kind="error"] { background-color: rgba(220, 53, 69, 0.2); color: #F3A7AF; }
    .stAlert[data-baseweb="alert"][kind="info"] { background-color: rgba(23, 162, 184, 0.2); color: #A3E1EB; }
    .st-emotion-cache-1xw8zd0 { padding: 1rem; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- NOVA FUNÇÃO: SIMULAÇÃO DE WINRATE ---
def simulate_random_results(target_winrate, num_simulations):
    """Simula a taxa de vitória acumulada ao longo do tempo"""
    target_winrate /= 100.0  # Convert to decimal
    results = []
    
    # Simulate random results
    for _ in range(num_simulations):
        result = 1 if np.random.rand() < target_winrate else 0
        results.append(result)
    
    # Calculate cumulative winrate
    winrate_accumulated = np.cumsum(results) / np.arange(1, num_simulations + 1)
    
    return results, winrate_accumulated

# --- Funções de Cálculo (EXISTENTES - SEM MUDANÇAS) ---
# Função Poisson
def poisson(k, lambda_):
    # ... (código da função poisson existente) ...
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

# Função de ajuste para o FINAL do jogo
def ajustar_taxa_final_jogo(minuto_calculo, taxa_base_pre75, diferenca_gols_75):
    # ... (código da função ajustar_taxa_final_jogo existente) ...
    if minuto_calculo < 75: return taxa_base_pre75
    aumento_percentual = (0.0333 + 0.0037 * max(0, minuto_calculo - 75))
    if diferenca_gols_75 < 0: aumento_percentual += 0.05
    elif diferenca_gols_75 == 0: aumento_percentual += 0.03
    else: aumento_percentual -= 0.02
    taxa_ajustada = taxa_base_pre75 * (1 + max(-0.95, aumento_percentual))
    return max(0.0001, taxa_ajustada)

# Função interna comum para calcular odds
def calcular_odd(prob):
    # ... (código da função calcular_odd existente) ...
    if prob is None or prob <= 1e-9 or prob == float('inf'): return float('inf')
    if prob >= 0.9999: return 1.01
    try:
        odd = 1 / prob
        if odd > 9999: return float('inf')
        return max(1.01, round(odd, 2))
    except ZeroDivisionError:
        return float('inf')

# Função para calcular odds para o FINAL DO SEGUNDO TEMPO
def calcular_odds_segundo_tempo_total_ate_74(acrescimos_2t, escanteios_totais_ate_74, diferenca_gols_75):
    # ... (código da função calcular_odds_segundo_tempo_total_ate_74 existente) ...
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

# --- Constante e Função para a calculadora Próximos 10 min ---
ACRESCIMO_PADRAO_1T_PROX10 = 3.0

def calcular_probabilidades_e_odds_poisson_prox10(tempo_decorrido_min, escanteios_ocorridos, inicio_intervalo_min, fim_intervalo_min):
    """Calcula odds para os próximos 10 min (versão interna, com ajuste de tempo)."""
    # ... (código da função calcular_probabilidades_e_odds_poisson_prox10 existente) ...
    tempo_efetivo_para_taxa = tempo_decorrido_min
    if tempo_decorrido_min >= 46.0:
        tempo_no_segundo_tempo = tempo_decorrido_min - 45.0
        tempo_efetivo_para_taxa = 45.0 + ACRESCIMO_PADRAO_1T_PROX10 + tempo_no_segundo_tempo
    if tempo_efetivo_para_taxa <= 0 or escanteios_ocorridos < 0 or fim_intervalo_min <= inicio_intervalo_min: return None
    try: # Adicionado try-except para segurança na divisão
        taxa_por_minuto = escanteios_ocorridos / tempo_efetivo_para_taxa
    except ZeroDivisionError:
         taxa_por_minuto = 0.0
    duracao_intervalo = fim_intervalo_min - inicio_intervalo_min
    lambda_intervalo = taxa_por_minuto * duracao_intervalo
    if lambda_intervalo > 700: prob_0 = 0.0
    else: prob_0 = math.exp(-lambda_intervalo)
    prob_1_ou_mais = 1.0 - prob_0
    odds_0 = calcular_odd(prob_0)
    odds_1_ou_mais = calcular_odd(prob_1_ou_mais)
    resultados = {
        "odds_justas_0_escanteios": odds_0, "odds_justas_1_ou_mais_escanteios": odds_1_ou_mais
    }
    return resultados

# --- Função para Calculadora de EV (EXISTENTE - SEM MUDANÇAS) ---
def calcular_ev(odd_apostada, odd_justa):
    """Calcula o Valor Esperado (EV) com base nas odds fornecidas."""
    if odd_apostada <= 1 or odd_justa <= 1:
        return None
    try:
        valor = (odd_apostada / odd_justa) - 1
        return valor
    except ZeroDivisionError:
        return None
    except Exception:
        return None

# --- NOVA FUNÇÃO PARA CALCULAR ODDS PRIMEIRO TEMPO (ADICIONADA) ---
def calcular_odds_primeiro_tempo(minuto_atual_1t, escanteios_ate_minuto_atual, acrescimos_1t):
    """
    Calcula as odds de escanteios para o restante do primeiro tempo.
    Assume taxa constante a partir do minuto atual.
    """
    resultados = []
    # Validações básicas
    if minuto_atual_1t <= 0 or minuto_atual_1t > 45 or escanteios_ate_minuto_atual < 0 or acrescimos_1t < 0:
        return []

    try:
        taxa_base_1t = escanteios_ate_minuto_atual / minuto_atual_1t
    except ZeroDivisionError:
        taxa_base_1t = 0.01
    taxa_base_1t = max(0.001, taxa_base_1t)

    minuto_final_1t = 45.0 + float(acrescimos_1t)
    minuto_inicial_loop = math.ceil(minuto_atual_1t)

    for minuto_loop in range(int(minuto_inicial_loop), int(minuto_final_1t) + 1):
        tempo_restante = minuto_final_1t - minuto_loop
        if tempo_restante < 0:
             continue

        taxa_para_periodo = taxa_base_1t # Taxa constante
        lambda_ = taxa_para_periodo * tempo_restante
        if lambda_ < 0: lambda_ = 0

        p0 = poisson(0, lambda_)
        p1 = poisson(1, lambda_)
        p_mais_0_5 = max(0.0, 1.0 - p0)
        resultados.append({
            'minuto': minuto_loop,
            '-0.5': calcular_odd(p0),
            'Exa 1': calcular_odd(p1),
            '+0.5': calcular_odd(p_mais_0_5)
        })
    return resultados

# --- Interface Streamlit ---

st.title("Corner Calculador") # Título principal mantido

# --- Cria as Abas (MODIFICADO PARA ADICIONAR A NOVA ABA) ---
tab_1tempo, tab_final_jogo, tab_prox_10, tab_calculadora_ev, tab_winrate_sim = st.tabs([
    "⏱️ HT",
    "🏁 FT",
    "📊 10 Min",
    "💰 EV Calc",
    "🎯 Winrate Sim"  # NOVA ABA ADICIONADA
])

# --- CONTEÚDO DA ABA 1: PRIMEIRO TEMPO (EXISTENTE) ---
with tab_1tempo:
    st.markdown("##### Calculadora de Odds HT")

    col_1t_1, col_1t_2, col_1t_3 = st.columns(3)
    with col_1t_1:
        minuto_atual_1t_input = st.number_input(
            "Minuto Atual (HT):",
            min_value=0.1, max_value=45.0, value=30.0, step=0.5, format="%.1f",
            key="1t_minuto_atual",
            help="Minuto exato no primeiro tempo (ex: 30.5 para 30:30)."
        )
    with col_1t_2:
        escanteios_1t_input = st.number_input(
            "Escanteios Total (HT):",
            min_value=0, step=1, value=3, format="%d",
            key="1t_escanteios_atual",
            help="Total de escanteios na partida até o minuto informado."
        )
    with col_1t_3:
        acrescimos_1t_input = st.number_input(
            "Acréscimos (HT):",
            min_value=0, step=1, value=2, format="%d",
            key="1t_acrescimos",
            help="Estimativa de acréscimos para o primeiro tempo."
        )

    calcular_button_1t = st.button("Calcular Odds HT", key="1t_calcular")
    st.divider()

    if calcular_button_1t:
        resultados_1t = calcular_odds_primeiro_tempo(
            minuto_atual_1t_input, escanteios_1t_input, acrescimos_1t_input
        )

        range_exibicao_1t = range(38, 43)

        if resultados_1t:
            resultados_para_exibir_1t = [res for res in resultados_1t if res['minuto'] in range_exibicao_1t]
            if resultados_para_exibir_1t:
                data_for_df_1t = []
                for res in resultados_para_exibir_1t:
                    minuto_display = f"{res['minuto']}'"
                    odd_menos_0_5 = "∞" if res['-0.5'] == float('inf') else f"{res['-0.5']:.2f}"
                    odd_exa_1 = "∞" if res['Exa 1'] == float('inf') else f"{res['Exa 1']:.2f}"
                    odd_mais_0_5 = "∞" if res['+0.5'] == float('inf') else f"{res['+0.5']:.2f}"
                    data_for_df_1t.append({
                        'Minuto (HT)': minuto_display,
                        '-0.5': odd_menos_0_5,
                        'Exato 1': odd_exa_1,
                        '+0.5': odd_mais_0_5
                    })
                df_1t = pd.DataFrame(data_for_df_1t)
                if not df_1t.empty:
                    st.dataframe(df_1t.set_index('Minuto (HT)'), use_container_width=True)
                else:
                     st.info(f"Nenhum dado calculado para exibir no intervalo 38' - 42'.")
            else:
                st.info(f"Nenhum dado calculado caiu no intervalo de exibição (38' - 42'). Verifique os inputs.")
        else:
            st.warning("Não foi possível calcular as odds para o primeiro tempo. Verifique os inputs (minuto deve ser <= 45).")

# --- Conteúdo da Aba 2: Final do Jogo (EXISTENTE) ---
with tab_final_jogo:
    st.markdown("##### Calculadora de Odds FT")

    col_final1, col_final2, col_final3 = st.columns(3)
    with col_final1:
        esc_totais_ate_74_tab1 = st.number_input(
            "Escanteios Total", min_value=0, step=1, value=5, key="final_esc_74_tab1"
        )
    with col_final2:
        diff_gols_75_tab1 = st.number_input(
            "Diferença Gols", step=1, value=0, key="final_diff_gols_tab1",
             help="Gols do seu time - Gols do adversário no minuto 75"
        )
    with col_final3:
        acr_2t_tab1 = st.number_input(
            "Acréscimos (FT)", min_value=0, step=1, value=3, key="final_acr_tab1",
             help="Estimativa de acréscimos no 2º Tempo"
        )

    calcular_button_final_tab1 = st.button("Calcular Odds FT", key="final_calcular_tab1")
    st.divider()

    if calcular_button_final_tab1:
        resultados_final = calcular_odds_segundo_tempo_total_ate_74(acr_2t_tab1, esc_totais_ate_74_tab1, diff_gols_75_tab1)
        range_exibicao_2t = range(82, 88)

        if resultados_final:
            resultados_para_exibir = [res for res in resultados_final if res['minuto'] in range_exibicao_2t]
            if resultados_para_exibir:
                data_for_df = []
                for res in resultados_para_exibir:
                    minuto_2t = res['minuto']
                    minuto_display = f"{minuto_2t}'"
                    odd_menos_0_5 = '∞' if res['-0.5'] == float('inf') else f"{res['-0.5']:.2f}"
                    odd_exa_1 = '∞' if res['Exa 1'] == float('inf') else f"{res['Exa 1']:.2f}"
                    odd_mais_0_5 = '∞' if res['+0.5'] == float('inf') else f"{res['+0.5']:.2f}"
                    data_for_df.append({
                        'Minuto (FT)': minuto_display, '-0.5': odd_menos_0_5, 'Exato 1': odd_exa_1, '+0.5': odd_mais_0_5
                    })
                df = pd.DataFrame(data_for_df)
                if not df.empty:
                    st.dataframe(df.set_index('Minuto (FT)'), use_container_width=True)
                else:
                    st.info(f"Nenhum dado calculado para exibir no intervalo {min(range_exibicao_2t)}' - {max(range_exibicao_2t)}'.")
            else:
                 st.info(f"Nenhum dado calculado caiu no intervalo de exibição ({min(range_exibicao_2t)}' - {max(range_exibicao_2t)}').")
        else:
            st.error("Não foi possível calcular as odds finais. Verifique os inputs.")

# --- Conteúdo da Aba 3: Próximos 10 Minutos (EXISTENTE) ---
with tab_prox_10:
    st.markdown("##### Calculadora de Odds para os Próximos 10 Minutos")

    col_prox1_tab2, col_prox2_tab2 = st.columns(2)
    with col_prox1_tab2:
        tempo_passado_prox10_tab2 = st.number_input(
            "Tempo Decorrido (min):",
            min_value=0.1, value=15.0, step=0.5, format="%.1f", key="prox10_tempo_tab2",
            help="Minuto atual do jogo (ex: 15.5 para 15:30, 60.0 para 60:00)"
        )
    with col_prox2_tab2:
        escanteios_ate_agora_prox10_tab2 = st.number_input(
            "Escanteios Ocorridos (Total):",
            min_value=0, value=1, step=1, format="%d", key="prox10_escanteios_tab2",
            help="Total de escanteios na partida até o tempo informado."
        )

    calcular_button_prox10_tab2 = st.button("Calcular Próximos 10 min", key="prox10_calcular_tab2")
    st.divider()

    if calcular_button_prox10_tab2:
        intervalo_inicio_prox10 = tempo_passado_prox10_tab2
        intervalo_fim_prox10 = tempo_passado_prox10_tab2 + 10.0

        calculo_prox10 = calcular_probabilidades_e_odds_poisson_prox10(
            tempo_passado_prox10_tab2, escanteios_ate_agora_prox10_tab2, intervalo_inicio_prox10, intervalo_fim_prox10
        )

        if calculo_prox10:
            odd0 = calculo_prox10['odds_justas_0_escanteios']
            odd1mais = calculo_prox10['odds_justas_1_ou_mais_escanteios']
            odd0_display = "∞" if odd0 == float('inf') else f"{odd0:.2f}"
            odd1mais_display = "∞" if odd1mais == float('inf') else f"{odd1mais:.2f}"

            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric(label="Odd Justa +0.5 Escanteios", value=odd1mais_display)
            with col_res2:
                st.metric(label="Odd Justa -0.5 Escanteios (Exato 0)", value=odd0_display)
        else:
            st.error("Erro no cálculo para próximos 10 min. Verifique os inputs.")

# --- Conteúdo da Aba 4: Calculadora de EV (EXISTENTE) ---
with tab_calculadora_ev:
    st.markdown("##### Calculadora de Valor Esperado (EV)")
    st.markdown("""
    Insira a odd oferecida pelo mercado e a sua estimativa da odd justa
    para calcular o valor esperado (EV) da aposta. Um EV positivo sugere uma aposta de valor.
    """)

    col_ev1, col_ev2 = st.columns(2)
    with col_ev1:
        odd_apostada_ev = st.number_input(
            "Odd Oferecida (Mercado):",
            min_value=1.01, step=0.01, format="%.2f", value=1.85,
            key="ev_odd_apostada",
            help="A odd que a casa de apostas está oferecendo."
        )
    with col_ev2:
        odd_justa_ev = st.number_input(
            "Sua Odd Justa Estimada:",
            min_value=1.01, step=0.01, format="%.2f", value=1.70,
            key="ev_odd_justa",
            help="Sua estimativa da odd correta (pode ser a calculada em outra aba)."
        )

    calcular_ev_button = st.button("Calcular EV", key="ev_calcular")
    st.divider()

    if calcular_ev_button:
        if odd_apostada_ev > 1 and odd_justa_ev > 1:
            ev_calculado = calcular_ev(odd_apostada_ev, odd_justa_ev)

            if ev_calculado is not None:
                ev_percentual = ev_calculado * 100
                st.metric(label="Valor Esperado (EV)", value=f"{ev_percentual:.2f}%")
                if ev_calculado > 0.01:
                    st.success(f"**EV Positivo ({ev_percentual:.2f}%)**: ✅ Aposta com valor encontrado!")
                elif ev_calculado < -0.01:
                    st.error(f"**EV Negativo ({ev_percentual:.2f}%)**: ❌ Evite esta aposta.")
                else:
                    st.info("**EV Próximo de Zero**: ⚖️ Aposta neutra, sem vantagem clara.")
            else:
                st.error("Erro ao calcular o EV. Verifique as odds inseridas.")
        else:
            st.warning("Por favor, insira odds válidas (maiores que 1.00) em ambos os campos.")

# --- NOVA ABA: SIMULAÇÃO DE WINRATE ---
with tab_winrate_sim:
    st.markdown("##### 🎯 Simulador de Taxa de Vitória")
    st.markdown("Esta ferramenta simula a taxa de vitória acumulada ao longo do tempo para entender a variação natural dos resultados.")
    
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    with col_sim1:
        winrate_target = st.slider(
            "Taxa de Vitória Alvo (%)", 
            min_value=1.0, 
            max_value=99.0, 
            value=47.5, 
            step=0.5,
            help="Taxa de vitória esperada em porcentagem"
        )
    with col_sim2:
        num_simulations = st.slider(
            "Número de Simulações", 
            min_value=10, 
            max_value=5000,
            value=1000,
            step=100,
            help="Número total de jogos/tentativas a simular"
        )
    with col_sim3:
        auto_run = st.checkbox("Executar automaticamente", value=True)
    
    if num_simulations > 10000:
        st.warning("⚠️ Simulações acima de 10.000 podem demorar alguns segundos para processar.")
    
    run_simulation = st.button("Executar Simulação")
    
    if run_simulation or auto_run:
        # Mostrar parâmetros
        st.subheader("Parâmetros da Simulação")
        col_param1, col_param2 = st.columns(2)
        with col_param1:
            st.metric("Taxa de Vitória Alvo", f"{winrate_target}%")
        with col_param2:
            st.metric("Número de Simulações", f"{num_simulations:,}".replace(",", "."))
        
        # Barra de progresso para simulações grandes
        if num_simulations > 5000:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Executar simulação
        results = []
        for i in range(num_simulations):
            result = 1 if np.random.rand() < (winrate_target / 100.0) else 0
            results.append(result)
            
            if num_simulations > 5000 and i % 1000 == 0:
                progress_bar.progress((i + 1) / num_simulations)
                status_text.text(f"Simulando... {i+1}/{num_simulations}")
        
        winrate_accumulated = np.cumsum(results) / np.arange(1, num_simulations + 1)
        
        if num_simulations > 5000:
            progress_bar.empty()
            status_text.empty()
        
        # Calcular estatísticas
        final_winrate = winrate_accumulated[-1] * 100
        total_wins = sum(results)
        total_losses = num_simulations - total_wins
        
        # Mostrar estatísticas
        st.subheader("Resultados da Simulação")
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        with col_stats1:
            st.metric("Vitórias", f"{total_wins:,}".replace(",", "."))
        with col_stats2:
            st.metric("Derrotas", f"{total_losses:,}".replace(",", "."))
        with col_stats3:
            st.metric("Winrate Final", f"{final_winrate:.2f}%")
        
        # Criar e mostrar o gráfico - VERSÃO ELEGANTE E MINIMALISTA
        st.subheader("Evolução da Taxa de Vitória")
        
        # Otimização para muitas simulações
        if num_simulations > 1000:
            step = max(1, num_simulations // 500)  # Menos pontos para mais minimalismo
            indices = range(0, num_simulations, step)
            sampled_winrate = winrate_accumulated[indices] * 100
            sampled_indices = [i + 1 for i in indices]
        else:
            sampled_winrate = winrate_accumulated * 100
            sampled_indices = range(1, num_simulations + 1)
        
        # Configuração do gráfico minimalista
        fig, ax = plt.subplots(figsize=(8, 4))  # 🔥 Tamanho menor e mais proporcional
        
        # Linha principal - mais suave e elegante
        ax.plot(sampled_indices, sampled_winrate, 
                linewidth=1.2, 
                color='#00D4AA',  # Verde água moderno
                alpha=0.9,
                label=f"Winrate Real ({final_winrate:.1f}%)")
        
        # Linha de target - mais discreta
        ax.axhline(y=winrate_target, 
                  color='#FF6B6B', 
                  linestyle='--', 
                  linewidth=1.5,
                  alpha=0.8,
                  label=f"Target ({winrate_target}%)")
        
        # Configurações minimalistas do gráfico
        ax.set_xlabel("Número de Simulações", fontsize=10, color='#CCCCCC', labelpad=10)
        ax.set_ylabel("Winrate (%)", fontsize=10, color='#CCCCCC', labelpad=10)
        
        # Título mais discreto
        ax.set_title(f"Evolução do Winrate • {num_simulations:,} simulações".replace(",", "."), 
                    fontsize=12, color='#FFFFFF', pad=15)
        
        # Legendas mais clean
        ax.legend(loc='upper right', framealpha=0.2, fontsize=9)
        
        # Grid muito sutil
        ax.grid(True, alpha=0.1, linestyle='-', linewidth=0.5)
        
        # Configuração de cores para tema escuro
        ax.set_facecolor('#1E1E1E')
        fig.patch.set_facecolor('#1E1E1E')
        
        # Configuração dos eixos
        ax.tick_params(colors='#AAAAAA', labelsize=9)
        ax.spines['bottom'].set_color('#444444')
        ax.spines['left'].set_color('#444444')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Zoom inteligente no eixo Y
        y_margin = max(5, winrate_target * 0.15)  # Margem dinâmica
        ax.set_ylim(max(0, winrate_target - y_margin), 
                   min(100, winrate_target + y_margin))
        
        # Formatação do eixo X para números grandes
        if num_simulations > 10000:
            ax.ticklabel_format(style='plain', axis='x', useOffset=False)
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'.replace(",", ".")))
        
        # Layout tight para evitar espaços desnecessários
        plt.tight_layout()
        
        # Exibir o gráfico no Streamlit
        st.pyplot(fig, use_container_width=False)  # 🔥 IMPORTANTE: não usar container width
        
        # Estatísticas adicionais (opcional)
        if num_simulations > 5000:
            with st.expander("📈 Estatísticas Avançadas"):
                std_dev = np.std(winrate_accumulated) * 100
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Desvio Padrão", f"{std_dev:.2f}%")
                    st.metric("Winrate Máximo", f"{np.max(winrate_accumulated) * 100:.2f}%")
                with col2:
                    # Tempo para convergência
                    convergence_threshold = 1.0
                    convergence_point = next((i + 1 for i, wr in enumerate(winrate_accumulated) 
                                            if abs(wr * 100 - winrate_target) <= convergence_threshold), None)
                    if convergence_point:
                        st.metric("Convergência (<1%)", f"{convergence_point:,}".replace(",", "."))
                    st.metric("Winrate Mínimo", f"{np.min(winrate_accumulated) * 100:.2f}%")
        
        # Explicação minimalista
        with st.expander("💡 Como interpretar"):
            st.markdown(f"""
            **📊 Resultado da Simulação**
            - **Winrate Final**: `{final_winrate:.2f}%` vs Target: `{winrate_target}%`
            - **Diferença**: `{abs(final_winrate - winrate_target):.2f}%`
            - **Volume**: `{num_simulations:,}` simulações
            
            **🎯 Insights**
            - **Curto Prazo**: Variação natural é esperada
            - **Longo Prazo**: Tendência ao valor esperado
            - **Aplicação**: Estratégias precisam de volume para validar edge
            
            *Lei dos Grandes Números em ação* 🔄
            """.replace(",", "."))

# --- Legenda Final (EXISTENTE) ---
baraka_image_url = "https://www.giantbomb.com/a/uploads/original/0/2218/459266-barakarender.gif"

st.markdown(
    f"""
    <div style="text-align: center; color: #AAAAAA; font-size: 0.85em; margin-top: 2em;">
        <img src="{baraka_image_url}" height="90px" style="vertical-align: middle; margin-right: 8px; border-radius: 3px;"> 
        Desenvolvido por Baraka#91 - @BarakaUP on Telegram
    </div>
    """,
    unsafe_allow_html=True
)