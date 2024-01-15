"""
    This module contains the services for the investment analysis page.
"""
import logging
import concurrent.futures
import threading
from typing import List, Tuple, cast
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from django.core.cache import cache
import inspect
from domain.stock_info_service import get_stock_price, get_stock_financial_report, \
    get_stock_financial_info_from_report , save_sp500_stocks_info
from domain.investment_analysis import infer_reasonable_share_price, eligibilitycheck
from pages.consts import SP500_STOCK_LIST
from .models import FinancialReportData, StockPriceHistoryData
from . import consts

logger = logging.getLogger(__name__)

locks_stock_price_history_data: dict = {}
locks_financial_report_data: dict = {}

def stock_price_history_data_cache_key(ticker):
    """
    Generate a cache key for stock price history data based on the ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        str: The cache key for stock price history.
    """
    return f"{consts.STOCK_PRICE_HISTORY_DATA}:{ticker}"

def financial_report_data_cache_key(ticker):
    """
    Generate a cache key for financial report data based on the ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        str: The cache key for financial report data.
    """
    return f"{consts.FINANCIAL_REPORT_DATA}:{ticker}"

def get_stock_price_history_data(ticker)-> StockPriceHistoryData:
    """
    Get the stock price history data for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        StockPriceHistoryData: The dataclass consist of daily and yearly stock price history .
    """
    stock_price_history_data = cache.get(stock_price_history_data_cache_key(ticker))
    if stock_price_history_data is None:
        if ticker not in locks_stock_price_history_data:
            locks_stock_price_history_data[ticker] = threading.Lock()
        
        lock = locks_stock_price_history_data[ticker]
        
        with lock:
            # Double check to avoid unnecessary refresh
            stock_price_history_data = cache.get(stock_price_history_data_cache_key(ticker))
            if stock_price_history_data is None:
                stock_price_history_data = refresh_stock_price_history_data_cache(ticker)
    return stock_price_history_data

# Update Stock price history Cache
def refresh_stock_price_history_data_cache(ticker) -> StockPriceHistoryData :
    """
    Refreshes the cache for the stock price history data of a given ticker.

    Args:
        ticker (str): The ticker symbol of the stock.
    """
    # Add code here to refresh the cache
    
    # trace the caller
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    logger.debug(f"Called by {caller_frame[1][3]}")
    dt_start = datetime.now()
    
    # If user select new stock, use multi threads to get both stock price history
    # and financial report

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        task_get_stock_price_history = executor.submit(get_stock_price, ticker,datetime.now() + relativedelta(years=-5))
  #      task_refresh_financial_report = executor.submit(refresh_financial_report_cache, ticker )
        stock_price_history = concurrent.futures.as_completed(task_get_stock_price_history)
        stock_price_history = task_get_stock_price_history.result()
  #      _ , _ , _ = task_refresh_financial_report.result()

 
    # Calculate yearly HIGH LOW AVERAGE last day  close share price
    stock_price_history['year'] = pd.DatetimeIndex(stock_price_history.index).year #pylint: disable=E1101
    stock_price_history['date'] = pd.DatetimeIndex(stock_price_history.index)
    yearly_close_price = stock_price_history[['year','Close']].loc[ stock_price_history.groupby('year').date.idxmax() ]
    yearly_close_price.rename(columns={'Close':'close'},inplace=True)
    yearly_stock_price = stock_price_history.groupby('year')['Close'].agg([('low','min'),('high','max'),'mean','count'])
    yearly_stock_price = pd.merge(yearly_stock_price, yearly_close_price, how='inner', on=['year'])
    stock_price_history_data = StockPriceHistoryData(stock_price_history, yearly_stock_price)
    cache.set(stock_price_history_data_cache_key(ticker), stock_price_history_data)
    logger.debug('refresh stock history and financial report cache take %s', str(datetime.now() - dt_start))
    return stock_price_history_data


def get_financial_report_data(ticker) -> FinancialReportData:
    """
    Get the financial report data for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        FinancialReportData: The financial report data.
    """
    financial_report_data = cache.get(financial_report_data_cache_key(ticker))
    if financial_report_data is None :
        if ticker not in locks_financial_report_data:
            locks_financial_report_data[ticker] = threading.Lock()
            
        lock = locks_financial_report_data[ticker]
        
        with lock:
            # Double check to avoid unnecessary refresh
            financial_report_data = cache.get(financial_report_data_cache_key(ticker))
            if financial_report_data is None:
                financial_report_data= refresh_financial_report_data_cache(ticker)
    
    return financial_report_data


def refresh_financial_report_data_cache(ticker):
    """
    Refresh the financial report data cache for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        FinancialReportData: A dataclass containing the financial report, financial info, and financial warning list.
    """
    # trace the caller
    current_frame = inspect.currentframe()
    caller_frame = inspect.getouterframes(current_frame, 2)
    logger.debug(f"Called by {caller_frame[1][3]}")
    
    dt_start = datetime.now()
    financial_report = get_stock_financial_report(ticker)
    financial_info = get_stock_financial_info_from_report(financial_report)
    #financial_report_np = financial_report.to_numpy()  # Convert DataFrame to NumPy array
    financial_report[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']] = np.round(
        financial_info[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']], 2)
    financial_report = pd.DataFrame(financial_report, columns=financial_info.columns)  # Convert back to DataFrame
    financial_warning_list = eligibilitycheck(ticker, financial_info)
    financial_report_data = FinancialReportData(financial_report, financial_info, financial_warning_list)
    cache.set(financial_report_data_cache_key(ticker), financial_report_data)
    logger.debug('refresh financial report data cache take %s ', str(datetime.now() - dt_start))
    return financial_report_data


def get_investment_suggestion(ticker, discount=0.05, margin=0.2):
    """
    Get the investment suggestion for a given stock ticker.

    Args:
        ticker (str): The ticker symbol of the stock.
        discount (float, optional): The discount rate for future cash flows. Defaults to 0.05.
        margin (float, optional): The margin of safety for the reasonable share price. Defaults to 0.2.

    Returns:
        float: The suggested reasonable share price.
    """
    stock_price_history = get_stock_price_history_data(ticker).stock_price_history
    financial_info = get_financial_report_data(ticker).financial_info
    suggestion = infer_reasonable_share_price(
        ticker, financial_info, stock_price_history, discount, margin)  # future 3 years
    return suggestion


def get_sp500_stock_list():
    """
    Get the list of SP500 stocks.

    Returns:
        list: The list of SP500 stocks.
    """
    stock_list = cache.get(SP500_STOCK_LIST)
    if stock_list is None:
        stock_list = refresh_sp500_stock_list_cache()
    return stock_list


def refresh_sp500_stock_list_cache():
    """
    Refresh the cache for the list of SP500 stocks.
    
    Returns:
        pandas.DataFrame: The sorted list of SP500 stocks.
    """
    stock_list = save_sp500_stocks_info().sort_values(by=['tickers'])
    cache.set(SP500_STOCK_LIST, stock_list)
    return stock_list
