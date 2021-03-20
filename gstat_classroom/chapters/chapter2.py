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
MY = 'my-3'
# Headline Jumbotron
header = dbc.Jumbotron([
    dbc.Container([
        html.H1('Variography', className='display-3'),
        html.P("This Chapter is about the core class of scikit-gstat. More description bla bla ...", className=MY),
        html.Hr(className=MY),
        components.dataset_select
    ])
])

# MODEL AND ESTIMATOR
#--------------------
model_estimator = dbc.Row([
    dbc.Col([
        html.H5('Variogram Model'),
        dcc.Dropdown(
            id='select-model',
            options=[{'label': v, 'value': k} for k,v in settings.MODELS.items()],
            value='spherical'
        ),
    ], xs=12, md=6),
    dbc.Col([
        html.H5('Variogram Estimator'),
        dcc.Dropdown(
            id='select-estimator',
            options=[{'label': v, 'value': k} for k,v in settings.ESTIMATORS.items()],
            value='matheron'
        )
    ], xs=12, md=6)
], className=MY)

# Binning 
# -------
binning = dbc.Row([
    dbc.Col([
        html.P('Binning function'),
        dcc.Dropdown(
            id='bin-function',
            options=[{'label': v, 'value': k} for k,v in settings.BINNING.items()],
            value='even'
        )

    ], xs=12, md=6),
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
    ], xs=12, md=6)
], className=MY)

# Fitting
#--------
fitting = dbc.Row([
    dbc.Col([
        html.P('Fitting function'),
        dcc.Dropdown(
            id='fit-function',
            options=[{'label': v, 'value': k} for k,v in settings.FITTING.items()],
            value='trf'
        )

    ], xs=12, md=6),
    dbc.Col([
        html.P('Fitting weights'),
        dcc.Dropdown(
            id='fit-sigma',
            options=[{'label': v, 'value': k} for k,v in settings.FITTING_WEIGHTS.items()],
            value='none'
        )
    ], xs=12, md=6)
], className=MY)

# Maxlag settings
#----------------
maxlag_setter = dbc.Row([
    dbc.Col([
        html.Strong('Distance function'),
        html.Br(),
        html.Span('You can switch the distance metric used. This is experimental.'),
        dcc.RadioItems(
            id='dist-function',
            options=[
                {'label': 'Euklidean', 'value': 'euklidean'},
                {'label': 'Manhattan', 'value': 'cityblock'},
                {'label': 'Cosine', 'value': 'cosine'},
                {'label': 'Minkowski (2-p norm)', 'value': 'minkowski'}
            ]
        )
    ], xs=12, md=4),
    dbc.Col([

    ], xs=12, md=4),
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
    ], xs=12, md=4)
], className=MY)

# INPUT FORM
#-----------
inputsForm = [
    html.H3('Settings'),
    html.P('Specify the variogram settings below and instantly see the effect on the results'),
    
    # MODEL and ESTIMATOR
    model_estimator,

    # LAG AND BINNING SETTINGS
    html.H5('Lag binning', className='mt-5'),
    binning,

    # Fitting
    html.H5('Model fitting', className='mt-5'),
    fitting,
    
    # maxlag
    html.Div([], className='mt-5'),
    maxlag_setter,
    dbc.Container([
        dbc.Button('Done? Apply Kriging here...', size='lg', block=True, color='secondary', outline=True, href='/chapter3')
    ], className='mt-3 p-5')
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
    Output('n-lags', 'disabled'),
    Input('bin-function', 'value')
)
def disable_slider(func_name):
    return func_name in ['sturges', 'scott', 'fd', 'sqrt', 'doane']

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
    Input('dist-function', 'value'),
    Input('n-lags', 'value'),
    Input('fit-function', 'value'),
    Input('fit-sigma', 'value'),
    Input('maxlag', 'data')
)
def estimate_variogram(data_name, model_name, estimator_name, bin_func, dist_func, n_lags, fit_func, fit_sigma, maxlag):
    # if there is no data selected, prevent update
    if data_name is None: 
        raise PreventUpdate
    
    # get the dataset
    data = DATAMANAGER.get_data(data_name)

    # get the data
    c = data.get('coordinates')
    v = data.get('values')

    # fit_sigma string 'none' has to be converted to Python None
    if fit_sigma == 'none':
        fit_sigma = None
    
    # estimate the variogram
    V = Variogram(c, v, 
        model=model_name,
        estimator=estimator_name,
        dist_func=dist_func,
        bin_func=bin_func,
        fit_method=fit_func,
        fit_sigma=fit_sigma,
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
