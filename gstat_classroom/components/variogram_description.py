"""
Component to print the current `Variogram.describe`

"""
import json
from dash.dependencies import Input, Output
import dash_html_components as html 
import dash_bootstrap_components as dbc

from gstat_classroom.app import app
from gstat_classroom.datasets import DATAMANAGER

LAYOUT = html.Div([
    html.H3([
        html.Code('describe()'),
        html.Span(' output')
    ], 
    className='my-3'),
    html.Pre(
        children=[
            html.Code(id='variogram-description')
        ],
        className='p-2',
        style=dict(
            backgroundColor='#E9ECEF',
            borderRadius='0 8px',
            boxShadow='1px 2px 4px silver'
        )
    )
])

@app.callback(
    Output('variogram-description', 'children'),
    Input('current-variogram-id', 'data')
)
def update_variogram_description(variogram_name):
    # load the variogram from the datastore
    tup = DATAMANAGER.get_variogram(variogram_name)

    # if no variogram estimated, print a message
    if tup is None:
        return '{\n\t"message": "No Variogram estimated"\n}'
    
    # extract and return
    V = tup['v']
    return json.dumps(V.describe(flat=True), indent=4)
