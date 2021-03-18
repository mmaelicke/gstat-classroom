"""
Component to print the current `Variogram.describe`

"""
import json
import numpy as np
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
    desc = V.describe(flat=True)

    # turn any numpy array to a list and round floats
    for key, value in desc.items():
        if isinstance(value, np.ndarray):
            desc[key] = [np.round(v, 2) for v in value]
        if isinstance(value, (float, np.float64)):
            if value > 1:
                desc[key] = np.round(value, decimals=2)
            elif value > 10:
                desc[key] = np.round(value, decimals=1)
            else:
                desc[key] = np.round(value, decimals=4)
    
    return json.dumps(desc, indent=4)
