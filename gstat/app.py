import numpy as np
import json

import dash
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
    ])
]

outputs = [
    html.H3('Results'),
    html.P('Inspect your results, they are instantly updated'),
    # Graph
    dbc.Row([
        dbc.Col([dcc.Graph(id='variogram-graph')])
    ]),
    dbc.Row([
        dbc.Col([
            html.Pre([html.Code(id='variogram-description')])
        ]),
        dbc.Col([
            dcc.Graph(id='variogram-scattergram')
        ]),
        dbc.Col([])
    ])
]

# build the layout
app.layout = html.Div([
    # HEADER
    html.H1('Variography', style={'text-align': 'center'}),
    
    dbc.Row([
        dbc.Col(inputsForm, width=12, md=6, lg=4),
        dbc.Col(outputs, width=12, md=6, lg=8)
    ])
])


@app.callback(
    Output('variogram-graph', 'figure'),
    Output('variogram-scattergram', 'figure'),
    Output('variogram-description', 'children'),
    Input('select-model', 'value'),
    Input('select-estimator', 'value')
)
def estimate_variogram(model_name, estimator_name):
    # estimate the variogram
    V = Variogram(coords, values, model=model_name, estimator=estimator_name) 

    # core plot
    fig = V.plot(show=False)
    desc = json.dumps(V.describe(), indent=4)

    # scattergram
    scat = V.scattergram(show=False)

    # update the layout
    fig.update_layout(template='plotly_white')
    scat.update_layout(template='plotly_white')
    

    return fig, scat, desc


if __name__=='__main__':
    app.run_server(debug=True)