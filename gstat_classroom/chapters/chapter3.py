import json
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc 

from gstat_classroom.app import app

from gstat_classroom.chapters import chapter2

from skgstat import OrdinaryKriging


LAYOUT = html.Div([
    dbc.Button('START', id='test-runner'),
    html.Div(id='test-output')
])

@app.callback(
    Output('test-output', 'children'),
    Input('test-runner', 'click')
)
def test(click_data):
    V = chapter2.CURRENT.get('variogram')

    if V is None:
        return 'No Variogram found'
    else:
        return html.Pre(html.Code(json.dumps(V.describe(), indent=4)))
