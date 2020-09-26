from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
import numpy as np
from rest_framework.decorators import api_view
import json
from datetime import datetime
from django.core.cache import cache
import logging
from . import consts 
from .services import getFinancialReport, getInvestmentSuggestion, getSP500StockList, getStockPriceHistory

logger = logging.getLogger(__name__)

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


def dashboardView(request):
    stock_list = getSP500StockList()
    step_range = {i: '{:.2f}'.format(round(i, 2)) for i in np.arange(0, 1, 0.05)}
    context = {'stock_list':stock_list, 'step_range':step_range}
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
    if (ticker == None ):
        return HttpResponse({}, content_type="application/json")

    suggestion = getInvestmentSuggestion(ticker)
    json_data = suggestion.to_json(orient="records",date_format="epoch",double_precision=5)
    return HttpResponse(json_data, content_type="application/json")


@api_view(['POST'])
def financialReportView(request):
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    ticker = json_data.get('ticker')
    if (ticker == None ):
        return HttpResponse({}, content_type="application/json")

    # get financial report & stock price 
    financial_report = getFinancialReport(ticker)

    json_data = financial_report.to_json(orient="records",date_format="epoch",double_precision=5)
    return HttpResponse(json_data, content_type="application/json")



