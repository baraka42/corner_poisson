# -*- coding: utf-8 -*-
"""corner_poisson.ipynb


"""

import math
from tabulate import tabulate

# Função para calcular a distribuição de Poisson
def poisson(k, lambda_):
    return (math.exp(-lambda_) * (lambda_ ** k)) / math.factorial(k)

# Função para ajustar a taxa de escanteios no final do jogo
def ajustar_taxa_final_jogo(minuto, taxa_base, diferenca_gols):
    aumento = 0.0333 + 0.0037 * (minuto - 75)  # Ajuste inicia no minuto 75

    if diferenca_gols < 0:
        aumento += 0.05  # Time perdendo → mais pressão, mais escanteios
    elif diferenca_gols == 0:
        aumento += 0.03  # Jogo empatado → ambos podem pressionar
    else:
        aumento -= 0.02  # Time vencendo → tendência de segurar o jogo

    return taxa_base * (1 + aumento)

# Função para calcular odds por minuto
def calcular_odds_por_minuto(escanteios_1t, escanteios_2t_74, diferenca_gols):
    total_escanteios = escanteios_1t + escanteios_2t_74
    taxa_base = total_escanteios / 74  # Taxa base considerando os 75 minutos
    minutos_totais = 15 + 5  # Considerar os acréscimos como 5 minutos

    resultados = []
    for minuto in range(75, 75 + minutos_totais + 1):
        tempo_restante = (75 + minutos_totais) - minuto
        taxa_ajustada = ajustar_taxa_final_jogo(minuto, taxa_base, diferenca_gols)
        lambda_ = taxa_ajustada * tempo_restante

        # Probabilidades Poisson
        p0 = poisson(0, lambda_)
        p1 = poisson(1, lambda_)
        p2 = poisson(2, lambda_)

        # Probabilidades acumuladas para "Menos de X escanteios"
        p_menos_0_5 = p0
        p_menos_1_5 = p0 + p1
        p_menos_2_5 = p0 + p1 + p2

        # Função para calcular as odds
        def calcular_odd(prob):
            return round(1 / prob, 2) if prob > 0 else float('inf')

        resultados.append({
            'minuto': minuto,
            'projecao': round(lambda_, 1),
            'menos': {
                '-0.5': calcular_odd(p_menos_0_5),
                '-1.5': f"\033[1m{calcular_odd(p_menos_1_5)}\033[0m",
                '-2.5': calcular_odd(p_menos_2_5)
            },
            'mais': {
                '+0.5': calcular_odd(1 - p0),
                '+1.5': f"\033[1m{calcular_odd(1 - p0 - p1)}\033[0m",
                '+2.5': calcular_odd(1 - p0 - p1 - p2)
            }
        })
    return resultados


try:
    escanteios_1t = int(input("Escanteios no 1° tempo: "))
    escanteios_2t_74 = int(input("Escanteios no 2° tempo até o 74': "))
    diferenca_gols = int(input("Diferença de gols até o minuto 75 (time da casa - visitante): "))
except ValueError:
    print("Erro: Digite valores inteiros válidos.")
    exit()

# Cálculo das Odds
resultados = calcular_odds_por_minuto(escanteios_1t, escanteios_2t_74, diferenca_gols)

# Exibição dos Resultados em Tabela
tabela_principal = []

for res in resultados:
    if res['minuto'] <= 90:
        tabela_principal.append([
            res['minuto'], res['projecao'],
            res['menos']['-0.5'], res['menos']['-1.5'], res['menos']['-2.5'],
            res['mais']['+0.5'], res['mais']['+1.5'], res['mais']['+2.5']
        ])

# Impressão organizada com tabulate
print("\n==================================================")
print("                CORNER ODDS                 ")
print("==================================================")
print(tabulate(tabela_principal, headers=[
    'Minuto', 'Esc. Proj.',
    '-0.5', '\033[1m-1.5\033[0m', '-2.5',
    '+0.5', '\033[1m+1.5\033[0m', '+2.5'

], tablefmt="plain"))
