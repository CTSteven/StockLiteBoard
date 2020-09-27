from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
import numpy as np
import pandas as pd
from rest_framework.decorators import api_view
import json
from datetime import datetime
from django.core.cache import cache
import logging
from . import consts 
from .services import getFinancialReport, getInvestmentSuggestion, getSP500StockList, \
    getStockPriceHistory , getFinancialWarningList , getYearlyStockPrice

logger = logging.getLogger(__name__)

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


def dashboardView(request):
    stock_list = getSP500StockList()
    #step_range = {i: '{:.2f}'.format(round(i, 2)) for i in np.arange(0, 1, 0.05)}
    discount_range = np.arange(0,10.1,0.5)
    discount_range = list(map(lambda x: str('{:.1f}'.format(x)), discount_range))
    margin_range = np.arange(0,0.51,0.05)
    margin_range = list(map(lambda x: str('{:.2f}'.format(x)), margin_range))
    context = {
        'stock_list':stock_list, 
        'discount_range':discount_range,
        'margin_range':margin_range
        }
    template = 'pages/dashboard.html'
    return render(request,template,context)

@api_view(['GET','POST'])
def stockPriceHistoryView(request):
    ticker = None
    dt_start = datetime.now()
    if request.method=='GET':
        ticker=request.query_params.get('ticker')
    elif request.method=='POST':
        data = request.body.decode('utf-8') 
        json_data = json.loads(data)
        ticker = json_data.get('ticker')

    if (ticker == None ):
        return HttpResponse({}, content_type="application/json")

    stock_price_history = getStockPriceHistory(ticker).reset_index()
    json_data = stock_price_history[['Date','Open','High','Low','Close','Volume']].to_json(orient="values",date_format="epoch",double_precision=5)
    logger.debug('stock price history total take %s' %( str( datetime.now() - dt_start) ) )
    return HttpResponse(json_data, content_type="application/json")


@api_view(['POST'])
def investmentSuggestionView(request):
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    ticker = json_data.get('ticker')
    discount = json_data.get('discount')
    margin = json_data.get('margin')
    err_msg = ""
    if (ticker == None ):
        err_msg = err_msg + 'Stock ticker is empty\n'
    if (discount == None ):
        err_msg = err_msg + 'Discount is empty\n'
    if (margin == None ):
        err_msg = err_msg + 'Margin is empty\n'

    logger.debug('ticker %s discount %s margin %s' % (ticker,discount,margin))

    if ( err_msg != ""):
        return HttpResponse({err_msg}, content_type="application/json")

    suggestion = getInvestmentSuggestion(ticker, discount=discount, margin= margin )
    json_data = suggestion.to_json(orient="records",date_format="epoch",double_precision=5)
    return HttpResponse(json_data, content_type="application/json")


@api_view(['POST'])
def financialReportView(request):
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    ticker = json_data.get('ticker')
    if (ticker == None ):
        return HttpResponse({}, content_type="application/json")

    financial_report = getFinancialReport(ticker).reset_index()
    financial_warning_list = getFinancialWarningList(ticker)
    yearly_stock_price = getYearlyStockPrice(ticker).rename(columns={'mean':'meanprice'})
    yearly_stock_price = pd.merge(yearly_stock_price, financial_report , how='inner', on=['year']).reset_index()
    yearly_stock_price = yearly_stock_price[['year','meanprice']]
    #print(yearly_stock_price)
    financial_report_summary = {
        'financial_report':financial_report.to_json(orient="records",date_format="epoch",double_precision=5),
        'financial_warning_list':financial_warning_list,
        'yearly_stock_price':yearly_stock_price.to_json(orient="records",double_precision=3),
        }

    json_data = json.dumps(financial_report_summary)
    return HttpResponse(json_data, content_type="application/json")



