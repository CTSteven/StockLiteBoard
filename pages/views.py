from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView, ListView
from stock_info_service import save_sp500_stocks_info, get_stock_price
import numpy as np
from rest_framework.decorators import api_view
import json
from datetime import datetime , date
import time
from dateutil.relativedelta import relativedelta
import decimal

# Create your views here.

class HomePageView(TemplateView):
    template_name = 'pages/home.html'

class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


def dashboardView(request):
    stock_list = save_sp500_stocks_info().sort_values(by=['tickers'])
    step_range = {i: '{:.2f}'.format(round(i, 2)) for i in np.arange(0, 1, 0.05)}
    context = {'stock_list':stock_list, 'step_range':step_range}
    template = 'pages/dashboard.html'
    return render(request,template,context)

@api_view(['GET','POST'])
def stockPriceHistoryView(request):
    ticker=request.query_params.get('ticker')
    stock_price_df = get_stock_price(ticker,start_date=datetime.now() + relativedelta(years=-5)).reset_index()
    json_data = stock_price_df[['Date','Open','High','Low','Close','Volume']].to_json(orient="values",date_format="epoch",double_precision=5)
    return HttpResponse(json_data, content_type="application/json")


