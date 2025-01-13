import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio
import os

# Função para extrair dados de temperatura máxima
def extrair_tmax(path_tmax):
    df_tmax = pd.read_excel(path_tmax, engine='openpyxl').rename(columns={'Maximum Temperature (TerraClimate)': 'data', 'Unnamed: 1': 'TMAX'})
    df_tmax = df_tmax.iloc[1:].reset_index(drop=True)
    df_tmax['data'] = pd.to_datetime(df_tmax['data'], format='%Y-%m-%d')
    df_tmax['Ano'] = df_tmax['data'].dt.year
    df_tmax['Mes'] = df_tmax['data'].dt.month
    return df_tmax

# Caminho do arquivo de dados
file_path_tmax = 'dados/TMAX_TERRACLIMATE.xlsx'

# Extrair os dados
tmax = extrair_tmax(file_path_tmax)

# Calcular as estatísticas de temperatura (mínimo, média, máximo) para cada mês ao longo dos anos
estatisticas_mensais = []

for mes in range(1, 13):  # Para cada mês de 1 a 12
    dados_mes = tmax[tmax['Mes'] == mes]
    
    # Calcular as estatísticas (mínimo, média, máximo) para cada mês
    minimo = dados_mes['TMAX'].min()
    media = dados_mes['TMAX'].mean()
    maximo = dados_mes['TMAX'].max()
    
    # Adicionar as estatísticas ao array
    estatisticas_mensais.append({
        'Mês': mes,
        'Mínimo': minimo,
        'Média': media,
        'Máximo': maximo
    })

# Converter para DataFrame
df_estatisticas_mensais = pd.DataFrame(estatisticas_mensais)

# Inicializar a figura do gráfico
fig = go.Figure()

# Adicionar as linhas de mínimo, média e máximo
fig.add_trace(go.Scatter(
    x=df_estatisticas_mensais['Mês'],
    y=df_estatisticas_mensais['Mínimo'],
    mode='lines+markers',
    name='Mínimo',
    line=dict(color='rgb(255, 99, 71)', width=3)
))

fig.add_trace(go.Scatter(
    x=df_estatisticas_mensais['Mês'],
    y=df_estatisticas_mensais['Média'],
    mode='lines+markers',
    name='Média',
    line=dict(color='rgb(70, 130, 180)', width=3)
))

fig.add_trace(go.Scatter(
    x=df_estatisticas_mensais['Mês'],
    y=df_estatisticas_mensais['Máximo'],
    mode='lines+markers',
    name='Máximo',
    line=dict(color='rgb(34, 139, 34)', width=3)
))

# Ajustando layout
fig.update_layout(
    # title='Temperaturas Mínimas, Médias e Máximas por Mês ao Longo da Série (1981-2020)',
    title_font=dict(size=18, family='Arial, sans-serif'),
    xaxis_title='Meses',
    xaxis_title_font=dict(size=14, family='Arial, sans-serif'),
    yaxis_title='Temperatura Máxima (°C)',
    yaxis_title_font=dict(size=14, family='Arial, sans-serif'),
    xaxis=dict(tickmode='array', tickvals=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], ticktext=['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']),
    template='plotly_white',
    font=dict(family="Arial, sans-serif", size=14, color="black", weight="bold"),
    margin=dict(l=50, r=50, t=20, b=20),  # Margens ajustadas para gráfico maior
    plot_bgcolor='white',  # Fundo branco para o gráfico
    paper_bgcolor='white',  # Fundo branco para o papel
    showlegend=True,  # Mostrar legenda
    height=400,  # Aumentando a altura do gráfico
    width=600,  # Aumentando a largura do gráfico
)

# Salvar o gráfico como imagem
file_path = os.path.join(os.getcwd(), "grafico_temperaturas_mensais.png")
fig.write_image(file_path)

# Exibir o gráfico
fig.show()
