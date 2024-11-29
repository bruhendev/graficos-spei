import pandas as pd
import spei as si
import plotly.graph_objs as go

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

# Calculando o SPEI mensalmente
spei_1 = si.spei(pd.Series(dados_1['dados']))

# Criando o DataFrame com o SPEI calculado
df_spei = pd.DataFrame({'data': dados_1.index, 'spei': spei_1})
df_spei.set_index('data', inplace=True)

# Adicionando o mês para agrupar
df_spei['mes'] = df_spei.index.month

# Filtrando os dados para o intervalo de 1981 a 1990
df_spei = df_spei[(df_spei.index.year >= 1981) & (df_spei.index.year <= 1990)]

# Calculando os valores do boxplot por mês
boxplot_data = []
for mes in range(1, 13):
    dados_mes = df_spei[df_spei['mes'] == mes]['spei']
    boxplot_data.append(dados_mes)

# Nomes dos meses em pt-BR
nomes_meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
               'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

# Criando o gráfico boxplot
fig = go.Figure()

# Adicionando os boxplots para cada mês
for mes in range(1, 13):
    fig.add_trace(go.Box(
        y=boxplot_data[mes - 1], 
        name=nomes_meses[mes - 1],  # Usando os nomes dos meses em pt-BR
        boxmean='sd',  # Exibir a média (linha horizontal) e desvio padrão
        marker=dict(color='gray'),  # Remover a cor de preenchimento
        line=dict(color='gray'),  # Definir a cor da linha das caixas como cinza
        fillcolor='rgba(0,0,0,0)'  # Deixar o preenchimento da caixa transparente
    ))

# Configurações do layout
fig.update_layout(
    yaxis_title='SPEI',  # Rótulo do eixo Y para SPEI
    yaxis=dict(
        range=[-3, 3],  # Ajustando o intervalo do eixo Y de -3 a 3
        showgrid=True,  # Mostrar grid no eixo Y
        gridcolor='lightgray',  # Cor mais clara para a grade
        gridwidth=0.5,  # Espessura da grade mais fina
    ),
    font=dict(family="Arial, sans-serif", size=12, color="black", weight="bold"),  # Fonte para título e rótulos
    # title=dict(text='Distribuição do Índice SPEI por Mês (Última Década)', font=dict(size=16)),
    width=1500,  # Largura do gráfico ajustada para ABNT
    height=800,  # Altura ajustada
    template='plotly_white',  # Estilo claro para o gráfico
    showlegend=False,  # Não mostrar legenda
    xaxis=dict(
        tickangle=45,  # Girar os rótulos para melhor legibilidade
        showgrid=True,  # Mostrar grid no eixo X
    ),
    margin=dict(l=50, r=50, t=20, b=20)  # Margens ajustadas
)

# Exibindo o gráfico
fig.show()

# Salvando o gráfico como uma imagem
fig.write_image("boxplot_spei_mes_ultima_decada_ajustado_ptbr_gray.png", width=2000, height=1200, scale=2)
