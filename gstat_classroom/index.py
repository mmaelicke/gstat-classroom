import dash_html_components as html 
import dash_bootstrap_components as dbc 
import dash_core_components as dcc
from dash.dependencies import Output, Input

from gstat_classroom.app import app
from gstat_classroom.chapters import home, chapter1, chapter2, chapter3

# create the application-wide navbar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavLink('Home', href='/'),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem('All chapters', header=True),
                dbc.DropdownMenuItem('Chapter 1 - Datasets', href='/chapter1'),
                dbc.DropdownMenuItem('Chapter 2 - Variography', href='/chapter2'),
                dbc.DropdownMenuItem('Chapter 3 - Kriging', href='/chapter3')
            ],
            nav=True,
            in_navbar=True,
            direction='bottom',
            right=True,
            label='Chapters',
            className='mr-5'
        )
    ],
    brand='SciKit-GStat',
    color='dark',
    dark=True,
    fluid=True,
    className='px-5'
)

# app layout
LAYOUT = dbc.Container(
    children=[
        # Stores
        dcc.Store(id='data-store', storage_type='session'),
        dcc.Store(id='current-variogram-id', storage_type='session'),
        dcc.Store(id='current-kriging-id', storage_type='session'),

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
    chapter2.LAYOUT,
    chapter3.LAYOUT
])

# CALLBACKS
# this callback swtiches the page
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname is None or pathname == '' or pathname == '/':
        return home.LAYOUT
    elif pathname == '/chapter1':
        return chapter1.LAYOUT
    elif pathname == '/chapter2':
        return chapter2.LAYOUT
    elif pathname == '/chapter3':
        return chapter3.LAYOUT
    else:
        return '404'


if __name__=='__main__':
    app.run_server(debug=True)