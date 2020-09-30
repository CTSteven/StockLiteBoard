from django.core.cache import cache
import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import concurrent.futures
import logging
from domain.stock_info_service import get_stock_price, get_stock_financial_report, \
    get_stock_financial_info_from_report , save_sp500_stocks_info
from domain.investment_analysis import infer_reasonable_share_price, eligibilitycheck
from pages.consts import SP500_STOCK_LIST
from . import consts 

logger = logging.getLogger(__name__)

def stock_price_history_cache_key(ticker):
    return "%s:%s" % ( consts.STOCK_PRICE_HISTORY , ticker)

def yearly_stock_price_cache_key(ticker):
    return "%s:%s" % ( consts.YEARLY_STOCK_PRICE , ticker)

def financial_report_cache_key(ticker):
    return "%s:%s" % ( consts.FINANCIAL_REPORT , ticker)

def financial_info_cache_key(ticker):
    return "%s:%s" % ( consts.FINANCIAL_INFO , ticker)

def financial_warning_list_cache_key(ticker):
    return "%s:%s" % ( consts.FINANCIAL_WARNING_LIST , ticker)

def getStockPriceHistory(ticker):
    stock_price_history = cache.get(stock_price_history_cache_key(ticker))
    if (stock_price_history is None ):
        stock_price_history, _ = refreshStockPriceHistoryCache(ticker)
    return stock_price_history

def getYearlyStockPrice(ticker):
    yearly_stock_price = cache.get(yearly_stock_price_cache_key(ticker))
    if (yearly_stock_price is None ):
        _, yearly_stock_price = refreshStockPriceHistoryCache(ticker)
    return yearly_stock_price

# Update Stock price history Cache
def refreshStockPriceHistoryCache(ticker):
    # If user select new stock , use multi threads to get both stock price history and financial report
    dt_start = datetime.now()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        task_get_stock_price_history = executor.submit(get_stock_price, ticker,datetime.now() + relativedelta(years=-5))
        task_refresh_financial_report = executor.submit(refreshFinancialReportCache, ticker )
        stock_price_history = concurrent.futures.as_completed(task_get_stock_price_history)
        stock_price_history = task_get_stock_price_history.result()
        _ , _ , _ = task_refresh_financial_report.result()

    cache.set(stock_price_history_cache_key(ticker), stock_price_history)
    # Calculate yearly HIGH LOW AVERAGE last day  close share price 
    stock_price_history['year'] = pd.DatetimeIndex(stock_price_history.index).year
    stock_price_history['date'] = pd.DatetimeIndex(stock_price_history.index)
    yearly_close_price = stock_price_history[['year','Close']].loc[ stock_price_history.groupby('year').date.idxmax() ]
    yearly_close_price.rename(columns={'Close':'close'},inplace=True)
    yearly_stock_price = stock_price_history.groupby('year')['Close'].agg([('low','min'),('high','max'),'mean','count'])
    yearly_stock_price = pd.merge(yearly_stock_price, yearly_close_price, how='inner', on=['year'])
    cache.set(yearly_stock_price_cache_key(ticker), yearly_stock_price)
    logger.debug('refresh stock history and financial report cache take %s' %( str( datetime.now() - dt_start) ) )
    return stock_price_history, yearly_stock_price


def getFinancialReport(ticker):
    financial_report = cache.get(financial_report_cache_key(ticker))
    if (financial_report is None ):
        financial_report, _ , _ = refreshFinancialReportCache(ticker)
    return financial_report

def getFinancialInfo(ticker):
    financial_info = cache.get(financial_info_cache_key(ticker))
    if (financial_info is None ):
        _, financial_info, _ = refreshFinancialReportCache(ticker)
    return financial_info

def getFinancialWarningList(ticker):
    financial_warning_list = cache.get(financial_warning_list_cache_key(ticker))
    if (financial_warning_list is None ):
        _, _, financial_warning_list = refreshFinancialReportCache(ticker)
    return financial_warning_list

# Update Financial Report & Info Cache
def refreshFinancialReportCache(ticker):
    dt_start = datetime.now()
    financial_report = get_stock_financial_report(ticker)
    financial_info = get_stock_financial_info_from_report(financial_report)
    financial_report[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']] = np.round(
        financial_info[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']], 2)
    financial_warning_list = eligibilitycheck(ticker, financial_info)
    cache.set(financial_report_cache_key(ticker), financial_report)
    cache.set(financial_info_cache_key(ticker), financial_info)
    cache.set(financial_warning_list_cache_key(ticker), financial_warning_list)
    logger.debug('refresh financial report cache take %s' %( str( datetime.now() - dt_start) ) )
    return financial_report , financial_info , financial_warning_list


def getInvestmentSuggestion(ticker, discount=0.05,margin=0.2):
    stock_price_history = getStockPriceHistory(ticker)
    financial_info = getFinancialInfo(ticker)
    suggestion = infer_reasonable_share_price(
            ticker, financial_info, stock_price_history, discount, margin) # future 3 years
    return suggestion
      

def getSP500StockList():
    stock_list = cache.get(SP500_STOCK_LIST)
    if (stock_list is None ):
       stock_list = refreshSP500StockListCache()
    return stock_list


def refreshSP500StockListCache():
    stock_list = save_sp500_stocks_info().sort_values(by=['tickers'])
    cache.set(SP500_STOCK_LIST, stock_list)
    return stock_list

