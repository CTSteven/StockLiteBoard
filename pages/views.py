"""
    This module provides views for the InvestmentDashboard application.
"""
import sys
import traceback
import json
import logging
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
import numpy as np
import pandas as pd
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import get_financial_report, get_investment_suggestion, get_sp500_stock_list, \
    get_stock_price_history , get_financial_warning_list , get_yearly_stock_price

logger = logging.getLogger(__name__)

# Create your views here.

class HomePageView(TemplateView):
    """
    This class provides the view for the home page.
    """
    template_name = 'pages/home.html'

class AboutPageView(TemplateView):
    """
    This class provides the view for the about page.
    """
    template_name = 'pages/about.html'


def dashboard_view(request):
    """
    This function provides the view for the dashboard.
    """
    stock_list = get_sp500_stock_list()
    discount_range = [f'{x:.1f}' for x in np.arange(0, 10.1, 0.5)]
    margin_range = [f'{x:.2f}' for x in np.arange(0, 0.51, 0.05)]
    context = {
        'stock_list': stock_list,
        'discount_range': discount_range,
        'margin_range': margin_range
    }
    template = 'pages/dashboard.html'
    return render(request,template,context)

@api_view(['GET','POST'])
def stock_price_history_view(request):
    """
    This function provides the view for the stock price history.
    """
    # Add your code here

    ticker = None
    dt_start = datetime.now()
    if request.method=='GET':
        ticker=request.query_params.get('ticker')
    elif request.method=='POST':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        ticker = json_data.get('ticker')

    if ticker is None :
        return HttpResponse({}, content_type="application/json")

    try:
        stock_price_history = get_stock_price_history(ticker).reset_index()
        json_data = stock_price_history[['Date','Open','High','Low','Close','Volume']].to_json(
            orient="values",
            date_format="epoch",
            double_precision=5)
        logger.debug('stock price history total take %s',  str( datetime.now() - dt_start) )
        return HttpResponse(json_data, content_type="application/json")
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exc( )
        logger.error('Exception Type:\n %s \n Exception Value:\n %s \n TraceBack:\n %s',
                     exc_type,exc_value,exc_traceback)
        return Response(str(exc_value) ,status= status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def investment_suggestion_view(request):
    """
    This function provides the view for the investment suggestion.
    """
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    ticker = json_data.get('ticker')
    discount = json_data.get('discount')
    margin = json_data.get('margin')
    err_msg = ""
    if ticker is None :
        err_msg = err_msg + 'Stock ticker is empty\n'
    if discount is None :
        err_msg = err_msg + 'Discount is empty\n'
    if margin is None :
        err_msg = err_msg + 'Margin is empty\n'

    logger.debug(f'ticker {ticker} discount {discount} margin {margin}')

    if  err_msg != "":
        return HttpResponse({err_msg}, content_type="application/json")

    try:
        suggestion = get_investment_suggestion(ticker, discount=discount, margin= margin )
        json_data = suggestion.to_json(orient="records",date_format="epoch",double_precision=2)
        return HttpResponse(json_data, content_type="application/json")
    except Exception as e:
        logger.error(e)
        return Response(str(e),status= status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def financial_report_view(request):
    """
        This function provides the view for the financial report.
    """
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    ticker = json_data.get('ticker')
    if ticker is None :
        return HttpResponse({}, content_type="application/json")

    try:
        financial_report = get_financial_report(ticker).reset_index()
        financial_warning_list = get_financial_warning_list(ticker)
        yearly_stock_price = get_yearly_stock_price(ticker)
        yearly_stock_price = pd.merge(yearly_stock_price, financial_report , how='inner', on=['year']).reset_index()
        yearly_stock_price = yearly_stock_price[['year','low','mean','high','close']]
        #logger.debug(yearly_stock_price)
        #logger.debug(financial_report)
        financial_report_summary = {
            'financial_report':financial_report.to_json(orient="records",date_format="epoch",double_precision=2),
            'financial_warning_list':financial_warning_list,
            'yearly_stock_price':yearly_stock_price.to_json(orient="records",double_precision=3),
            }

        json_data = json.dumps(financial_report_summary)
        return HttpResponse(json_data, content_type="application/json")

    except Exception as e:
        logger.error(e)
        return Response(str(e),status= status.HTTP_400_BAD_REQUEST)
