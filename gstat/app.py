import numpy as np
import json

import dash
from dash.exceptions import PreventUpdate
import dash_core_components as dcc 
import dash_html_components as html 
import dash_bootstrap_components as dbc 
from dash.dependencies import Input, Output 

from skgstat import plotting
from skgstat import Variogram 

# set plotly as plotting backend
plotting.backend('plotly')

## DEV dummy data
np.random.seed(42)
coords = np.random.gamma(14, 6, size=(150, 2))
np.random.seed(42)
values = np.random.gamma(150, 2, size=(150))


# settings
MODELS = {
    'spherical': 'Spherical',
    'exponential': 'Exponential',
    'gaussian': 'Gaussian',
    'matern': 'Matérn',
    'cubic': 'Cubic Model',
    'stable': 'Stable model'
}
ESTIMATORS = {
    'matheron': 'Matheron',
    'cressie': 'Cressie-Hawkins',
    'dowd': 'Dowd',
    'genton': 'Genton',
    'entropy': 'Shannon Entropy',
    'minmax': 'MinMax (experimental)'
}

# build the dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# dataset selector
dataset_select = html.Div([
    html.H3('Select your dataset'),
    dcc.Dropdown(id='data-select', options=[{'label': 'Random Dummy data', 'value': 'rand'}])
])

# build the input mask
inputsForm = [
    html.H3('Settings'),
    html.P('Specify the variogram settings below and instantly see the effect on the results'),
    # MODEL and ESTIMATOR
    dbc.Row([
        dbc.Col([
            html.H5('Variogram Model'),
            dcc.Dropdown(
                id='select-model',
                options=[{'label': v, 'value': k} for k,v in MODELS.items()],
                value='spherical'
            ),
        ], width=6),
        dbc.Col([
            html.H5('Variogram Estimator'),
            dcc.Dropdown(
                id='select-estimator',
                options=[{'label': v, 'value': k} for k,v in ESTIMATORS.items()],
                value='matheron'
            )
        ], width=6)
    ]),

    # LAG AND BINNING SETTINGS
    html.H5('Lag binning'),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P([
                        html.Strong('Binning function'),
                        html.Br(),
                        html.Span('There are multiple options how the Variogram can automatically lag bin edges')
                    ]),
                    dcc.RadioItems(
                        id='bin-function',
                        options=[
                            {'label': 'Evenly spaced edges', 'value': 'even'},
                            {'label': 'Uniform bin sizes', 'value': 'uniform'}
                        ],
                        value='even'
                    ),
                ]),
                dbc.Col([
                    html.P([
                        html.Strong('Maximum lag distance'),
                        html.Br(),
                        html.Span('Use the one of the functions below, or click on the graph to set a maximum lag.')
                    ]),
                    dcc.RadioItems(
                        id='maxlag-method-select',
                        options=[
                            {'label': 'No MaxLag', 'value': 'none'},
                            {'label': 'median', 'value': 'median'},
                            {'label': 'mean', 'value': 'mean'},
                            {'label': 'Use the Graph', 'value': 'graph'},
                        ],
                        value='none'
                    ),
                    dcc.Store(id='maxlag')
                ])
            ]),
        ]),
        dbc.Col([
            html.P([
                'Number of lag bins:',
                html.Span(id='n-lags-output', children=['10'])
            ]),
            dcc.Slider(
                id='n-lags',
                min=3,
                max=100,
                step=1,
                value=10
            )

        ])
    ])

]

main_graph = dbc.Row([
    dbc.Col([
        dcc.Loading(
            id='main-graph-loader',
            children=[dcc.Graph(id='variogram-graph')],
            type='graph'
        )
    ], width=12, lg=9),
    dbc.Col([html.Pre([html.Code(id='variogram-description')])], width=12, lg=3)
])

outputs = [
    html.H3('More Results'),
    html.P('Inspect your results, they are instantly updated'),
    # Graph
    dbc.Row([
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='variogram-scattergram'), type='graph')],
            width=12, lg=4
        ),
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='distance-difference'), type='graph')],
            width=12, lg=4
        ),
        dbc.Col([], width=12, lg=4)
    ])
]

# MAIN APP LAYOUT
app.layout = html.Div([
    dcc.Store(id='data-store'),
    # HEADER
     html.H1('Variography', style={'text-align': 'center'}),

     # dataset selector
     dataset_select,
    
     # Main graph
     main_graph,
     
     # additional stuff
    html.Div(inputsForm), html.Div(outputs)
])

# CALLBACKS
@app.callback(
    Output('data-store', 'data'),
    Input('data-select', 'value')
)
def load_data(dataset_name):
    if dataset_name == 'rand':
        return {
            'coordinates': coords,
            'values': values
        }
    return None


@app.callback(
    Output('maxlag', 'data'),
    Input('maxlag-method-select', 'value'),
    Input('variogram-graph', 'clickData')
)
def update_maxlag_value(method_select, clickData):
    if method_select == 'graph' and clickData is not None:
        return clickData.get('points', [{}])[0].get('x')
    elif method_select in ['median', 'mean']:
        return method_select
    else:
        return None

@app.callback(
    Output('n-lags-output', 'children'),
    Input('n-lags', 'value')
)
def update_n_lags_output(n_lags):
    return str(n_lags)


@app.callback(
    Output('variogram-graph', 'figure'),
    Output('variogram-description', 'children'),
    Output('variogram-scattergram', 'figure'),
    Output('distance-difference', 'figure'),
    Input('data-store', 'data'),
    Input('select-model', 'value'),
    Input('select-estimator', 'value'),
    Input('bin-function', 'value'),
    Input('n-lags', 'value'),
    Input('maxlag', 'data')
)
def estimate_variogram(data, model_name, estimator_name, bin_func, n_lags, maxlag):
    # if there is no data selected, prevent update
    if data is None:
        raise PreventUpdate

    # get the data
    c = data.get('coordinates')
    v = data.get('values')
    
    # estimate the variogram
    V = Variogram(c, v, 
        model=model_name,
        estimator=estimator_name,
        bin_func=bin_func,
        n_lags=n_lags,
        maxlag=maxlag
    ) 

    # core plot
    fig = V.plot(show=False) 
    
    # scattergram
    scat = V.scattergram(show=False)

    # distance difference plot
    diff = V.distance_difference_plot(show=False)

    # description
    desc = json.dumps(V.describe(), indent=4)

    # update the layout
    fig.update_layout(
        template='plotly_white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    scat.update_layout(template='plotly_white')
    diff.update_layout(template='plotly_white')
    

    return fig, desc, scat, diff


if __name__=='__main__':
    app.run_server(debug=True)