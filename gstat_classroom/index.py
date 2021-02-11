import dash_html_components as html 
import dash_bootstrap_components as dbc 
import dash_core_components as dcc
from dash.dependencies import Output, Input

from gstat_classroom.app import app
from gstat_classroom.chapters import chapter1, chapter2

# create the application-wide navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem('All chapters', header=True),
                dbc.DropdownMenuItem('Chapter 1 - Datasets', href='/chapter1'),
                dbc.DropdownMenuItem('Chapter 2 - Variography', href='/chapter2')
            ],
            nav=True,
            in_navbar=True,
            direction='left bottom',
            label='Chapters',
            className='mr-5'
        )
    ],
    brand='SciKit-GStat',
    color='dark',
    dark=True,
    fluid=True
)

# app layout
LAYOUT = dbc.Container(
    children=[
        # Store
        dcc.Store(id='data-store'),

        dcc.Location(id='url', refresh=False),
        navbar,
        dbc.Container(
            id='page-content',
            className='m-0 p-0',
            style=dict(
                boxSizing='border-box',
                overflowY='auto',
            ),
            fluid=True
        )
    ], 
    fluid=True, 
    className='m-0 p-0', 
    style=dict(boxSizing='border-box')
)

app.layout = LAYOUT

# validation layout
app.validation_layout = html.Div([
    LAYOUT,
    chapter1.LAYOUT,
    chapter2.LAYOUT
])

# CALLBACKS
# this callback swtiches the page
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/chapter1':
        return chapter1.LAYOUT
    elif pathname == '/chapter2':
        return chapter2.LAYOUT
    else:
        return '404'


if __name__=='__main__':
    app.run_server(debug=True)