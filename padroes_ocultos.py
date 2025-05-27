def analisar_padroes_ocultos(df):
    df = df.copy()

    # Faixas: baixa (1-26), média (27-53), alta (54-80)
    def faixa_numerica(dezenas):
        baixa = sum(1 for d in dezenas if 1 <= d <= 26)
        media = sum(1 for d in dezenas if 27 <= d <= 53)
        alta = sum(1 for d in dezenas if 54 <= d <= 80)
        return baixa, media, alta

    faixas = df['dezenas'].apply(faixa_numerica)
    df[['faixa_baixa', 'faixa_media', 'faixa_alta']] = pd.DataFrame(faixas.tolist(), index=df.index)

    # Colunas: unidade (coluna do volante)
    def colunas(dezenas):
        col = [0] * 10
        for d in dezenas:
            col[d % 10] += 1
        return col

    colunas_dist = df['dezenas'].apply(colunas)
    col_df = pd.DataFrame(colunas_dist.tolist(), index=df.index)
    col_df.columns = [f'col_{i}' for i in range(10)]
    df = pd.concat([df, col_df], axis=1)

    # Linhas (1-10, 11-20, ..., 71-80)
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

    # Distâncias e amplitude
    df['distancias'] = df['dezenas'].apply(lambda x: [b - a for a, b in zip(sorted(x), sorted(x)[1:])])
    df['amplitude'] = df['dezenas'].apply(lambda x: max(x) - min(x))
    df['min'] = df['dezenas'].apply(min)
    df['max'] = df['dezenas'].apply(max)

    # Média aritmética
    df['media'] = df['dezenas'].apply(lambda x: round(sum(x) / len(x), 2))

    # Sequências consecutivas
    def sequencias_consecutivas(dezenas):
        dezenas = sorted(dezenas)
        contagem = 0
        for i in range(len(dezenas) - 1):
            if dezenas[i+1] - dezenas[i] == 1:
                contagem += 1
        return contagem

    df['sequencias'] = df['dezenas'].apply(sequencias_consecutivas)

    return df

# 🔁 Aplicar ao DataFrame existente
df_padroes = analisar_padroes_ocultos(df_estatisticas)

# Exemplo: visualizar as novas colunas com padrões
print(df_padroes[['concurso', 'faixa_baixa', 'faixa_media', 'faixa_alta', 
                  'amplitude', 'media', 'sequencias']].head())
