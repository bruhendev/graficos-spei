import pandas as pd
import spei as si
import plotly.graph_objects as go

# Função de categorização de SPEI
def categorizar_spei(spei_value):
    if spei_value >= 2.00:
        return 'Umidade extrema'
    elif 1.50 <= spei_value < 2.00:
        return 'Umidade severa'
    elif 1.00 <= spei_value < 1.50:
        return 'Umidade moderada'
    elif 0 <= spei_value < 1.00:
        return 'Umidade fraca'
    elif -0.99 <= spei_value < 0:
        return 'Seca fraca'
    elif -1.50 <= spei_value < -1.00:
        return 'Seca moderada'
    elif -1.99 <= spei_value < -1.50:
        return 'Seca severa'
    else:
        return 'Seca extrema'

# Função para extrair os dados e calcular o balanço hídrico
def extrair_dados(path_etp, path_prp, acumulado=1):
    # Leitura dos arquivos ETP e PRP
    df_etp = pd.read_excel(path_etp).rename(columns={'Hargreaves Potential Evapotranspiration (TerraClimate)': 'data', 'Unnamed: 1': 'dados'})
    df_etp = df_etp.iloc[1:].reset_index(drop=True)
    
    df_prp = pd.read_excel(path_prp).rename(columns={'Precipitation (TerraClimate)': 'data', 'Unnamed: 1': 'dados'})
    df_prp = df_prp.iloc[1:].reset_index(drop=True)
    
    # Mesclando as duas tabelas pelo campo 'data'
    df_merged = pd.merge(df_etp, df_prp, on='data', suffixes=('_etp', '_prp'))
    df_merged['balanco_hidrico'] = df_merged['dados_prp'] - df_merged['dados_etp']
    df_merged['data'] = pd.to_datetime(df_merged['data'], format='%Y-%m-%d')
    
    # Calculando o balanço hídrico acumulado
    df = pd.DataFrame({'data': df_merged['data'], 'dados': pd.to_numeric(df_merged['balanco_hidrico'])})
    df.set_index('data', inplace=True)
    
    df_preparado = pd.DataFrame({'data': df['dados'].rolling(acumulado).sum().dropna().index,
                                  'dados': df['dados'].rolling(acumulado).sum().dropna().values})
    df_preparado.set_index('data', inplace=True)
    
    return df_preparado

# Caminhos dos arquivos de ETP e PRP
file_path_etp = 'dados/ETP_HARVREAVES_TERRACLIMATE.xlsx'
file_path_prp = 'dados/PRP_TERRACLIMATE.xlsx'

# Extração dos dados e cálculo do SPEI
dados_1 = extrair_dados(file_path_etp, file_path_prp, acumulado=1)
spei_1 = si.spei(pd.Series(dados_1['dados']))

# Categorizar os valores de SPEI e criar uma coluna com as categorias
categorias = [categorizar_spei(spei) for spei in spei_1]
df_spei = pd.DataFrame({'SPEI': spei_1, 'Categoria': categorias})

# Contar as ocorrências de cada categoria
contagem_categorias = df_spei['Categoria'].value_counts()

# Calcular a porcentagem de cada categoria
total = len(df_spei)
porcentagem_categorias = (contagem_categorias / total) * 100

# Criar uma tabela com as porcentagens
tabela_porcentagem = pd.DataFrame({'Categoria': contagem_categorias.index, 
                                   'Contagem': contagem_categorias.values, 
                                   'Porcentagem': porcentagem_categorias.values})

# Definindo as cores para cada categoria
cores = {
    'Umidade extrema': '#1e3a8a',
    'Umidade severa': '#1e40af',
    'Umidade moderada': '#2563eb',
    'Umidade fraca': '#60a5fa',
    'Seca fraca': '#f87171',
    'Seca moderada': '#dc2626',
    'Seca severa': '#991b1b',
    'Seca extrema': '#450a0a'
}

# Definir a ordem desejada das categorias de acordo com a ordem que você quer
ordem_desejada = ['Seca extrema', 'Seca severa', 'Seca moderada', 'Seca fraca', 
                  'Umidade fraca', 'Umidade moderada', 'Umidade severa', 'Umidade extrema']

# Reorganizar a tabela de porcentagens de acordo com a ordem desejada
tabela_porcentagem['Categoria'] = pd.Categorical(tabela_porcentagem['Categoria'], categories=ordem_desejada, ordered=True)
tabela_porcentagem = tabela_porcentagem.sort_values('Categoria')

# Aplicar as cores no gráfico com base nas categorias
tabela_porcentagem['Cor'] = tabela_porcentagem['Categoria'].map(cores)

# Criando o gráfico de barras horizontal com cores e formatação
fig = go.Figure(data=[go.Bar(
    y=tabela_porcentagem['Categoria'],  # Eixo Y com categorias
    x=tabela_porcentagem['Porcentagem'],  # Eixo X com as porcentagens
    text=tabela_porcentagem['Porcentagem'].round(2),
    textposition='auto',
    marker_color=tabela_porcentagem['Cor'],  # Cores aplicadas conforme as categorias
    orientation='h',  # Barra horizontal
    marker_line=dict(width=0.5, color='black')  # Linhas mais finas (0.5) e cor preta
)])

# Ajustando o layout para formatação profissional e gráfico mais compacto
fig.update_layout(
    # title='Distribuição das Categorias de SPEI',
    title_font=dict(size=16, family='Arial, sans-serif'),
    xaxis_title='Porcentagem (%)',
    xaxis_title_font=dict(size=12, family='Arial, sans-serif'),
    yaxis_title='Categoria',
    yaxis_title_font=dict(size=12, family='Arial, sans-serif'),
    template='plotly_white',
    font=dict(family="Arial, sans-serif", size=12, color="black", weight="bold"),
    yaxis_tickangle=0,
    margin=dict(l=50, r=50, t=20, b=50),  # Margens ajustadas para gráfico menor
    plot_bgcolor='white',  # Fundo branco para o gráfico
    paper_bgcolor='white',  # Fundo branco para o papel
    showlegend=False,  # Remover a legenda
    height=400,  # Altura reduzida para gráfico mais compacto
    width=700  # Largura reduzida para gráfico mais compacto
)

# Salvar como imagem (necessário instalar o kaleido)
fig.write_image("grafico_spei_horizontal_colorido_formatado_ordem_invertida.png")
fig.show()
