import dash_html_components as html 
import dash_core_components as dcc 
from dash.dependencies import Input, Output

from gstat_classroom import settings
from gstat_classroom import datasets
from gstat_classroom.app import app

__options = [{'label': k, 'value': v} for k,v in settings.DATASETS.items()]

# create the actual datasets
DATA = dict(
    rand=datasets.create_random_3d()
)

LAYOUT = html.Div([
    html.H3('Select you dataset'),
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
    return DATA.get(dataset_name, None)
