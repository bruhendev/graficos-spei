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

# Criando intervalos de décadas
bins = [1980, 1990, 2000, 2010, 2020]  # Definindo os limites das décadas
labels = ['1981-1990', '1991-2000', '2001-2010', '2011-2020']  # Nomes para as décadas
df_spei['Decada'] = pd.cut(df_spei.index.year, bins=bins, labels=labels, right=False)

# Agrupar por intervalo de década e contar as categorias
contagem_decada = df_spei.groupby('Decada')['Categoria'].value_counts().unstack(fill_value=0)

# Calcular a porcentagem de cada categoria por década
porcentagem_decada = (contagem_decada.T / contagem_decada.sum(axis=1)).T * 100

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
porcentagem_decada = porcentagem_decada[ordem_desejada]

# Criando o gráfico
fig = go.Figure()

# Adicionando as barras para cada categoria
for categoria in ordem_desejada:
    fig.add_trace(go.Bar(
        y=porcentagem_decada.index,  # Intervalos de décadas
        x=porcentagem_decada[categoria],  # Porcentagem
        name=categoria,  # Nome da categoria
        orientation='h',  # Barra horizontal
        marker_color=cores[categoria],  # Cor da categoria
        text=porcentagem_decada[categoria].round(2),  # Valor da porcentagem
        textposition='auto'  # Posição do texto
    ))

# Ajustando o layout para formatação profissional e gráfico maior
fig.update_layout(
    # title='Distribuição das Categorias de SPEI por Década',
    title_font=dict(size=18, family='Arial, sans-serif'),
    xaxis_title='Porcentagem (%)',
    xaxis_title_font=dict(size=14, family='Arial, sans-serif'),
    yaxis_title='Intervalo de Década',
    yaxis_title_font=dict(size=14, family='Arial, sans-serif'),
    template='plotly_white',
    font=dict(family="Arial, sans-serif", size=14, color="black", weight="bold"),
    yaxis_tickangle=0,
    margin=dict(l=100, r=20, t=80, b=60),  # Margens ajustadas para gráfico maior
    plot_bgcolor='white',  # Fundo branco para o gráfico
    paper_bgcolor='white',  # Fundo branco para o papel
    showlegend=True,  # Mostrar legenda
    height=800,  # Aumentando a altura do gráfico
    width=1200  # Aumentando a largura do gráfico
)

# Salvar como imagem (necessário instalar o kaleido)
fig.write_image("grafico_spei_por_intervalos_decada.png")
fig.show()
