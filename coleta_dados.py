import requests
import pandas as pd
import streamlit as st
from time import sleep

BASE_URL = "https://loteriascaixa-api.herokuapp.com/api/quina/{}"
LATEST_URL = "https://loteriascaixa-api.herokuapp.com/api/quina/latest"

def obter_ultimo_concurso():
    try:
        resposta = requests.get(LATEST_URL, timeout=10)
        resposta.raise_for_status()
        return resposta.json()["concurso"]
    except requests.exceptions.RequestException as e:
        st.error("Erro ao buscar o último concurso.")
        st.exception(e)
        return None

@st.cache_data(show_spinner="🔄 Carregando concursos da Quina...")
def obter_todos_concursos():
    concursos = []
    ultimo = obter_ultimo_concurso()
    if not ultimo:
        return []

    for n in range(1, ultimo + 1):
        try:
            resposta = requests.get(BASE_URL.format(n), timeout=10)
            resposta.raise_for_status()
            dados = resposta.json()
            concursos.append({
                'concurso': dados['concurso'],
                'data': dados['data'],
                'dezenas': list(map(int, dados['dezenas']))
            })
            sleep(0.15)  # prevenir bloqueio da API
        except requests.exceptions.RequestException as e:
            st.warning(f"Erro ao buscar concurso {n}: {e}")
            continue

    return pd.DataFrame(concursos)
