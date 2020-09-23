"""
    Run "Simple Investment Dashboard" in Flask.
"""
import dash
import dash_bootstrap_components as dbc
import dashboard 
from dashboard import *
#import importlib
import logging
from flask.logging import default_handler
import os
#%reload_ext autoreload
#%autoreload 2
#%matplotlib inline
cf.offline.go_offline() # with execute this command will cause QuantFig.iplot() run into error

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
application = app.server
app.layout = dashboard_layout()
app.title = 'Simple Value Investing Dashboard'
debug_mode = os.environ.get('FLASK_DEBUG') == '1'
if ( debug_mode ):
    app.logger.setLevel(level=logging.DEBUG)
register_callbacks(app)
if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run_server(
        debug=debug_mode,
        port=server_port,
        host='0.0.0.0',
        dev_tools_ui=False,
        dev_tools_silence_routes_logging=True) 
    # dev_tools_silence_routes_logging=False
