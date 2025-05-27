
import streamlit as st
import pandas as pd
from collections import Counter
from itertools import combinations
import requests
from time import sleep
import random

# ==================== FUNÇÕES ====================

@st.cache_data(show_spinner=True)
def obter_todos_concursos(qtd):
    concursos = []
    ultimo_concurso = 6740
    inicio = max(1, ultimo_concurso - qtd + 1)
    progresso = st.progress(0)

    for i, n in enumerate(range(inicio, ultimo_concurso + 1), 1):
        try:
            url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/quina/{n}"
            resposta = requests.get(url, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()
            dezenas = list(map(int, dados['listaDezenas']))
            concursos.append({'concurso': dados['numero'], 'dezenas': dezenas, 'data': dados['dataApuracao']})
        except Exception as e:
            st.warning(f"Erro ao baixar concurso {n}: {e}")
        progresso.progress(i / qtd)
        sleep(0.15)
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

def calcular_frequencia_global(df):
    contagem = Counter()
    for dezenas in df['dezenas']:
        contagem.update(dezenas)
    return contagem

# ===================== INTERFACE =====================

st.set_page_config(page_title="Quina Inteligente", layout="centered")

st.title("🔍 Análise Inteligente da Quina")

st.header("📥 Coleta de Dados")

opcoes_concursos = [10, 50, 100, 200, 500, 1000, 1500, 2000, 2500]
quantidade_concursos = st.select_slider(
    "Escolha a quantidade de concursos a analisar:",
    options=opcoes_concursos,
    value=500
)

with st.spinner("🔄 Coletando concursos da Quina..."):
    df_todos = obter_todos_concursos(quantidade_concursos)

if df_todos.empty:
    st.error("Nenhum concurso foi carregado. Tente novamente mais tarde.")
    st.stop()

df_estatisticas = calcular_estatisticas(df_todos)
df_padroes = analisar_padroes_ocultos(df_estatisticas)

st.header("📈 Análise Estatística")

with st.expander("➕ Soma das dezenas"):
    st.line_chart(df_estatisticas['soma'])

with st.expander("♻️ Repetição de dezenas entre concursos"):
    st.bar_chart(df_estatisticas['repetidas'].value_counts().sort_index())

with st.expander("⚖️ Quantidade de Pares e Ímpares"):
    st.dataframe(df_estatisticas[['concurso', 'pares', 'ímpares']])

with st.expander("🧭 Distribuição por Quadrantes"):
    st.dataframe(df_estatisticas[['concurso', 'q1', 'q2', 'q3', 'q4']])

st.header("🔍 Padrões Ocultos")

with st.expander("🔢 Faixas Numéricas"):
    st.dataframe(df_padroes[['concurso', 'faixa_baixa', 'faixa_media', 'faixa_alta']])

with st.expander("🧮 Colunas mais sorteadas"):
    colunas_sum = df_padroes[[f'col_{i}' for i in range(10)]].sum().sort_values(ascending=False)
    st.dataframe(colunas_sum)

with st.expander("📏 Linhas mais frequentes"):
    linhas_sum = df_padroes[[f'linha_{i+1}' for i in range(8)]].sum().sort_values(ascending=False)
    st.dataframe(linhas_sum)

with st.expander("🎯 Sequências consecutivas"):
    st.bar_chart(df_padroes['sequencias'].value_counts().sort_index())

with st.expander("↔️ Estatísticas diversas"):
    st.dataframe(df_padroes[['concurso', 'min', 'max', 'media', 'amplitude']])

with st.expander("🧬 Saltos entre dezenas"):
    st.write(analisar_saltos(df_todos))

resumo = estatisticas_agregadas(df_padroes)

st.header("📊 Estatísticas Agregadas")
st.write(resumo)

st.header("🎲 Gerador Inteligente de Cartões")

qtd_cartoes = st.slider("Quantidade de cartões a gerar:", 1, 120, 50)

if st.button("🧠 Gerar Cartões Inteligentes"):
    st.subheader("🃏 Cartões Gerados:")

    freq = df_padroes['dezenas'].explode().value_counts()
    top_dezenas = freq.nlargest(40).index.tolist()

    cartoes = []
    for _ in range(qtd_cartoes):
        cartao = sorted(random.sample(top_dezenas, 5))
        cartoes.append(cartao)

    st.session_state['cartoes'] = cartoes  # Armazenar para conferência

    for i, cartao in enumerate(cartoes, 1):
        dezenas_formatadas = "   ".join(f"{d:02d}" for d in cartao)
        st.markdown(f"**Cartão {i}:** `{dezenas_formatadas}`")

# ===================== CONFERÊNCIA DE CARTÕES =====================

st.header("✅ Conferência de Cartões Gerados")

qtd_ultimos = st.slider("Quantos concursos recentes deseja conferir?", 1, 10, 3)

if st.button("📋 Conferir Cartões"):
    if 'cartoes' not in st.session_state or not st.session_state['cartoes']:
        st.warning("⚠️ Nenhum cartão gerado ainda. Gere os cartões primeiro.")
    else:
        cartoes = st.session_state['cartoes']
        concursos_para_conferir = df_todos.tail(qtd_ultimos).reset_index(drop=True)
        st.subheader(f"Verificando contra os últimos {qtd_ultimos} concursos:")

        for idx, linha in concursos_para_conferir.iterrows():
            dezenas_resultado = set(linha['dezenas'])
            st.markdown(f"### Concurso {linha['concurso']} ({linha['data']}) - Resultado: `{sorted(dezenas_resultado)}`")

            houve_premio = False
            for i, cartao in enumerate(cartoes, 1):
                acertos = len(set(cartao) & dezenas_resultado)
                
                if acertos >= 2:  # Exibe apenas prêmios: duque, terno, quadra, quina
                    houve_premio = True
                    if acertos == 5:
                        status = "🏆 **QUINA!**"
                    elif acertos == 4:
                        status = "🎯 **QUADRA**"
                    elif acertos == 3:
                        status = "✅ **TERNO**"
                    else:  # acertos == 2
                        status = "💰 **DUQUE**"
                    dezenas_formatadas = "   ".join(f"{d:02d}" for d in cartao)
                    st.markdown(f"- **Cartão {i}**: `{dezenas_formatadas}` → **{acertos} acertos** → {status}")

            if not houve_premio:
                st.markdown("_Nenhum cartão premiado neste concurso._")


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
