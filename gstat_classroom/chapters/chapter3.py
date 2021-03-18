import json
import numpy as np
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_bootstrap_components as dbc 
import dash_core_components as dcc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from gstat_classroom.app import app
from gstat_classroom.datasets import DATAMANAGER
from gstat_classroom import components

from skgstat import OrdinaryKriging


# ----------------------------------------------
#                   LAYOUT
# ----------------------------------------------
# Headline Jumbotron
header = dbc.Jumbotron([
    dbc.Container([
        html.H1('Kriging', className='display-3'),
        html.P("In this chapter you can apply an OrdinaryKriging algorithm to the variogram estimated in the last session."),
        html.Hr(className='my-3'),
        html.P([
            html.Span('Variogram last modified: '),
            html.Code(id='last-variogram-change')
        ])
    ])
])

variogram_plots = dbc.Row(
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

kriging_settings = html.Div([
    html.H2('Settings'),
    html.P('The settings for kriging are only a few in SciKit-GStat'),

    dbc.Row([
        dbc.Col(
            children=[
                html.H5('Neighbors'),
                html.P('Use the range slider to set the minimum and maximum amount of neighbors used to build a kriging matrix'),
                html.P(
                    children=[
                        html.Div([
                            html.Code('min: '),
                            html.Span(id='min_points'),
                        ]),
                        html.Div([
                            html.Code('max: '),
                            html.Span(id='max_points')
                        ])
                    ],
                    style=dict(
                        display='flex',
                        flexDirection='row',
                        justifyContent='space-around'
                    )
                ),
                dcc.RangeSlider(
                    id='points',
                    min=2,
                    max=35,
                    step=1,
                    value=[5, 15],
                    allowCross=False,
                    pushable=1
                )
            ],
            width=12,
            lg=4
        ),
        dbc.Col(
            children=[
                html.H5('Calculation Method'),
                html.P('The kriging matrix distances can be calculated in every iteration, or only once and then approximated.'),
                dcc.RadioItems(
                    id='mode-select',
                    options=[
                        {'label': 'Exact calculation [slow]', 'value': 'exact'},
                        {'label': 'Dist. Estimation  [fast]', 'value': 'estimate'}
                    ],
                    value='exact'
                )
            ],
            width=12,
            lg=4
        ),
        dbc.Col(
            children=[
                html.H5('Result Grid'),
                html.P('Specify the size of the result grid. Due to calculation limitation, the grid size to limited to 100x100.'),
                html.P([
                    html.Span('current size: '),
                    html.Code(id='grid-size-label')
                ]),
                dcc.Slider(
                    id='grid-size',
                    min=25,
                    max=100,
                    step=1,
                    value=25,
                    marks={
                        25: {'label': '25x25', 'style': {'color': 'green'}},
                        50: {'label': '50x50', 'style': {'color': 'green'}},
                        75: {'label': '75x75', 'style': {'color': 'orange'}},
                        100: {'label': '100x100', 'style': {'color': 'red'}}
                    }
                )
            ],
            width=12,
            lg=4
        ),
        dbc.Col(
            children=[
                dbc.Container([
                    dbc.Button(
                        'START KRIGING',
                        id='start-button',
                        size='lg',
                        block=True,
                        color='primary',
                        className='mt-5'
                    )
                ])
            ],
            width=12
        )
    ])
])

output_graph = dbc.Row([
    dbc.Col(
        children=[
            html.H3('Kriging result'),
            dcc.Loading(
                id='kriging-plot-loading',
                children=dcc.Graph(id='kriging-plot'), 
                type='graph'
            )
        ],
        width=12
    ),
])

LAYOUT = html.Div([
    # page header
    header,

    # the currently fitted variogram
    html.H2('Variogram', className='mx-5'),
    variogram_plots,

    # Krigin settings
    dbc.Container(
        children=kriging_settings,
        fluid=True,
        style=dict(backgroundColor='#E9ECEF'),
        className='p-5'
    ),

    dbc.Container(
        children=output_graph,
        fluid=True,
        className='p-5'
    ),

    html.Code(id='dummy')
])


# ----------------------------------------------
#              Append Callbacks
# ----------------------------------------------
@app.callback(
    Output('last-variogram-change', 'children'),
    Input('current-variogram-id', 'data'),
)
def load_recent_variogram(variogram_hash):
    tup = DATAMANAGER.get_variogram(variogram_hash)

    if tup is None:
        return 'No Variogram estimated'
    else:
        return  '%s' % str(tup['dtime'])
    

@app.callback(
    Output('min_points', 'children'),
    Output('max_points', 'children'),
    Input('points', 'value')
)
def update_points_label(current_range):
    # extract min and max points
    min_points, max_points = current_range

    return str(min_points), str(max_points)


@app.callback(
    Output('grid-size-label', 'children'),
    Input('grid-size', 'value')
)
def update_grid_size_label(size):
    return f'{size}x{size}'


# MAIN Kriging application
@app.callback(
    Output('current-kriging-id', 'data'),
    Output('kriging-plot-loading', 'is_loading'),
    Input('start-button', 'n_clicks'),
    State('current-variogram-id', 'data'),
    State('grid-size', 'value'),
    State('points', 'value'),
    State('mode-select', 'value')
)
def kriging(n_clicks, variogram_name, grid_size, points_range, mode):
    # get the current Variogram
    tup = DATAMANAGER.get_variogram(variogram_name)
    if tup is None:
        raise PreventUpdate
    else:
        V = tup['v']

    # parse the points
    min_points, max_points = points_range

    dummy = dict(
        min_points=min_points,
        max_points=max_points,
        variogram=variogram_name,
        grid_size=grid_size,
        mode=mode
    )

    # build the grid
    min_x = np.min(V.coordinates[:,0])
    max_x = np.max(V.coordinates[:,0])
    min_y = np.min(V.coordinates[:,1])
    max_y = np.max(V.coordinates[:,1])
    xx,yy = np.mgrid[min_x:max_x:grid_size*1j, min_y:max_y:grid_size*1j]

    # instantiate the kriging algorithm
    ok = OrdinaryKriging(
        V,
        min_points=min_points,
        max_points=max_points,
        mode=mode,
        perf=True
    )

    # start interpolation
    field = ok.transform(xx.flatten(), yy.flatten()).reshape(xx.shape)
    sigma = ok.sigma.reshape(xx.shape)

    # add the field to the datastore
    field_hash = DATAMANAGER.add_kriging(field=field, sigma=sigma)

    return field_hash, True


@app.callback(
    Output('kriging-plot', 'figure'),
    Input('current-kriging-id', 'data')
)
def update_fields_figure(field_hash):
    if field_hash is None:
        raise PreventUpdate

    data = DATAMANAGER.get_kriging(field_hash)
    field = data['data']['field']
    sigma = data['data'].get('sigma')

    # create the figure
    if sigma is not None:
        fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'surface'}, {'type': 'surface'}]])
    else:
        fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'surface'}]])

    fig.add_trace(
        go.Surface(z=field, colorscale='Earth_r'),
        row=1, col=1
    )

    if sigma is not None:
        fig.add_trace(
            go.Surface(z=np.log(sigma), colorscale='thermal', showscale=False),
            row=1, col=2
        )

    # set the scene
    scene = dict(
        aspectratio=dict(x=1, y=1, z=0.1),
        camera=dict(eye=dict(x=.1, y=0., z=1.5))
    )

    # define the layout
    layout = dict(
        template='plotly_white',
        margin=dict(t=0, b=0, l=15, r=15)
    )

    if sigma is None:
        layout['scene'] = scene
    else:
        layout['scene1'] = scene
        layout['scene2'] = scene

    # update the figures
    fig.update_layout(**layout)

    return fig
