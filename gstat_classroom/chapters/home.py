import dash_html_components as html 
import dash_bootstrap_components as dbc 

INTRO = [
    html.Span('This is a playground application making the functionality of '),
    html.A('SciKit-GStat', href='https://github.com/mmaelicke/scikit-gstat', target='_blank'),
    html.Span(' available. '),
    html.Span('Explore the all the pages, you will find documentation and further resources in most places.'),
    html.Br(className='my-1'),
    html.Span('This application is made available on resources of '),
    html.A('hydrocode GbR', href='https://hydrocode.de', target='_blank')
]

LAYOUT = html.Div([
    dbc.Jumbotron([
        dbc.Container([
            html.H1('SciKit-GStat Playground', className='display-3'),
            html.P(INTRO, className='my-3'),
            html.Hr(className='my-3'),
            dbc.Button('Estimate a Variogram', size='lg', color='secondary', outline=True, href='/chapter2')

        ])
    ])
])