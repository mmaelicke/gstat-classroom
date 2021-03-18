"""
Component for the main Variogram plot

"""
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_html_components as html
import dash_core_components as dcc
from skgstat.plotting import backend

from gstat_classroom.app import app
from gstat_classroom.datasets import DATAMANAGER

# set scikit-gstat backend to plotly
backend('plotly')


# Component layout
LAYOUT = html.Div(
    children=[
        dcc.Loading(
            id='variogram-plot-loading',
            children=dcc.Graph(id='variogram-plot'),
            type='graph'
        )
    ]
)


# Component callbacks
@app.callback(
    Output('variogram-plot', 'figure'),
    Input('current-variogram-id', 'data')
)
def update_main_variogram_plot(variogram_name):
    # get the current variogram
    tup = DATAMANAGER.get_variogram(variogram_name)

    # if no Variogram estimated, return
    if tup is None:
        raise PreventUpdate
    
    # extract the variogram
    V = tup['v']

    # plot and update the layout
    fig = V.plot(show=False)
    fig.update_layout(
        autosize=True,
        template='plotly_white',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )

    return fig