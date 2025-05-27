import requests
import time
import pandas as pd

# URLs
LATEST_URL = "https://loteriascaixa-api.herokuapp.com/api/quina/latest"
BASE_URL = "https://loteriascaixa-api.herokuapp.com/api/quina/{}"

# Obter último concurso
def get_latest_concurso():
    try:
        r = requests.get(LATEST_URL)
        if r.status_code == 200:
            return r.json()["concurso"]
    except Exception as e:
        print(f"Erro: {e}")
    return None

# Buscar um concurso específico
def fetch_concurso(numero):
    try:
        r = requests.get(BASE_URL.format(numero))
        if r.status_code == 200:
            return r.json()
    except:
        return None

# Carregar todos os concursos em uma lista
def carregar_todos_concursos():
    concursos = []
    ultimo = get_latest_concurso()
    for n in range(1, ultimo + 1):
        dados = fetch_concurso(n)
        if dados:
            concursos.append(dados)
            print(f"Concurso {n} capturado")
        else:
            print(f"Concurso {n} falhou")
        time.sleep(0.2)
    return concursos

# Converter concursos para DataFrame
def concursos_para_dataframe(concursos):
    registros = []
    for c in concursos:
        dezenas = list(map(int, c['dezenas']))
        registros.append({
            'concurso': c['concurso'],
            'data': c['data'],
            'dezenas': dezenas
        })
    return pd.DataFrame(registros)

# 🔁 EXECUÇÃO
concursos = carregar_todos_concursos()
df_concursos = concursos_para_dataframe(concursos)

print(df_concursos.head())
