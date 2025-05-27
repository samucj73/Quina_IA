import random
from collections import Counter

def estatisticas_agregadas(df):
    resumo = {}

    # Faixas numéricas
    for faixa in ['faixa_baixa', 'faixa_media', 'faixa_alta']:
        resumo[faixa + '_média'] = df[faixa].mean()
        resumo[faixa + '_mais_comum'] = df[faixa].mode()[0]

    # Média e amplitude
    resumo['média_geral'] = df['media'].mean()
    resumo['amplitude_média'] = df['amplitude'].mean()

    # Sequências consecutivas
    resumo['sequências_média'] = df['sequencias'].mean()
    resumo['sequências_max'] = df['sequencias'].max()

    # Linhas e colunas mais comuns
    linha_soma = df[[f'linha_{i}' for i in range(1, 9)]].sum()
    coluna_soma = df[[f'col_{i}' for i in range(10)]].sum()

    resumo['linha_mais_frequente'] = linha_soma.idxmax()
    resumo['coluna_mais_frequente'] = coluna_soma.idxmax()

    return resumo

def classificar_cartao(cartao, resumo):
    cartao = sorted(cartao)
    soma = sum(cartao)
    pares = sum(1 for x in cartao if x % 2 == 0)
    ímpares = len(cartao) - pares
    media = soma / len(cartao)
    amplitude = max(cartao) - min(cartao)
    sequencias = sum(1 for i in range(len(cartao)-1) if cartao[i+1] - cartao[i] == 1)

    # Faixas
    baixa = sum(1 for x in cartao if x <= 26)
    media_f = sum(1 for x in cartao if 27 <= x <= 53)
    alta = sum(1 for x in cartao if x >= 54)

    # Avaliação baseada em distância da média histórica
    score = 0
    score += 1 if abs(media - resumo['média_geral']) <= 5 else -1
    score += 1 if abs(amplitude - resumo['amplitude_média']) <= 10 else -1
    score += 1 if baixa == resumo['faixa_baixa_mais_comum'] else 0
    score += 1 if sequencias <= resumo['sequências_max'] else -1

    status = "bom" if score >= 2 else "ruim"
    return {"pontuação": score, "status": status}

def comparar_com_padroes(cartao, df_padroes):
    cartao_set = set(cartao)
    similares = df_padroes[df_padroes['dezenas'].apply(lambda x: len(cartao_set & set(x)) >= 4)]
    return similares[['concurso', 'dezenas', 'media', 'amplitude', 'sequencias']]

def gerar_cartao_inteligente(resumo, tentativas=1000):
    melhores = []

    for _ in range(tentativas):
        cartao = sorted(random.sample(range(1, 81), 5))
        classificacao = classificar_cartao(cartao, resumo)
        if classificacao['status'] == 'bom':
            melhores.append((cartao, classificacao['pontuação']))
    
    melhores.sort(key=lambda x: x[1], reverse=True)
    return melhores[:5]  # Top 5 melhores cartões

def conferir_aposta(cartao, dezenas_sorteadas):
    acertos = len(set(cartao) & set(dezenas_sorteadas))
    return {"acertos": acertos, "cartao": cartao, "sorteio": dezenas_sorteadas}

# Exemplos de uso (supondo que você já tenha os DataFrames df_padroes e df_concursos):

# resumo_padroes = estatisticas_agregadas(df_padroes)
# print("Resumo dos padrões ocultos:", resumo_padroes)

# classificacao = classificar_cartao([7, 21, 38, 52, 69], resumo_padroes)
# print("Classificação do cartão:", classificacao)

# comparados = comparar_com_padroes([7, 21, 38, 52, 69], df_padroes)
# print("Concursos com padrão semelhante ao cartão:", comparados.head())

# cartoes_gerados = gerar_cartao_inteligente(resumo_padroes)
# print("Cartões inteligentes gerados:", cartoes_gerados)

# ultimo_jogo = df_concursos.iloc[-1]
# resultado = conferir_aposta([7, 21, 38, 52, 69], ultimo_jogo['dezenas'])
# print("Conferência do cartão:", resultado)
