import dash
import os
from dash import Input, Output, dcc, html
import spei as si
import pandas as pd
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

# Função para extrair dados (sem alterações)
def extrair_dados(path_etp, path_prp, acumulado=1):
    df_etp = pd.read_excel(path_etp).rename(columns={'Hargreaves Potential Evapotranspiration (TerraClimate)': 'data', 'Unnamed: 1': 'dados'})
    df_etp = df_etp.iloc[1:].reset_index(drop=True)

    df_prp = pd.read_excel(path_prp).rename(columns={'Precipitation (TerraClimate)': 'data', 'Unnamed: 1': 'dados'})
    df_prp = df_prp.iloc[1:].reset_index(drop=True)

    df_merged = pd.merge(df_etp, df_prp, on='data', suffixes=('_etp', '_prp'))
    df_merged['balanco_hidrico'] = df_merged['dados_prp'] - df_merged['dados_etp']
    df_merged['data'] = pd.to_datetime(df_merged['data'], format='%Y-%m-%d')

    df = pd.DataFrame({'data': df_merged['data'], 'dados': pd.to_numeric(df_merged['balanco_hidrico'])})
    df.set_index('data', inplace=True)

    df_preparado = pd.DataFrame({'data': df['dados'].rolling(acumulado).sum().dropna().index,
                                  'dados': df['dados'].rolling(acumulado).sum().dropna().values})
    df_preparado.set_index('data', inplace=True)

    return df_preparado

# Função para extrair dados somente de ETP e precipitação (sem alterações)
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

# Extração dos dados e cálculo do SPEI (sem alterações)
dados_1 = extrair_dados(file_path_etp, file_path_prp, 1)
df_etp_prp = extrair_etp_prp(file_path_etp, file_path_prp)
spei_1 = si.spei(pd.Series(dados_1['dados']))

# Função para filtrar os anos (sem alterações)
def filtrar_por_ano(spei, ano_inicial, ano_final):
    return spei[(spei.index.year >= ano_inicial) & (spei.index.year <= ano_final)]

# Função para categorizar o SPEI com as novas categorias
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

# Enhanced color palette
COLOR_PALETTE = {
    'background': '#f4f4f4',
    'card_background': '#ffffff',
    'primary': '#1e3a8a',
    'secondary': '#0ea5e9',
    'text': '#333333',
    'grid': '#e0e0e0',
    'categories': {
        'Umidade extrema': '#1e3a8a',
        'Umidade severa': '#1d4ed8',
        'Umidade moderada': '#0ea5e9',
        'Umidade fraca': '#93c5fd',
        'Seca fraca': '#fca5a5',
        'Seca moderada': '#ef4444',
        'Seca severa': '#b91c1c',
        'Seca extrema': '#7f1d1d',
    }
}

# Enhanced control card with tooltips
def create_controls():
    return dbc.Card(
        [
            html.Div(
                [
                    dbc.Label("Intervalo de Anos", html_for='intervalo-dropdown'),
                    dcc.Dropdown(
                        id='intervalo-dropdown',
                        options=[
                            {'label': '5 anos', 'value': '5'},
                            {'label': '10 anos', 'value': '10'},
                            {'label': 'Todos os anos', 'value': 'all'}
                        ],
                        value='10',
                        clearable=False,
                    ),
                    dbc.Tooltip(
                        "Escolha o intervalo de anos para análise",
                        target='intervalo-dropdown',
                        placement='right'
                    ),
                    
                    dbc.Label("Ano", html_for='ano-dropdown'),
                    dcc.Dropdown(
                        id='ano-dropdown',
                        options=[],
                        value=None,
                        clearable=False,
                    ),
                    dbc.Tooltip(
                        "Selecione o período específico de anos",
                        target='ano-dropdown',
                        placement='right'
                    ),
                ]
            ),
        ],
        body=True,
        className='control-card',
        style={
            'backgroundColor': COLOR_PALETTE['card_background'],
            'boxShadow': '0 4px 6px rgba(0,0,0,0.1)',
            'borderRadius': '10px'
        }
    )

# Enhanced app layout
app = dash.Dash(__name__, 
                external_stylesheets=[
                    dbc.themes.BOOTSTRAP, 
                    'https://use.fontawesome.com/releases/v5.15.4/css/all.css',
                    '/assets/custom.css'
                ],
                title='Variabilidade do clima em Paragominas',
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])

app.layout = dbc.Container(
    [
        # Header with icon
        html.Div([
            html.H1([
                html.I(className="fas fa-chart-line me-2"),
                "Dashboard de SPEI"
            ], className="text-center my-4", style={'color': COLOR_PALETTE['primary']}),
        ]),
        
        # Main content
        dbc.Row(
            [
                dbc.Col(create_controls(), md=3, className="mb-3"),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                "Série Temporal de SPEI", 
                                className="card-title",
                                style={'backgroundColor': COLOR_PALETTE['primary'], 'color': 'white'}
                            ),
                            dcc.Graph(
                                id='spei-graph', 
                                config={'responsive': True}, 
                                style={'height': '450px'}
                            )
                        ],
                        className='h-100 dashboard-card'
                    ), 
                    md=9
                ),
            ],
            className="g-3 mb-3"
        ),
        
        # Secondary visualizations
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        "Categorias de SPEI", 
                        className="card-title",
                        style={'backgroundColor': COLOR_PALETTE['secondary'], 'color': 'white'}
                    ),
                    dcc.Graph(id='barras-empilhadas-graph', style={'height': '300px'})
                ], className='h-100 dashboard-card'), 
                md=4
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        "Média Mensal de SPEI", 
                        className="card-title",
                        style={'backgroundColor': COLOR_PALETTE['secondary'], 'color': 'white'}
                    ),
                    dcc.Graph(id='media-mensal-graph', style={'height': '300px'})
                ], className='h-100 dashboard-card'), 
                md=4
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        "Distribuição de SPEI", 
                        className="card-title",
                        style={'backgroundColor': COLOR_PALETTE['secondary'], 'color': 'white'}
                    ),
                    dcc.Graph(id='histograma-graph', style={'height': '300px'})
                ], className='h-100 dashboard-card'), 
                md=4
            )
        ], className="g-3 mb-3"),
        
        # Bottom row visualizations
        dbc.Row([
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        "Dispersão de SPEI", 
                        className="card-title",
                        style={'backgroundColor': COLOR_PALETTE['primary'], 'color': 'white'}
                    ),
                    dcc.Graph(id='scatter-graph', style={'height': '350px'})
                ], className='h-100 dashboard-card'), 
                md=6
            ),
            dbc.Col(
                dbc.Card([
                    dbc.CardHeader(
                        "Boxplot de SPEI por Ano", 
                        className="card-title",
                        style={'backgroundColor': COLOR_PALETTE['primary'], 'color': 'white'}
                    ),
                    dcc.Graph(id='boxplot-graph', style={'height': '350px'})
                ], className='h-100 dashboard-card'), 
                md=6
            )
        ], className="g-3")
    ],
    fluid=True,
    style={'backgroundColor': COLOR_PALETTE['background']}
)

@app.callback(
    [Output('ano-dropdown', 'options'),
     Output('ano-dropdown', 'value')],
    Input('intervalo-dropdown', 'value')
)
def atualizar_ano_dropdown(intervalo):
    anos_disponiveis = list(range(1981, 2023))  # Supondo que os dados vão até 2022
    opcoes = []
    
    if intervalo == '5':
        for ano in range(1981, 2023, 5):
            ano_final = ano + 4
            if ano_final <= anos_disponiveis[-1]:
                opcoes.append({'label': f'{ano} a {ano_final}', 'value': f'{ano}-{ano_final}'})
        if anos_disponiveis[-1] > 1981:
            opcoes.append({'label': f'{anos_disponiveis[-2]} a {anos_disponiveis[-1]}', 'value': f'{anos_disponiveis[-2]}-{anos_disponiveis[-1]}'})
            
    elif intervalo == '10':
        for ano in range(1981, 2023, 10):
            ano_final = ano + 9
            if ano_final <= anos_disponiveis[-1]:
                opcoes.append({'label': f'{ano} a {ano_final}', 'value': f'{ano}-{ano_final}'})
        if anos_disponiveis[-1] > 2020:
            opcoes.append({'label': f'{anos_disponiveis[-2]} a {anos_disponiveis[-1]}', 'value': f'{anos_disponiveis[-2]}-{anos_disponiveis[-1]}'})

    elif intervalo == 'all':
        opcoes = [{'label': '1981 a 2022', 'value': '1981-2022'}]

    # Define o value como a primeira opção se houver opções
    valor_default = opcoes[0]['value'] if opcoes else None

    return opcoes, valor_default

@app.callback(
    [Output('spei-graph', 'figure'),
     Output('barras-empilhadas-graph', 'figure'),
     Output('media-mensal-graph', 'figure'),
     Output('histograma-graph', 'figure'),
     Output('scatter-graph', 'figure'),
     Output('boxplot-graph', 'figure')],
    Input('ano-dropdown', 'value')
)
def atualizar_graficos(intervalo):
    if not intervalo:  # Se não houver intervalo selecionado
        raise dash.exceptions.PreventUpdate

    if intervalo == '1981-2022':
        ano_inicial, ano_final = 1981, 2022
    else:
        ano_inicial, ano_final = map(int, intervalo.split('-'))

    spei_filtrado = filtrar_por_ano(spei_1, ano_inicial, ano_final)
    categorias = spei_filtrado.apply(categorizar_spei)
    dados_ano = spei_filtrado.groupby(spei_filtrado.index.year).apply(lambda x: x.apply(categorizar_spei).value_counts(normalize=True) * 100).unstack(fill_value=0)

    # [The rest of the graph creation code remains the same as in the previous script]
    # ... (copy the graph creation code from the previous script)

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1', port=int(os.environ.get('PORT', 8050)))