import pandas as pd
import plotly.express as px
from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.offline as plyo
from flask import Flask
from flask_caching import Cache
from dateutil.relativedelta import relativedelta
import stock_info_service
from stock_info_service import *
from investment_analysis import *
import sys
import logging

discountrate = 0.2
margin = 0.15

timeout = 10

stock_financial_df_dict = dict()
share_price_df_dict = dict()

#logger = None


def dashboard_layout():
    layout = html.Div([
        html.Div([
            html.H2('Simple Value Investing', className='text-center'),
            html.H6('(This POC application should not be used for real trading reference)',
                    className='text-center'),
            # First let users choose stocks
            html.H3('Choose a stock'),
            dcc.Dropdown(
                id='stock-dropdown',
                options=get_stocks_dash_options(),
                value='GOOG'
            ),
        ], className='shadow-sm p-3 bg-white', style={'opacity': '1'}),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Label('Discount Rate',
                                       className='font-weight-bold '),
                        ], className='col-2'),
                        html.Div([
                            dcc.Slider(
                                id='discountrate-slider',
                                min=0,
                                max=1,
                                value=0.15,
                                step=0.05,
                                marks={i: '{}'.format(round(i, 2))
                                       for i in np.arange(0, 1, 0.05)}
                            )], className='col-10 font-weight-bold'),
                    ], className='row col-12'),
                    html.Div([
                        html.Div([
                            html.Label('Margin Rate',
                                    className='font-weight-bold '),
                        ],className='col-2'),
                        html.Div([
                            dcc.Slider(
                                id='marginrate-slider',
                                min=0,
                                max=1,
                                value=0.15,
                                step=0.05,
                                marks={i: '{}'.format(round(i, 2))
                                       for i in np.arange(0, 1, 0.05)}
                            )],className='col-10 font-weight-bold'),
                    ], className='row col-12'),
                    html.Div([
                        html.H3('Investment Suggestion'),
                        html.Table(id='expected-future-price-table',
                                   className='table table-hover text-center')
                    ], className='col-12 p-2')
                ], className='col-12'),
                html.H3('5 years share price'),
                html.Div([
                    dcc.Graph(id='stock-graph'),
                ], className='col-12 bg-white',style={'paddingLeft':'0','paddingRight':'0'}),
                html.P('')
                # style={'width': '40%', 'display': 'inline-block'}
            ], className='row p-3'),
            html.Div([
                html.Div([
                    html.H3('Critical Variables and Ratios'),
                    html.Table(id='financial-report-table',
                               className='table table-hover text-center'),
                    html.P(''),
                    html.H3('Warning Flags'),
                    html.Table(id='reason-list',
                               className='table table-hover table-borderless'),
                    html.P('')
                ], className='col-12'),

            ], className='row')
        ],
            className='container-fluid',
            style={
            'backgroundColor': '#efefef',
            'paddingLeft': '1rem',
            'paddingRight': '1rem'
        }),
        html.Div(id='ticker-changed', style={'display': 'none'})
    ]
    )

    return layout


def register_callbacks(app):
    app.logger.info('call register')
    #cache = Cache(config={'CACHE_TYPE': 'simple'})
    # cache.init_app(app)
    #global logger
    #logger = main_logger
    #logger = logging.getLogger('werkzeug')
    # logger.setLevel(logging.DEBUG)
    # logging.debug("test")
    # @cache.memoize(timeout=TIMEOUT)

    def query_share_price_history(ticker):
        share_price_df = share_price_df_dict.get(ticker)
        # logger.debug('ticker:%s'.format(ticker))
        # logger.debug(share_price_df)
        if (share_price_df is None):
            last_2_year = dt.now() + relativedelta(years=-5)
            share_price_df = pdr.DataReader(
                ticker, data_source='yahoo',
                start=last_2_year, end=dt.now())
            share_price_df_dict[ticker] = share_price_df
        # return df.to_json(date_format='iso', orient='split')
        return share_price_df

    def get_share_price_history(ticker):
        # return pd.read_json(query_share_price_history(ticker),orient='split')
        return query_share_price_history(ticker)

    # @cache.memoize(timeout=TIMEOUT)
    def query_financial_report(ticker):
        stock_financial_df = stock_financial_df_dict.get(ticker)
        if (stock_financial_df is None):
            stock_financial_df = {}  # pd.DataFrame()
            financial_report = get_stock_financial_report(ticker).reset_index()
            financial_info_df = get_stock_financial_info_from_report(
                financial_report)
            financial_report[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']] = np.round(
                financial_info_df[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']], 2)
            stock_financial_df["financial_report"] = financial_report
            stock_financial_df["financial_info_df"] = financial_info_df
            stock_financial_df_dict[ticker] = stock_financial_df
        return stock_financial_df
        # return stock_financial_df.to_json(date_format='iso', orient='split')

    def get_financial_report(ticker):
        return query_financial_report(ticker)
        # return pd.read_json(query_financial_report(ticker),orient='split')

    # @cache.memoize(timeout=TIMEOUT)
    def query_eligibilitycheck(ticker):
        stock_financial_df = get_financial_report(ticker)
        financial_info_df = stock_financial_df["financial_info_df"]
        reasonlist = eligibilitycheck(ticker, financial_info_df)
        # return reasonlist.to_json(date_format='iso', orient='split')
        return reasonlist

    def get_eligibilitycheck(ticker):
        # return pd.read_json(query_eligibilitycheck(ticker),orient='split')
        return query_eligibilitycheck(ticker)

    @app.callback(
        Output('ticker-changed', 'children'),
        [Input('stock-dropdown', 'value')]
    )
    def get_stock_price(value):
        ticker = value.strip()
        query_share_price_history(ticker)
        return ticker

    # For the stocks graph
    @app.callback(
        Output('stock-graph', 'figure'),
        [Input('ticker-changed', 'children')]
    )
    def update_stock_graph(ticker):
        stockprice_df = get_share_price_history(ticker)
        fig = plot_stock_k_chart(ticker, stockprice_df, asFigure=True)
        return fig

    # for financial report table
    @app.callback(
        Output('financial-report-table', 'children'),
        [Input('ticker-changed', 'children')])
    def generate_table(ticker, max_rows=10):
        # global financial_info_df  # Needed to modify global copy of financial_info_df
        stock_financial_df = get_financial_report(ticker)
        financial_report = stock_financial_df["financial_report"]
        return [html.Thead([html.Tr([html.Th(col) for col in financial_report.columns])], className=' bg-info text-white')] + [html.Tbody([html.Tr([
            html.Td(financial_report.iloc[i][col]) for col in financial_report.columns
        ]) for i in range(min(len(financial_report), max_rows))], className='bg-white', style={'textAlign': 'right'})]

    # for the reason-list

    @app.callback(
        Output('reason-list', 'children'),
        [Input('ticker-changed', 'children')])
    def generate_reason_list(ticker):
        reasonlist = get_eligibilitycheck(ticker)
        return [html.Thead([html.Tr(html.Th('reasonlist'))], className='bg-warning')] + [html.Tbody([html.Tr(html.Td(reason)) for reason in reasonlist], className='bg-white')]

    # for the expected-future-price-table
    @app.callback(
        Output('expected-future-price-table', 'children'),
        [Input('ticker-changed', 'children'),
         Input('discountrate-slider', 'value'),
         Input('marginrate-slider', 'value')])
    def generate_future_price_table(ticker, discountrate, marginrate, max_rows=10):
        stockprice_df = get_share_price_history(ticker)
        stock_financial_df = get_financial_report(ticker)
        financial_info_df = stock_financial_df["financial_info_df"]
        # logger.warning(financial_info_df)
        # logger.warning(stockprice_df)
        app.logger.info('test...')
        pricedf = infer_reasonable_share_price(
            ticker, financial_info_df, stockprice_df, discountrate, marginrate,3) # future 3 years
        app.logger.debug(pricedf)
        return [html.Thead([html.Tr([html.Th(col) for col in pricedf.columns], className='rounded')], className='bg-info text-white')] + [html.Tbody([html.Tr([
            html.Td(html.B(pricedf.iloc[i][col]), className='bg-warning') if col == 'decision' else html.Td(
                round(pricedf.iloc[i][col], 2))
            for col in pricedf.columns
        ]) for i in range(min(len(pricedf), max_rows))], className='bg-white')]


def setLogger(p_logger):
    global logger
    logger = p_logger
