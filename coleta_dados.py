import requests
import pandas as pd
import streamlit as st
from time import sleep

# Nova URL da API oficial da Caixa
BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/quina/{}"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def fetch_concurso(numero):
    try:
        url = BASE_URL.format(numero)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        dezenas = list(map(int, data["listaDezenas"]))
        return {
            "concurso": data["numero"],
            "data": data["dataApuracao"],
            "dezenas": dezenas
        }
    except Exception as e:
        st.warning(f"Erro no concurso {numero}: {e}")
        return None

@st.cache_data(show_spinner="🔄 Carregando concursos da Quina...")
def obter_concursos_ate(limit=2500):
    concursos = []
    # Tenta pegar o último concurso manualmente
    ultimo = 6740  # atualize conforme necessário ou use lógica automática

    for n in range(max(1, ultimo - limit + 1), ultimo + 1):
        resultado = fetch_concurso(n)
        if resultado:
            concursos.append(resultado)
            st.info(f"Concurso {n} carregado")
        sleep(0.15)  # Para evitar sobrecarga da API

    return pd.DataFrame(concursos)

# 🔁 Execução principal
st.title("🔍 Coleta de Concursos da Quina")
df_concursos = obter_concursos_ate(2500)

st.success(f"{len(df_concursos)} concursos carregados!")
st.dataframe(df_concursos)
