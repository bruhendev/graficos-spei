import dash 
from dash import Input, Output, dcc, html
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

# Função para extrair dados de precipitação (sem alterações)
def extrair_etp_prp(path_etp, path_prp):
    df_etp = pd.read_excel(path_etp).rename(columns={'Hargreaves Potential Evapotranspiration (TerraClimate)': 'data', 'Unnamed: 1': 'ETP'})
    df_prp = pd.read_excel(path_prp).rename(columns={'Precipitation (TerraClimate)': 'data', 'Unnamed: 1': 'Precipitação'})

    df_etp = df_etp.iloc[1:].reset_index(drop=True)
    df_prp = df_prp.iloc[1:].reset_index(drop=True)

    df_etp['data'] = pd.to_datetime(df_etp['data'], format='%Y-%m-%d')
    df_prp['data'] = pd.to_datetime(df_prp['data'], format='%Y-%m-%d')

    df_merged = pd.merge(df_etp, df_prp, on='data', how='inner')
    df_merged.set_index('data', inplace=True)

    return df_merged

# Caminhos dos arquivos (sem alterações)
file_path_etp = 'dados/ETP_HARVREAVES_TERRACLIMATE.xlsx'
file_path_prp = 'dados/PRP_TERRACLIMATE.xlsx'

# Extração dos dados de precipitação
df_etp_prp = extrair_etp_prp(file_path_etp, file_path_prp)

# Cálculo da média mensal de precipitação (1981-2022)
df_etp_prp['mes'] = df_etp_prp.index.month
df_etp_prp['ano'] = df_etp_prp.index.year

# Calculando a média de precipitação por mês (para o período total)
media_mensal = df_etp_prp.groupby('mes')['Precipitação'].mean()

# Preparar os dados para o gráfico
meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']

# Criar o gráfico de linha
grafico_precipitacao = go.Figure()

# Adicionando a linha para a média mensal
grafico_precipitacao.add_trace(go.Scatter(
    x=meses,
    y=media_mensal.values,
    mode='lines+markers',
    name='Média Mensal de Precipitação',
    line=dict(color='#1f77b4', width=2),  # Cor mais neutra e espessura ajustada
    marker=dict(size=6, color='#1f77b4', symbol='circle', opacity=0.7)  # Marcadores mais discretos
))

# Destaque para os meses mais chuvosos (Jan-Abr)
grafico_precipitacao.add_trace(go.Scatter(
    x=meses[:4],
    y=media_mensal.values[:4],
    mode='lines+markers',
    name='Meses mais Chuvosos (Jan-Abr)',
    line=dict(color='#e31a1c', dash='solid', width=2),  # Cor suave e linha sólida
    marker=dict(size=6, color='#e31a1c', symbol='circle', opacity=0.7)  # Marcadores discretos
))

# Destaque para os meses mais secos (Jun-Set) - Correção feita aqui
grafico_precipitacao.add_trace(go.Scatter(
    x=meses[5:9],  # Agora inclui Junho (5), Julho (6), Agosto (7) e Setembro (8)
    y=media_mensal.values[5:9],  # Valores de junho a setembro
    mode='lines+markers',
    name='Meses mais Secos (Jun-Set)',
    line=dict(color='#33a02c', dash='solid', width=2),  # Cor mais neutra para os meses secos
    marker=dict(size=6, color='#33a02c', symbol='circle', opacity=0.7)  # Marcadores discretos
))

# Layout do gráfico ajustado para dissertação com grades visíveis
grafico_precipitacao.update_layout(
    # title='Média Mensal de Precipitação em Paragominas (1981-2022)',  # Título mais formal
    title_x=0.5,  # Centralizando o título
    xaxis_title='Meses',  # Título do eixo X
    yaxis_title='Precipitação (mm)',  # Título do eixo Y
    xaxis=dict(
        tickmode='array',
        tickvals=meses,  # Colocando os nomes dos meses
        ticktext=meses,  # Colocando os nomes dos meses
        tickangle=45,  # Girando os rótulos do eixo X para melhorar a legibilidade
        showgrid=True,  # Exibindo a grade no eixo X
        gridcolor='rgba(128, 128, 128, 0.2)',  # Cor da grade do eixo X
        gridwidth=1  # Largura da linha da grade do eixo X
    ),
    yaxis=dict(
        showgrid=True,  # Exibindo a grade no eixo Y
        zeroline=True,  # Linha no valor 0
        showline=True,  # Linha no eixo Y
        linewidth=1,  # Largura da linha do eixo Y
        linecolor='black',  # Cor da linha do eixo Y
        gridcolor='rgba(128, 128, 128, 0.2)',  # Cor da grade do eixo Y
        gridwidth=1  # Largura da linha da grade do eixo Y
    ),
    font=dict(
        family="Arial, sans-serif",  # Fontes mais formais
        size=12,  # Tamanho de fonte moderado
        color="black"  # Cor da fonte
    ),
    plot_bgcolor='white',  # Fundo branco para contraste
    paper_bgcolor='white',  # Fundo branco para a área do gráfico
    showlegend=True,  # Mostrar a legenda
    legend=dict(
        x=0.8,  # Posicionamento da legenda
        y=0.95,  # Posicionamento da legenda
        traceorder='normal',
        font=dict(size=12),  # Tamanho da fonte da legenda
        bgcolor='rgba(255, 255, 255, 0.7)',  # Cor de fundo da legenda
        bordercolor='black',  # Cor da borda da legenda
        borderwidth=1  # Largura da borda da legenda
    ),
    margin=dict(
        t=20,  # Margem superior
        b=20,  # Margem inferior
        l=50,  # Margem esquerda
        r=50   # Margem direita
    )
)

# Exibindo o gráfico com o Dash
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    html.H1("Gráfico 1: Precipitação Mensal em Paragominas (1981-2022)", style={'text-align': 'center'}),  # Centralizando título
    dcc.Graph(
        id='grafico-precipitacao',
        figure=grafico_precipitacao
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
