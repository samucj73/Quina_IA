from collections import Counter
from itertools import combinations

def calcular_frequencia_global(df):
    """Calcula a frequência absoluta de cada dezena."""
    todas_dezenas = [dezena for lista in df['dezenas'] for dezena in lista]
    frequencia = Counter(todas_dezenas)
    freq_ordenada = dict(sorted(frequencia.items()))
    return freq_ordenada

def combinacoes_mais_comuns(df, tamanho=2, top=10):
    """Encontra as combinações (pares ou trincas) mais comuns."""
    todas = []
    for dezenas in df['dezenas']:
        todas.extend(combinations(sorted(dezenas), tamanho))
    contagem = Counter(todas)
    return contagem.most_common(top)

def analisar_saltos(df):
    """Analisa os saltos (diferença entre dezenas consecutivas)."""
    saltos = []
    for dezenas in df['dezenas']:
        dezenas_ordenadas = sorted(dezenas)
        saltos.extend([b - a for a, b in zip(dezenas_ordenadas, dezenas_ordenadas[1:])])
    contagem_saltos = Counter(saltos)
    return dict(sorted(contagem_saltos.items()))

def analisar_cartao(cartao, frequencia_global, saltos_frequentes, pares_comuns, trincas_comuns):
    """Analisa um cartão individual baseado em estatísticas históricas."""
    cartao = sorted(cartao)
    soma = sum(cartao)
    pares = sum(1 for x in cartao if x % 2 == 0)
    ímpares = len(cartao) - pares

    # Frequência individual
    freq_dezenas = [frequencia_global.get(d, 0) for d in cartao]
    media_freq = sum(freq_dezenas) / len(cartao)

    # Quadrantes
    q = [0, 0, 0, 0]
    for n in cartao:
        if 1 <= n <= 20: q[0] += 1
        elif 21 <= n <= 40: q[1] += 1
        elif 41 <= n <= 60: q[2] += 1
        elif 61 <= n <= 80: q[3] += 1

    # Saltos
    saltos = [b - a for a, b in zip(cartao, cartao[1:])]

    # Pares e trincas reconhecidas
    pares_do_cartao = list(combinations(cartao, 2))
    trincas_do_cartao = list(combinations(cartao, 3))

    pares_encontrados = [p for p in pares_comuns if p[0] in pares_do_cartao]
    trincas_encontradas = [t for t in trincas_comuns if t[0] in trincas_do_cartao]

    return {
        'soma': soma,
        'pares': pares,
        'ímpares': ímpares,
        'frequência_média': round(media_freq, 2),
        'quadrantes': q,
        'saltos': saltos,
        'saltos_comuns': [s for s in saltos if s in saltos_frequentes],
        'pares_históricos': pares_encontrados,
        'trincas_históricas': trincas_encontradas
    }
