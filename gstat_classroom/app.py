import dash
import dash_bootstrap_components as dbc

# build the main dash app
# this instance will be served to all the child pages
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)
server = app.server
