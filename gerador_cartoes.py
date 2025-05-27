import random
import pandas as pd

def gerar_cartoes_inteligentes(df_analisado, quantidade=5):
    cartoes = []

    # 1. Frequência das dezenas
    todas_dezenas = [dez for lista in df_analisado['dezenas'] for dez in lista]
    freq = pd.Series(todas_dezenas).value_counts().sort_values(ascending=False)
    dezenas_mais_frequentes = freq.head(30).index.tolist()

    # 2. Dezenas que aparecem em linhas e colunas mais frequentes
    colunas_total = df_analisado[[f'col_{i}' for i in range(10)]].sum()
    colunas_top = colunas_total.sort_values(ascending=False).head(5).index
    colunas_top_numeros = [i for i in range(1, 81) if f'col_{i % 10}' in colunas_top]

    linhas_total = df_analisado[[f'linha_{i+1}' for i in range(8)]].sum()
    linhas_top = linhas_total.sort_values(ascending=False).head(3).index
    linhas_top_numeros = [i for i in range(1, 81) if f'linha_{(i-1)//10 + 1}' in linhas_top]

    # 3. Dezenas por faixa (baixa, média, alta)
    faixa_baixa = [i for i in range(1, 27)]
    faixa_media = [i for i in range(27, 54)]
    faixa_alta = [i for i in range(54, 81)]

    for _ in range(quantidade):
        cartao = set()

        # Escolher 2 dezenas das mais frequentes
        cartao.update(random.sample(dezenas_mais_frequentes, 2))

        # Escolher 1 de coluna e 1 de linha mais frequentes
        cartao.add(random.choice(colunas_top_numeros))
        cartao.add(random.choice(linhas_top_numeros))

        # Garantir uma distribuição entre as faixas
        cartao.add(random.choice(faixa_baixa))
        cartao.add(random.choice(faixa_media))
        cartao.add(random.choice(faixa_alta))

        # Completar com dezenas aleatórias não repetidas até chegar a 5
        while len(cartao) < 5:
            candidato = random.randint(1, 80)
            cartao.add(candidato)

        cartoes.append(sorted(cartao))

    return cartoes
