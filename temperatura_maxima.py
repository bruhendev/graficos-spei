import pandas as pd
import plotly.graph_objs as go
import plotly.io as pio  # Para salvar a imagem
import os

# Função para extrair dados de precipitação (sem alterações)
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

# Definir os intervalos de tempo (1981-1990, 1991-2000, 2001-2010, 2011-2020)
intervalos = [(1981, 1990), (1991, 2000), (2001, 2010), (2011, 2020)]

# Calcular as estatísticas de temperatura (mínimo, médio, máximo) para cada intervalo
estatisticas_intervalos = []

for inicio, fim in intervalos:
    dados_intervalo = tmax[(tmax['Ano'] >= inicio) & (tmax['Ano'] <= fim)]
    
    # Calcular estatísticas (mínimo, médio, máximo) para cada intervalo de 10 anos
    estatisticas = {
        'Intervalo': f'{inicio}-{fim}',
        'Mínimo': dados_intervalo['TMAX'].min(),
        'Média': dados_intervalo['TMAX'].mean(),
        'Máximo': dados_intervalo['TMAX'].max()
    }
    
    estatisticas_intervalos.append(estatisticas)

# Converter para DataFrame
df_estatisticas = pd.DataFrame(estatisticas_intervalos)

# Criar o gráfico de linha
fig = go.Figure()

# Adicionar as estatísticas ao gráfico de linha
fig.add_trace(go.Scatter(
    x=df_estatisticas['Intervalo'],
    y=df_estatisticas['Mínimo'],
    mode='lines+markers',
    name='Mínimo',
    line=dict(color='rgb(255, 99, 71)', width=3),
    marker=dict(size=8, color='rgb(255, 99, 71)', line=dict(color='black', width=1))
))

fig.add_trace(go.Scatter(
    x=df_estatisticas['Intervalo'],
    y=df_estatisticas['Média'],
    mode='lines+markers',
    name='Média',
    line=dict(color='rgb(70, 130, 180)', width=3),
    marker=dict(size=8, color='rgb(70, 130, 180)', line=dict(color='black', width=1))
))

fig.add_trace(go.Scatter(
    x=df_estatisticas['Intervalo'],
    y=df_estatisticas['Máximo'],
    mode='lines+markers',
    name='Máximo',
    line=dict(color='rgb(34, 139, 34)', width=3),
    marker=dict(size=8, color='rgb(34, 139, 34)', line=dict(color='black', width=1))
))

# Ajustando o layout para formatação profissional
fig.update_layout(
    # title='Temperaturas Mínimas, Médias e Máximas por Intervalo de Tempo (1981-2020)',
    title_font=dict(size=18, family='Arial, sans-serif'),
    xaxis_title='Intervalos de Tempo',
    xaxis_title_font=dict(size=14, family='Arial, sans-serif'),
    yaxis_title='Temperatura Máxima (°C)',
    yaxis_title_font=dict(size=14, family='Arial, sans-serif'),
    template='plotly_white',
    font=dict(family="Arial, sans-serif", size=14, color="black", weight="bold"),
    yaxis_tickangle=0,
    margin=dict(l=50, r=50, t=20, b=20),  # Margens ajustadas para gráfico maior
    plot_bgcolor='white',  # Fundo branco para o gráfico
    paper_bgcolor='white',  # Fundo branco para o papel
    showlegend=True,  # Mostrar legenda
    height=400,  # Aumentando a altura do gráfico
    width=600,  # Aumentando a largura do gráfico
)

# Salvar a imagem no formato PNG
file_path = os.path.join(os.getcwd(), "grafico_temperaturas_linha.png")
fig.write_image(file_path)

print(f"Gráfico salvo como imagem em: {file_path}")
