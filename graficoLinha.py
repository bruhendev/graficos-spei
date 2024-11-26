import pandas as pd
import spei as si
import plotly.graph_objs as go

# Função para extrair dados (com base no seu código)
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

# A série temporal de datas do DataFrame de entrada
datas = dados_1.index

# Criando o gráfico de linha
fig = go.Figure()

# Adicionando a linha para o SPEI com a cor #60a5fa
fig.add_trace(go.Scatter(x=datas, y=spei_1, mode='lines', name='SPEI', line=dict(color='#2563eb', width=2)))

# Configurações de layout
fig.update_layout(
    # title='Índice SPEI-1 ao Longo do Tempo',  # Título mais formal
    title_font=dict(family="Arial", size=18, color="black"),  # Título mais destacado
    yaxis_title='Índice SPEI-1',  # Rótulo do eixo Y
    template='plotly_white',  # Estilo claro para o gráfico
    font=dict(family="Arial, sans-serif", size=12, color="black", weight="bold"),  # Fonte
    width=1500,  # Largura ajustada para ABNT
    height=800,  # Altura ajustada
    showlegend=False,  # Não exibir legenda
    xaxis=dict(
        tickformat='%Y',  # Formato de data para mostrar apenas o ano
        tickvals=pd.to_datetime([f'{ano}-01-01' for ano in dados_1.index.year.unique()]),  # Mostrar cada ano
        ticktext=[str(ano) for ano in dados_1.index.year.unique()],  # Rótulos de cada ano
        tickangle=45,  # Girar os rótulos para melhor legibilidade
        showgrid=True,  # Mostrar grid no eixo X
        gridcolor='lightgray',  # Cor mais clara para a grade
        gridwidth=0.5,  # Espessura da grade mais fina
        zeroline=True,  # Linha no zero
        zerolinecolor='black',  # Cor da linha do zero
        zerolinewidth=1  # Espessura da linha do zero
    ),
    yaxis=dict(
        showgrid=True,  # Mostrar grid no eixo Y
        gridcolor='lightgray',  # Cor mais clara para a grade
        gridwidth=0.5,  # Espessura da grade mais fina
        zeroline=True,  # Linha no zero
        zerolinecolor='black',  # Cor da linha do zero
        zerolinewidth=1  # Espessura da linha do zero
    ),
    margin=dict(l=50, r=50, t=50, b=50)  # Margens ajustadas
)

# Exibindo o gráfico
fig.show()

# Salvando o gráfico como uma imagem
fig.write_image("spei_grafico_com_anos.png")
