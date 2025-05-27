def calcular_estatisticas(df):
    df = df.copy()
    df['soma'] = df['dezenas'].apply(sum)

    # Pares e ímpares
    df['pares'] = df['dezenas'].apply(lambda d: sum(1 for x in d if x % 2 == 0))
    df['ímpares'] = df['dezenas'].apply(lambda d: sum(1 for x in d if x % 2 != 0))

    # Quadrantes
    def quadrantes(dezenas):
        q = [0, 0, 0, 0]
        for n in dezenas:
            if 1 <= n <= 20:
                q[0] += 1
            elif 21 <= n <= 40:
                q[1] += 1
            elif 41 <= n <= 60:
                q[2] += 1
            elif 61 <= n <= 80:
                q[3] += 1
        return q

    quadrantes_split = df['dezenas'].apply(quadrantes)
    df[['q1', 'q2', 'q3', 'q4']] = pd.DataFrame(quadrantes_split.tolist(), index=df.index)

    # Repetidas do concurso anterior
    repetidas = [0]
    for i in range(1, len(df)):
        atual = set(df.loc[i, 'dezenas'])
        anterior = set(df.loc[i - 1, 'dezenas'])
        repetidas.append(len(atual & anterior))
    df['repetidas'] = repetidas

    return df

# Aplicar as estatísticas
df_estatisticas = calcular_estatisticas(df_concursos)

# Exibir as 5 primeiras linhas
print(df_estatisticas[['concurso', 'soma', 'pares', 'ímpares', 'repetidas', 'q1', 'q2', 'q3', 'q4']].head())
