
import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations
import random
import requests

# ==================== FUNÇÕES ====================

@st.cache_data(show_spinner=True)
def obter_todos_concursos():
    url = "https://loteriascaixa-api.herokuapp.com/api/quina/all"
    resposta = requests.get(url)
    resposta.raise_for_status()
    dados = resposta.json()
    concursos = []
    for c in dados:
        dezenas = list(map(int, c['dezenas'].split()))
        concursos.append({'concurso': int(c['concurso']), 'dezenas': dezenas})
    df = pd.DataFrame(concursos).sort_values('concurso').reset_index(drop=True)
    return df

def calcular_estatisticas(df):
    df = df.copy()
    df['soma'] = df['dezenas'].apply(sum)
    df['pares'] = df['dezenas'].apply(lambda d: sum(1 for x in d if x % 2 == 0))
    df['ímpares'] = df['dezenas'].apply(lambda d: 5 - sum(1 for x in d if x % 2 == 0))

    def quadrantes(dezenas):
        q = [0, 0, 0, 0]
        for n in dezenas:
            if 1 <= n <= 20: q[0] += 1
            elif 21 <= n <= 40: q[1] += 1
            elif 41 <= n <= 60: q[2] += 1
            elif 61 <= n <= 80: q[3] += 1
        return q

    quadrantes_split = df['dezenas'].apply(quadrantes)
    df[['q1', 'q2', 'q3', 'q4']] = pd.DataFrame(quadrantes_split.tolist(), index=df.index)

    repetidas = [0]
    for i in range(1, len(df)):
        atual = set(df.loc[i, 'dezenas'])
        anterior = set(df.loc[i - 1, 'dezenas'])
        repetidas.append(len(atual & anterior))
    df['repetidas'] = repetidas
    return df

def calcular_frequencia_global(df):
    todas_dezenas = [dezena for lista in df['dezenas'] for dezena in lista]
    frequencia = Counter(todas_dezenas)
    freq_ordenada = dict(sorted(frequencia.items()))
    return freq_ordenada

def combinacoes_mais_comuns(df, tamanho=2, top=10):
    todas = []
    for dezenas in df['dezenas']:
        todas.extend(combinations(sorted(dezenas), tamanho))
    contagem = Counter(todas)
    return contagem.most_common(top)

def analisar_saltos(df):
    saltos = []
    for dezenas in df['dezenas']:
        dezenas_ordenadas = sorted(dezenas)
        saltos.extend([b - a for a, b in zip(dezenas_ordenadas, dezenas_ordenadas[1:])])
    contagem_saltos = Counter(saltos)
    return dict(sorted(contagem_saltos.items()))

def analisar_padroes_ocultos(df):
    df = df.copy()

    def faixa_numerica(dezenas):
        baixa = sum(1 for d in dezenas if 1 <= d <= 26)
        media = sum(1 for d in dezenas if 27 <= d <= 53)
        alta = sum(1 for d in dezenas if 54 <= d <= 80)
        return baixa, media, alta

    faixas = df['dezenas'].apply(faixa_numerica)
    df[['faixa_baixa', 'faixa_media', 'faixa_alta']] = pd.DataFrame(faixas.tolist(), index=df.index)

    def colunas(dezenas):
        col = [0] * 10
        for d in dezenas:
            col[d % 10] += 1
        return col

    colunas_dist = df['dezenas'].apply(colunas)
    col_df = pd.DataFrame(colunas_dist.tolist(), index=df.index)
    col_df.columns = [f'col_{i}' for i in range(10)]
    df = pd.concat([df, col_df], axis=1)

    def linhas(dezenas):
        linha = [0] * 8
        for d in dezenas:
            index = (d - 1) // 10
            linha[index] += 1
        return linha

    linhas_dist = df['dezenas'].apply(linhas)
    lin_df = pd.DataFrame(linhas_dist.tolist(), index=df.index)
    lin_df.columns = [f'linha_{i+1}' for i in range(8)]
    df = pd.concat([df, lin_df], axis=1)

    df['distancias'] = df['dezenas'].apply(lambda x: [b - a for a, b in zip(sorted(x), sorted(x)[1:])])
    df['amplitude'] = df['dezenas'].apply(lambda x: max(x) - min(x))
    df['min'] = df['dezenas'].apply(min)
    df['max'] = df['dezenas'].apply(max)
    df['media'] = df['dezenas'].apply(lambda x: round(sum(x) / len(x), 2))

    def sequencias_consecutivas(dezenas):
        dezenas = sorted(dezenas)
        contagem = 0
        for i in range(len(dezenas) - 1):
            if dezenas[i+1] - dezenas[i] == 1:
                contagem += 1
        return contagem

    df['sequencias'] = df['dezenas'].apply(sequencias_consecutivas)
    return df

def estatisticas_agregadas(df):
    resumo = {}
    for faixa in ['faixa_baixa', 'faixa_media', 'faixa_alta']:
        resumo[faixa + '_média'] = df[faixa].mean()
        resumo[faixa + '_mais_comum'] = df[faixa].mode()[0]
    resumo['média_geral'] = df['media'].mean()
    resumo['amplitude_média'] = df['amplitude'].mean()
    resumo['sequências_média'] = df['sequencias'].mean()
    resumo['sequências_max'] = df['sequencias'].max()
    linha_soma = df[[f'linha_{i}' for i in range(1, 9)]].sum()
    coluna_soma = df[[f'col_{i}' for i in range(10)]].sum()
    resumo['linha_mais_frequente'] = linha_soma.idxmax()
    resumo['coluna_mais_frequente'] = coluna_soma.idxmax()
    return resumo

# ==================== INTERFACE STREAMLIT ====================

st.set_page_config(page_title="Quina Inteligente", layout="centered")
st.title("🔍 Análise Inteligente da Quina")

opcoes_concursos = [10, 50, 100, 200, 500, 1000, 1500, 2000, 2500]
quantidade_concursos = st.select_slider(
    "Escolha a quantidade de concursos a analisar:",
    options=opcoes_concursos,
    value=500,
    help="Quanto mais concursos, mais abrangente a análise (pode demorar um pouco)"
)

df_todos = obter_todos_concursos()
df_usado = df_todos.tail(quantidade_concursos).reset_index(drop=True)
df_estatisticas = calcular_estatisticas(df_usado)
df_padroes = analisar_padroes_ocultos(df_estatisticas)
resumo = estatisticas_agregadas(df_padroes)

st.subheader("📊 Estatísticas Agregadas")
st.write(resumo)

def rodape():
    st.markdown("""
        <hr style="margin-top: 50px;"/>
        <div style="text-align: center; font-size: 14px; color: gray;">
            Desenvolvido por <b>SAMUCJ TECHNOLOGY</b> · 
            App baseado em dados da <a href="https://loterias.caixa.gov.br" target="_blank">Caixa Econômica Federal</a><br>
            Rodando com <b>Streamlit</b> · Última atualização: Maio/2025
        </div>
    """, unsafe_allow_html=True)

rodape()
