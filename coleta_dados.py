import requests
import time
import pandas as pd
from tqdm import tqdm

# URLs
LATEST_URL = "https://loteriascaixa-api.herokuapp.com/api/quina/latest"
BASE_URL = "https://loteriascaixa-api.herokuapp.com/api/quina/{}"

# Obter número do último concurso
def get_latest_concurso():
    try:
        r = requests.get(LATEST_URL, timeout=5)
        r.raise_for_status()
        return r.json()["concurso"]
    except Exception as e:
        print(f"[Erro ao buscar último concurso] {e}")
        return None

# Buscar concurso individual
def fetch_concurso(numero):
    try:
        r = requests.get(BASE_URL.format(numero), timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[Falha no concurso {numero}] {e}")
        return None

# Coleta todos os concursos até o último disponível
def carregar_todos_concursos():
    concursos = []
    ultimo = get_latest_concurso()
    if not ultimo:
        print("Não foi possível obter o último concurso.")
        return []

    for n in tqdm(range(1, ultimo + 1), desc="Baixando concursos"):
        dados = fetch_concurso(n)
        if dados:
            concursos.append(dados)
        time.sleep(0.2)  # Prevenir bloqueio por excesso de requisições

    return concursos

# Converte lista de concursos em DataFrame com colunas úteis
def concursos_para_dataframe(concursos):
    registros = []
    for c in concursos:
        try:
            dezenas = sorted(int(d) for d in c['dezenas'])
            registros.append({
                'concurso': c['concurso'],
                'data': c['data'],
                'dezenas': dezenas,
                'acumulou': c.get('acumulou', False),
                'premiacoes': c.get('premiacoes', [])
            })
        except Exception as e:
            print(f"[Erro ao processar concurso {c.get('concurso')}] {e}")
            continue

    return pd.DataFrame(registros)

# ⏯️ Execução
if __name__ == "__main__":
    concursos = carregar_todos_concursos()
    df_concursos = concursos_para_dataframe(concursos)

    print(df_concursos.head())
