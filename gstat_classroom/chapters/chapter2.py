import json
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_html_components as html 
import dash_core_components as dcc 
import dash_bootstrap_components as dbc
from skgstat import plotting
from skgstat import Variogram

from gstat_classroom.app import app

from gstat_classroom import settings
from gstat_classroom.datasets import DATAMANAGER
from gstat_classroom import components

# Set plotly as plotting backend
plotting.backend('plotly')

# ----------------------------------------------
#                   LAYOUT
# ----------------------------------------------
# Headline Jumbotron
header = dbc.Jumbotron([
    dbc.Container([
        html.H1('Variography', className='display-3'),
        html.P("This Chapter is about the core class of scikit-gstat. More description bla bla ...", className="my-3"),
        html.Hr(className='my-3'),
        components.dataset_select
    ])
])

# INPUT FORM
inputsForm = [
    html.H3('Settings'),
    html.P('Specify the variogram settings below and instantly see the effect on the results'),
    # MODEL and ESTIMATOR
    dbc.Row([
        dbc.Col([
            html.H5('Variogram Model'),
            dcc.Dropdown(
                id='select-model',
                options=[{'label': v, 'value': k} for k,v in settings.MODELS.items()],
                value='spherical'
            ),
        ], width=6),
        dbc.Col([
            html.H5('Variogram Estimator'),
            dcc.Dropdown(
                id='select-estimator',
                options=[{'label': v, 'value': k} for k,v in settings.ESTIMATORS.items()],
                value='matheron'
            )
        ], width=6)
    ], className='my-3'),

    # LAG AND BINNING SETTINGS
    html.H5('Lag binning', className='my-1'),
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
    ], className='my-3')
]

# MAIN GRAPH
main_graph = dbc.Row(
    children=[
        dbc.Col(
            children=components.variogram_plot,
            width=12,
            lg=9
        ),
        dbc.Col(
            children=components.variogram_description,
            width=12,
            lg=3
        )
    ],
    className="m-0 p-3",
    style=dict(boxSizing='border-box')
)

# OUPUT ROW
output_row = [
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
        dbc.Col(
            [dcc.Loading(dcc.Graph(id='location-trend'), type='graph')],
            width=12, lg=4)
    ])
]

LAYOUT = html.Div([
    # HEADLINE
    header,

    # Main graph
    main_graph,

    # inputForm 
    dbc.Container(
        children=inputsForm, 
        fluid=True, 
        style=dict(backgroundColor='#E9ECEF'),
        className='p-5'
    ),

    # additional output row
    html.Div(
        children=output_row,
        className='p-5'
    )
])


# ----------------------------------------------
#              Append Callbacks
# ----------------------------------------------
@app.callback(
    Output('maxlag', 'data'),
    Input('maxlag-method-select', 'value'),
    Input('variogram-plot', 'clickData')
)
def update_maxlag_value(method_select, clickData):
    if method_select == 'graph' and clickData is not None:
        return clickData.get('points', [{}])[0].get('x')
    elif method_select in ['median', 'mean']:
        return method_select
    else:
        raise PreventUpdate 

@app.callback(
    Output('n-lags-output', 'children'),
    Input('n-lags', 'value')
)
def update_n_lags_output(n_lags):
    return str(n_lags)


@app.callback(
    Output('variogram-scattergram', 'figure'),
    Output('distance-difference', 'figure'),
    Output('location-trend', 'figure'),
    Output('current-variogram-id', 'data'),
    Output('variogram-plot-loading', 'is_loading'),
    Input('data-store', 'data'),
    Input('select-model', 'value'),
    Input('select-estimator', 'value'),
    Input('bin-function', 'value'),
    Input('n-lags', 'value'),
    Input('maxlag', 'data')
)
def estimate_variogram(data_name, model_name, estimator_name, bin_func, n_lags, maxlag):
    # if there is no data selected, prevent update
    if data_name is None: 
        raise PreventUpdate
    
    # get the dataset
    data = DATAMANAGER.get_data(data_name)

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

    # development test
    current_variogram = DATAMANAGER.add_variogram(V)
    
    # scattergram
    scat = V.scattergram(show=False)

    # distance difference plot
    diff = V.distance_difference_plot(show=False)

    # location trend plot
    trend = V.location_trend(show=False, add_trend_line=True)

    # update the layout
    scat.update_layout(template='plotly_white')
    diff.update_layout(template='plotly_white')
    trend.update_layout(template='plotly_white')
    

    return scat, diff, trend, current_variogram, True
