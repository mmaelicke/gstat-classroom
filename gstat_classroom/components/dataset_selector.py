import dash_html_components as html 
import dash_core_components as dcc 
from dash.dependencies import Input, Output

from gstat_classroom.datasets import DATAMANAGER
from gstat_classroom.app import app

__options = [{'label': v, 'value': h} for h,v in DATAMANAGER.get_names().items()]

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
