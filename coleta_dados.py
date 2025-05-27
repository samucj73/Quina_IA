import requests
import pandas as pd
import streamlit as st
from time import sleep

BASE_URL = "https://servicebus2.caixa.gov.br/portaldeloterias/api/quina/{}"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def fetch_concurso(numero, max_retries=5, delay=0.3):
    for tentativa in range(max_retries):
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
        except requests.exceptions.HTTPError as e:
            st.warning(f"HTTPError no concurso {numero}, tentativa {tentativa+1}/{max_retries}: {e}")
            sleep(delay)
        except Exception as e:
            st.warning(f"Erro inesperado no concurso {numero}, tentativa {tentativa+1}/{max_retries}: {e}")
            sleep(delay)
    st.error(f"Falha ao obter dados do concurso {numero} após {max_retries} tentativas.")
    return None

@st.cache_data(show_spinner="🔄 Carregando concursos da Quina...")
def obter_concursos_ate(limit=2500):
    concursos = []
    # Para pegar o último concurso da API Caixa (tentativa rápida)
    try:
        ultimo_resp = requests.get(BASE_URL.format("latest"), headers=HEADERS, timeout=10)
        ultimo_resp.raise_for_status()
        ultimo = ultimo_resp.json()["numero"]
    except Exception:
        # fallback manual
        ultimo = 6740

    inicio = max(1, ultimo - limit + 1)
    st.info(f"Buscando concursos do {inicio} até o {ultimo}...")

    for n in range(inicio, ultimo + 1):
        resultado = fetch_concurso(n)
        if resultado:
            concursos.append(resultado)
        sleep(0.15)  # evita sobrecarga

    return pd.DataFrame(concursos)

# ======================== STREAMLIT ===========================

st.title("🔍 Coleta de Concursos da Quina")

quantidade_concursos = st.slider(
    "Escolha a quantidade de concursos a carregar",
    min_value=10, max_value=2500, value=500, step=10
)

df_concursos = obter_concursos_ate(quantidade_concursos)

st.success(f"{len(df_concursos)} concursos carregados com sucesso!")
st.dataframe(df_concursos)
