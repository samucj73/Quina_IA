from collections import Counter

def calcular_frequencia_global(df):
    todas_dezenas = [dezena for lista in df['dezenas'] for dezena in lista]
    frequencia = Counter(todas_dezenas)
    freq_ordenada = dict(sorted(frequencia.items()))
    return freq_ordenada

frequencia_dezenas = calcular_frequencia_global(df_estatisticas)
print("Frequência das dezenas:", frequencia_dezenas)
