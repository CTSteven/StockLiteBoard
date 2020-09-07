import pandas as pd
import plotly.express as px
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import stock_info_service 
from stock_info_service import *
from investment_analysis import *

 
# Set up global variables
stockpricedf = pd.DataFrame()
financial_info_df = pd.DataFrame()
discountrate=0.2
margin = 0.15

def dashboard_layout():
    layout = html.Div([
        html.Div([

            html.H1('Value Investing'),
            # First let users choose stocks
            html.H2('Choose a stock'),
            dcc.Dropdown(
                id='my-dropdown',
                options=get_stocks_dash_options(),
                value='coke'
            ),
            html.H2('2 years stocks price graph'),
            dcc.Graph(id='my-graph'),
            html.P('')

        ],style={'width': '40%', 'display': 'inline-block'}),
        html.Div([
            html.H2('Critical Variables and Ratios'),
            html.Table(id='my-table',className='table table-hover'),
            html.P(''),
            html.H2('Warning Flags'),
            html.Table(id='reason-list',className='table table-hover'),
            html.P('')
        ], style={'width': '55%', 'float': 'right', 'display': 'inline-block'}),
        html.H4('Discount Calculation Rate'),
        dcc.Slider(
            id='discountrate-slider',
            min=0,
            max=1,
            value=0.15,
            step=0.05,
            marks={i: '{}'.format(round(i,2)) for i in np.arange(0, 1, 0.05)}
        ),
        html.H4('Margin Calculation Rate'),
        dcc.Slider(
            id='marginrate-slider',
            min=0,
            max=1,
            value=0.15,
            step=0.05,
            marks={i: '{}'.format(round(i,2)) for i in np.arange(0, 1, 0.05)}
        ),
        html.Table(id='expected-future-price-table',className='table table-hover')
    ],
    style={
            'backgroundColor':'#eee',
            'paddingLeft':'1rem',
            'paddingRight':'1rem'
        }
    )

    return layout


def register_callbacks(app):
    # For the stocks graph
    @app.callback(Output('my-graph', 'figure'), [Input('my-dropdown', 'value')])
    def update_graph(selected_dropdown_value):
        global stockpricedf # Needed to modify global copy of stockpricedf
        stockpricedf = pdr.DataReader(
            selected_dropdown_value.strip(), data_source='yahoo',
            start=dt(2013, 1, 1), end=dt.now())
        return {
            'data': [{
                'x': stockpricedf.index,
                'y': stockpricedf.Close
            }]
        }


    # for the table
    @app.callback(Output('my-table', 'children'), [Input('my-dropdown', 'value')])
    def generate_table(selected_dropdown_value,max_rows=10):
        global financial_info_df # Needed to modify global copy of financial_info_df
        financial_report = get_stock_financial_report(selected_dropdown_value.strip()).reset_index()
        financial_info_df = get_stock_financial_info_from_report(financial_report).reset_index()
        
        financial_report[['roe','interestcoverageratio','epsgrowth','roa']] = np.round(financial_info_df[['roe','interestcoverageratio','epsgrowth','roa']],2)
        #print(financial_info_df)
        # Header
        return [html.Thead( [html.Tr([html.Th(col) for col in financial_report.columns])], className='thead-dark'  )] + [html.Tbody( [html.Tr([
            html.Td(financial_report.iloc[i][col]) for col in financial_report.columns
        ]) for i in range(min(len(financial_report), max_rows))], style={'textAlign':'right'} )]

        
    # for the reason-list
    @app.callback(Output('reason-list', 'children'), [Input('my-dropdown', 'value')])
    def generate_reason_list(selected_dropdown_value):
        global financial_info_df # Needed to modify global copy of financial_info_df
        if ( not financial_info_df.empty ):
            reasonlist = eligibilitycheck(selected_dropdown_value.strip(),financial_info_df)
        
            # Header
            return [html.Thead( [html.Tr(html.Th('reasonlist'))] )]  + [html.Tbody( [html.Tr(html.Td(reason)) for reason in reasonlist] )]
        else:
            return None

    # for the expected-future-price-table
    @app.callback(Output('expected-future-price-table', 'children'), 
        [Input('my-dropdown', 'value'), Input('discountrate-slider', 'value'),Input('marginrate-slider', 'value')])
    def generate_future_price_table(selected_dropdown_value,discountrate,marginrate,max_rows=10):
        global financial_info_df # Needed to modify global copy of financial_info_df
        global stockpricedf
        if ( not financial_info_df.empty  and  not stockpricedf.empty ):
            pricedf = infer_reasonable_share_price(selected_dropdown_value.strip(),financial_info_df,stockpricedf,discountrate,marginrate)

            # Header
            return [html.Thead( [html.Tr([html.Th(col) for col in pricedf.columns])] )] + [ html.Tbody(  [html.Tr([
                html.Td(html.B(pricedf.iloc[i][col]))  if col == 'decision' else html.Td(round(pricedf.iloc[i][col],2))
                for col in pricedf.columns
            ]) for i in range(min(len(pricedf), max_rows))] )]
        else:
            return None