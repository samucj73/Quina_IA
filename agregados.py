def estatisticas_agregadas(df):
    resumo = {}

    # Faixas numéricas
    for faixa in ['faixa_baixa', 'faixa_media', 'faixa_alta']:
        resumo[faixa + '_média'] = df[faixa].mean()
        resumo[faixa + '_mais_comum'] = df[faixa].mode()[0]

    # Média e amplitude
    resumo['média_geral'] = df['media'].mean()
    resumo['amplitude_média'] = df['amplitude'].mean()

    # Sequências consecutivas
    resumo['sequências_média'] = df['sequencias'].mean()
    resumo['sequências_max'] = df['sequencias'].max()

    # Linhas e colunas mais comuns
    linha_soma = df[[f'linha_{i}' for i in range(1, 9)]].sum()
    coluna_soma = df[[f'col_{i}' for i in range(10)]].sum()

    resumo['linha_mais_frequente'] = linha_soma.idxmax()
    resumo['coluna_mais_frequente'] = coluna_soma.idxmax()

    return resumo

resumo_padroes = estatisticas_agregadas(df_padroes)
print("Resumo dos padrões ocultos:", resumo_padroes)
