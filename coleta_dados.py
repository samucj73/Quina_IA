import requests
import pandas as pd
import streamlit as st
from time import sleep

BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/quina/{}"
LATEST_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/quina"

def obter_ultimo_concurso():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resposta = requests.get(LATEST_URL, headers=headers, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
        return dados["numero"]  # chave do número do último concurso na API oficial
    except requests.exceptions.RequestException as e:
        st.error("Erro ao buscar o último concurso na API oficial.")
        st.exception(e)
        return None

@st.cache_data(show_spinner="🔄 Carregando concursos da Quina...")
def obter_todos_concursos(limite=2500):
    concursos = []
    ultimo = obter_ultimo_concurso()
    if not ultimo:
        return pd.DataFrame()  # retorna DF vazio se erro

    max_concurso = min(ultimo, limite)

    headers = {"User-Agent": "Mozilla/5.0"}

    for n in range(1, max_concurso + 1):
        try:
            resposta = requests.get(BASE_URL.format(n), headers=headers, timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()
            dezenas = list(map(int, dados.get("listaDezenas", [])))
            concursos.append({
                'concurso': dados.get('numero', n),
                'data': dados.get('dataApuracao', ''),
                'dezenas': dezenas
            })
            sleep(0.15)  # para não sobrecarregar o servidor
        except requests.exceptions.RequestException as e:
            st.warning(f"Erro ao buscar concurso {n}: {e}")
            continue

    return pd.DataFrame(concursos)
