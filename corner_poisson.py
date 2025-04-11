import math
import streamlit as st
import pandas as pd
# import locale # Pode ser removido se não usar formatação específica de locale

# --- CONFIGURAÇÃO DA PÁGINA (ADICIONADO) ---
# Deve ser o primeiro comando Streamlit no seu script
st.set_page_config(
    page_title="Corner Odds & EV Calc", # Título da aba do navegador
    page_icon="⚽",  # Ícone da aba (pode ser emoji ou path)
    layout="wide",   # Usar layout largo para um visual mais moderno
    initial_sidebar_state="auto" # Ou 'expanded'/'collapsed' se preferir
)

# --- CSS CUSTOMIZADO (ADICIONADO) ---
custom_css = """
<style>
    /* === GERAL === */
    /* Cor de fundo principal e texto */
    .stApp {
        background-color: #1E1E1E; /* Cinza bem escuro (VS Code dark) */
        color: #D4D4D4; /* Texto principal - cinza claro */
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; /* Fonte limpa */
    }

    /* Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF; /* Títulos brancos */
    }
    h1 { /* Título principal maior */
      font-size: 2.5em;
      padding-bottom: 0.3em;
    }

    /* Links (se houver) */
    a {
        color: #9CDCFE; /* Azul claro para links */
    }

    /* --- COMPONENTES ESPECÍFICOS --- */

    /* Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; /* Espaço entre os botões das abas */
        border-bottom: 1px solid #444444; /* Linha sutil abaixo das abas */
        padding-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #2D2D2D; /* Fundo da aba inativa */
        color: #AAAAAA; /* Texto da aba inativa */
        border-radius: 4px 4px 0 0; /* Cantos arredondados só em cima */
        border: none; /* Sem borda padrão */
        transition: all 0.3s;
        padding: 0px 20px; /* Espaçamento interno */
    }
    .stTabs [aria-selected="true"] {
        background-color: #3C3C3C; /* Fundo da aba ativa */
        color: #FFFFFF; /* Texto da aba ativa (branco) */
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab"]:hover {
         background-color: #3C3C3C; /* Fundo ao passar mouse */
         color: #FFFFFF;
    }

    /* Botões - Estilo Flat/2D */
    .stButton>button {
        border: 1px solid #555555; /* Borda sutil cinza */
        border-radius: 5px;
        background-color: #3A3A3A; /* Fundo do botão */
        color: #E0E0E0;
        padding: 0.5em 1em;
        transition: all 0.2s ease-in-out;
        box-shadow: none;
        font-weight: 500; /* Peso da fonte */
        width: 100%; /* Ocupar largura da coluna/container */
        margin-top: 10px; /* Espaço acima do botão */
    }
    .stButton>button:hover {
        background-color: #4A4A4A;
        color: #FFFFFF;
        border-color: #777777;
    }
    .stButton>button:active {
        background-color: #2A2A2A;
        border-color: #555555;
    }
    .stButton>button:focus {
        outline: none !important;
        box-shadow: none !important;
    }


    /* Inputs (NumberInput, TextInput) */
    .stNumberInput input, .stTextInput input {
        border: 1px solid #555555;
        background-color: #2D2D2D;
        color: #D4D4D4;
        border-radius: 5px;
        box-shadow: none;
        padding: 0.5em; /* Ajuste padding */
    }
    /* Estilo para os botões +/- do number input (se necessário) */
    /* .stNumberInput button { background-color: #444; color: #FFF; } */

    /* Tabela (st.table) */
    .stTable {
        border-collapse: collapse; /* Remove espaços entre células */
        width: 100%;
        background-color: #2D2D2D; /* Fundo da área da tabela */
        border-radius: 5px;
        overflow: hidden; /* Garante que o border-radius funcione */
        border: 1px solid #444444;
        margin-top: 1em; /* Espaço acima da tabela */
    }
    .stTable th { /* Cabeçalho da tabela */
        background-color: #3C3C3C; /* Fundo do cabeçalho */
        color: #FFFFFF;
        text-align: center; /* Centralizar texto do cabeçalho */
        padding: 0.75em 0.5em;
        font-weight: 600;
        border-bottom: 1px solid #555555;
    }
    .stTable td { /* Células da tabela */
        color: #D4D4D4;
        padding: 0.6em 0.5em;
        border: none; /* Remover bordas internas */
        text-align: center; /* Centralizar conteúdo */
        border-bottom: 1px solid #444444; /* Linha sutil entre linhas */
    }
    .stTable tr:last-child td { /* Remove a borda da última linha */
         border-bottom: none;
    }
    .stTable tr:hover td { /* Efeito hover nas linhas */
        background-color: #383838;
    }
    /* Primeira coluna (Minutos) com alinhamento à esquerda se preferir */
     .stTable td:first-child, .stTable th:first-child {
        text-align: left;
        padding-left: 15px;
         font-weight: 500; /* Leve destaque */
     }


    /* Métricas (st.metric) */
    [data-testid="stMetric"] {
        background-color: #2D2D2D;
        border: 1px solid #444444;
        border-radius: 5px;
        padding: 15px;
        text-align: center; /* Centraliza todo o conteúdo da métrica */
    }
    [data-testid="stMetricLabel"] {
        color: #AAAAAA; /* Cor do label mais suave */
        font-size: 0.9em;
        font-weight: 500;
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF; /* Valor principal em branco */
        font-size: 1.8em; /* Tamanho maior para o valor */
        font-weight: 600;
        margin-top: 5px;
        margin-bottom: 5px;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.9em;
        font-weight: 500;
    }
    /* Cores específicas para delta positivo/negativo (padrão já funciona bem no dark) */
    /* [data-testid="stMetricDelta"] > div[data-delta-direction="positive"] { color: #4CAF50; } */
    /* [data-testid="stMetricDelta"] > div[data-delta-direction="negative"] { color: #F44336; } */


    /* Divisor (st.divider) */
    hr {
        border-top: 1px solid #444444; /* Linha divisória mais sutil */
        margin-top: 1.5em; /* Mais espaço antes/depois */
        margin-bottom: 1.5em;
    }

    /* Legenda (st.caption) */
    .stCaption {
        color: #AAAAAA; /* Cor mais suave para legendas */
        font-size: 0.85em;
        text-align: center;
        margin-top: 2em;
    }

    /* Alertas (Success, Warning, Error, Info) */
    .stAlert {
        border-radius: 5px;
        border: none; /* Remove borda padrão */
        padding: 1em; /* Espaçamento interno */
        box-shadow: none; /* Sem sombra */
    }
    /* Cores customizadas para os alertas */
    .stAlert[data-baseweb="alert"][kind="success"] { background-color: rgba(40, 167, 69, 0.2); color: #A8D5B3; }
    .stAlert[data-baseweb="alert"][kind="warning"] { background-color: rgba(255, 193, 7, 0.2); color: #FFE599; }
    .stAlert[data-baseweb="alert"][kind="error"] { background-color: rgba(220, 53, 69, 0.2); color: #F3A7AF; }
    .stAlert[data-baseweb="alert"][kind="info"] { background-color: rgba(23, 162, 184, 0.2); color: #A3E1EB; }

    /* --- AJUSTES DE LAYOUT --- */
    /* Adiciona um pouco de padding nas colunas para não colar nas bordas */
     .st-emotion-cache-1xw8zd0 { /* Seletor pode mudar em futuras versões do Streamlit */
        padding: 1rem;
     }

    /* Esconder o menu "Made with Streamlit" (opcional) */
     #MainMenu {visibility: hidden;}
     footer {visibility: hidden;}
     header {visibility: hidden;} /* Esconde o cabeçalho que pode aparecer com o menu */


</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# --- Funções de Cálculo (Mantidas como no seu código original) ---
# Função Poisson
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

# Função de ajuste para o FINAL do jogo
def ajustar_taxa_final_jogo(minuto_calculo, taxa_base_pre75, diferenca_gols_75):
    # ... (seu código completo da função ajustar_taxa_final_jogo) ...
    if minuto_calculo < 75: return taxa_base_pre75
    aumento_percentual = (0.0333 + 0.0037 * max(0, minuto_calculo - 75))
    if diferenca_gols_75 < 0: aumento_percentual += 0.05
    elif diferenca_gols_75 == 0: aumento_percentual += 0.03
    else: aumento_percentual -= 0.02
    taxa_ajustada = taxa_base_pre75 * (1 + max(-0.95, aumento_percentual))
    return max(0.0001, taxa_ajustada)


# Função interna comum para calcular odds
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

# Função para calcular odds para o FINAL DO SEGUNDO TEMPO
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

# --- Constante e Função para a calculadora Próximos 10 min ---
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
    if odd_apostada <= 1 or odd_justa <= 1:
        return None
    try:
        valor = (odd_apostada / odd_justa) - 1
        return valor
    except ZeroDivisionError:
        return None
    except Exception:
        return None

# --- Interface Streamlit ---

# st.set_page_config(layout="centered", page_title="CORNER ODDS V2 & EV Calc") # Removido daqui e colocado no topo
st.title("CORNER ODDS V2 & EV Calculator") # Título principal mantido

# --- Cria as Abas ---
tab_final_jogo, tab_prox_10, tab_calculadora_ev = st.tabs([
    "🏁 Final do Tempo", # Emojis para um toque visual
    "⏱️ Próximos 10 Min",
    "💰 Calculadora de EV"
])

# --- Conteúdo da Aba 1: Final do Jogo ---
with tab_final_jogo:
    st.markdown("##### Calculadora de Odds para o Final do Jogo") # Nível de cabeçalho ajustado

    # Inputs com colunas para melhor layout
    col_final1, col_final2, col_final3 = st.columns(3)
    with col_final1:
        esc_totais_ate_74_tab1 = st.number_input(
            "Escanteios até 74'", min_value=0, step=1, value=5, key="final_esc_74_tab1"
        )
    with col_final2:
        diff_gols_75_tab1 = st.number_input(
            "Diferença Gols (75')", step=1, value=0, key="final_diff_gols_tab1",
             help="Gols do seu time - Gols do adversário no minuto 75"
        )
    with col_final3:
        acr_2t_tab1 = st.number_input(
            "Acréscimos 2T", min_value=0, step=1, value=3, key="final_acr_tab1",
             help="Estimativa de acréscimos no 2º Tempo"
        )

    calcular_button_final_tab1 = st.button("Calcular Odds Finais", key="final_calcular_tab1")
    st.divider()

    if calcular_button_final_tab1:
        resultados_final = calcular_odds_segundo_tempo_total_ate_74(acr_2t_tab1, esc_totais_ate_74_tab1, diff_gols_75_tab1)
        range_exibicao_2t = range(82, 88)

        if resultados_final: # Simplificado
            resultados_para_exibir = [res for res in resultados_final if res['minuto'] in range_exibicao_2t]
            if resultados_para_exibir:
                data_for_df = []
                for res in resultados_para_exibir:
                    minuto_2t = res['minuto']
                    # minuto_1t = minuto_2t - 45 # Pode ser omitido se só mostrar o minuto do 2T
                    # minuto_display = f"{minuto_1t}'/{minuto_2t}'"
                    minuto_display = f"{minuto_2t}'" # Exibir apenas minuto do 2T
                    odd_menos_0_5 = '-' if res['-0.5'] == float('inf') else f"{res['-0.5']:.2f}"
                    odd_exa_1 = '-' if res['Exa 1'] == float('inf') else f"{res['Exa 1']:.2f}"
                    odd_mais_0_5 = '-' if res['+0.5'] == float('inf') else f"{res['+0.5']:.2f}"
                    data_for_df.append({
                        'Minuto (2T)': minuto_display, '-0.5': odd_menos_0_5, 'Exato 1': odd_exa_1, '+0.5': odd_mais_0_5
                    })
                df = pd.DataFrame(data_for_df)
                if not df.empty:
                     # Usar st.dataframe para mais interatividade ou manter st.table
                    st.dataframe(df.set_index('Minuto (2T)'), use_container_width=True) # use_container_width adapta à largura
                    # st.table(df.set_index('Minuto (2T)')) # Alternativa mais simples
                else:
                    st.info(f"Nenhum dado calculado para exibir no intervalo {min(range_exibicao_2t)}' - {max(range_exibicao_2t)}'.") # Usando st.info
            else:
                 st.info(f"Nenhum dado calculado caiu no intervalo de exibição ({min(range_exibicao_2t)}' - {max(range_exibicao_2t)}').")
        else:
            st.error("Não foi possível calcular as odds finais. Verifique os inputs.")

# --- Conteúdo da Aba 2: Próximos 10 Minutos ---
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
            odd0_display = "∞" if odd0 == float('inf') else f"{odd0:.2f}" # Usando ∞ para infinito
            odd1mais_display = "∞" if odd1mais == float('inf') else f"{odd1mais:.2f}"

            # Usando st.metric para um visual mais interessante
            col_res1, col_res2 = st.columns(2)
            with col_res1:
                st.metric(label="Odd Justa +0.5 Escanteios", value=odd1mais_display)
            with col_res2:
                st.metric(label="Odd Justa -0.5 Escanteios (Exato 0)", value=odd0_display)

            # st.markdown(f"**+0.5:** {odd1mais_display}  |  **-0.5:** {odd0_display}") # Alternativa
        else:
            st.error("Erro no cálculo para próximos 10 min. Verifique os inputs.")

# --- Conteúdo da Aba 3: Calculadora de EV ---
with tab_calculadora_ev:
    st.markdown("##### Calculadora de Valor Esperado (EV)")
    st.markdown("""
    Insira a odd oferecida pelo mercado e a sua estimativa da odd justa
    para calcular o valor esperado (EV) da aposta. Um EV positivo sugere uma aposta de valor.
    """)

    col_ev1, col_ev2 = st.columns(2)
    with col_ev1:
        odd_apostada_ev = st.number_input(
            "Odd Oferecida (Mercado):", # Label ligeiramente alterado
            min_value=1.01, step=0.01, format="%.2f", value=1.85,
            key="ev_odd_apostada",
            help="A odd que a casa de apostas está oferecendo."
        )
    with col_ev2:
        odd_justa_ev = st.number_input(
            "Sua Odd Justa Estimada:", # Label ligeiramente alterado
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

                # Usando st.metric para destacar o resultado do EV
                st.metric(label="Valor Esperado (EV)", value=f"{ev_percentual:.2f}%")

                # Interpretação com cores e ícones
                if ev_calculado > 0.01: # Adicionando uma pequena margem para considerar "positivo"
                    st.success(f"**EV Positivo ({ev_percentual:.2f}%)**: ✅ Aposta com valor encontrado!")
                elif ev_calculado < -0.01: # Margem para "negativo"
                    st.error(f"**EV Negativo ({ev_percentual:.2f}%)**: ❌ Evite esta aposta.") # Usando st.error
                else:
                    st.info("**EV Próximo de Zero**: ⚖️ Aposta neutra, sem vantagem clara.") # Usando st.info
            else:
                st.error("Erro ao calcular o EV. Verifique as odds inseridas.")
        else:
            st.warning("Por favor, insira odds válidas (maiores que 1.00) em ambos os campos.")

# --- Legenda Final ---
st.caption("Desenvolvido com Streamlit | Estilo por Parceiro de Programação") # Adicionando um crédito ;)
