import pandas as pd
import spei as si
import plotly.graph_objs as go

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

# Classificando os valores de SPEI em categorias
categorias = [categorizar_spei(spei) for spei in spei_1]

# Criando o DataFrame com as categorias e agrupando por ano
df_categorias = pd.DataFrame({
    'data': dados_1.index,
    'categoria': categorias
})

# Adicionando o ano para a contagem por ano
df_categorias['ano'] = df_categorias['data'].dt.year

# Contagem das ocorrências por categoria por ano
contagem_ocorrencias = df_categorias.groupby(['ano', 'categoria']).size().unstack(fill_value=0)

# Calculando a porcentagem por categoria em relação ao total de meses por ano
contagem_ocorrencias_percentage = contagem_ocorrencias.div(contagem_ocorrencias.sum(axis=1), axis=0) * 100

# Criando o gráfico
fig = go.Figure()

# Adicionando as barras para cada categoria de umidade (será a parte inferior)
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Umidade extrema'], 
                     name='Umidade Extrema (SPEI >= 2.00)', 
                     marker=dict(color='#1e3a8a')))
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Umidade severa'], 
                     name='Umidade Severa (1.50 <= SPEI < 2.00)', 
                     marker=dict(color='#1e40af')))
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Umidade moderada'], 
                     name='Umidade Moderada (1.00 <= SPEI < 1.50)', 
                     marker=dict(color='#2563eb')))
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Umidade fraca'], 
                     name='Umidade Fraca (0 <= SPEI < 1.00)', 
                     marker=dict(color='#60a5fa')))

# Adicionando as barras para cada categoria de seca (será a parte superior)
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Seca fraca'], 
                     name='Seca Fraca (-0.99 <= SPEI < 0)', 
                     marker=dict(color='#f87171')))
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Seca moderada'], 
                     name='Seca Moderada (-1.50 <= SPEI < -1.00)', 
                     marker=dict(color='#dc2626')))
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Seca severa'], 
                     name='Seca Severa (-1.99 <= SPEI < -1.50)', 
                     marker=dict(color='#991b1b')))
fig.add_trace(go.Bar(x=contagem_ocorrencias_percentage.index, 
                     y=contagem_ocorrencias_percentage['Seca extrema'], 
                     name='Seca Extrema (SPEI < -2.00)', 
                     marker=dict(color='#450a0a')))

# Configurações do layout
fig.update_layout(
    yaxis_title='Porcentagem de Ocorrências (%)',  # Rótulo do eixo Y
    barmode='stack',  # Tipo de gráfico: barras empilhadas
    font=dict(family="Arial, sans-serif", size=12, color="black", weight="bold"),  # Fonte
    width=1500,  # Largura do gráfico ajustada para ABNT
    height=800,  # Altura ajustada
    template='plotly_white',  # Estilo claro para o gráfico
    showlegend=True,  # Exibir legenda
    xaxis=dict(
        tickangle=45,  # Girar os rótulos para melhor legibilidade
        showgrid=True,  # Mostrar grid no eixo X
    ),
    yaxis=dict(
        showgrid=True,  # Mostrar grid no eixo Y
        gridcolor='lightgray',  # Cor mais clara para a grade
        gridwidth=0.5,  # Espessura da grade mais fina
    ),
    margin=dict(l=50, r=50, t=50, b=50)  # Margens reduzidas
)

# Exibindo o gráfico
fig.show()

# Salvando o gráfico como uma imagem
fig.write_image("grafico_barras_porcentagem_ano_seca_fraca_em_diante.png")
