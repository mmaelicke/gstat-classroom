import dash_html_components as html 
import dash_core_components as dcc 
from dash.dependencies import Input, Output

from gstat_classroom import datasets
from gstat_classroom.app import app

__options = [{'label': v, 'value': k} for k,v in datasets.DATASETS.items()]

LAYOUT = html.Div([
    html.H3('Select your dataset'),
    dcc.Dropdown(
        id='data-select',
        options=__options
    )
])

@app.callback(
    Output('data-store', 'data'),
    Input('data-select', 'value')
)
def load_data(dataset_name):
    return dataset_name
