"""
    This module contains the services for the investment analysis page.
"""
import logging
import concurrent.futures
from typing import List, Tuple, cast
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd
from django.core.cache import cache
from domain.stock_info_service import get_stock_price, get_stock_financial_report, \
    get_stock_financial_info_from_report , save_sp500_stocks_info
from domain.investment_analysis import infer_reasonable_share_price, eligibilitycheck
from pages.consts import SP500_STOCK_LIST
from . import consts

logger = logging.getLogger(__name__)

def stock_price_history_cache_key(ticker):
    """
    Generate a cache key for stock price history based on the ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        str: The cache key for stock price history.
    """
    return f"{consts.STOCK_PRICE_HISTORY}:{ticker}"

def yearly_stock_price_cache_key(ticker):
    """
    Generate a cache key for yearly stock price based on the ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        str: The cache key for yearly stock price.
    """
    return f"{consts.YEARLY_STOCK_PRICE}:{ticker}"

def financial_report_cache_key(ticker):
    """
    Generate a cache key for financial report based on the ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        str: The cache key for financial report.
    """
    return f"{consts.FINANCIAL_REPORT}:{ticker}"

def financial_info_cache_key(ticker):
    """
    Generate a cache key for financial info based on the ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        str: The cache key for financial info.
    """
    return f"{consts.FINANCIAL_INFO}:{ticker}"

def financial_warning_list_cache_key(ticker):
    """
    Generate a cache key for financial warning list based on the ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        str: The cache key for financial warning list.
    """
    return f"{consts.FINANCIAL_WARNING_LIST}:{ticker}"

def get_stock_price_history(ticker):
    """
    Get the stock price history for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        pandas.DataFrame: The stock price history.
    """
    stock_price_history = cache.get(stock_price_history_cache_key(ticker))
    if stock_price_history is None:
        stock_price_history, _ = refresh_stock_price_history_cache(ticker)
    return stock_price_history

def get_yearly_stock_price(ticker)-> pd.DataFrame:
    """
    Get the yearly stock price for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        pandas.DataFrame: The yearly stock price.
    """
    yearly_stock_price = cast(pd.DataFrame,
                              cache.get(yearly_stock_price_cache_key(ticker)) )
    if yearly_stock_price is None:
        _, yearly_stock_price = refresh_stock_price_history_cache(ticker)
    return yearly_stock_price

# Update Stock price history Cache
def refresh_stock_price_history_cache(ticker) :
    """
    Refreshes the cache for the stock price history of a given ticker.

    Args:
        ticker (str): The ticker symbol of the stock.
    """
    # Add code here to refresh the cache
    # If user select new stock, use multi threads to get both stock price history
    # and financial report
    dt_start = datetime.now()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        task_get_stock_price_history = executor.submit(get_stock_price, ticker,datetime.now() + relativedelta(years=-5))
        task_refresh_financial_report = executor.submit(refresh_financial_report_cache, ticker )
        stock_price_history = concurrent.futures.as_completed(task_get_stock_price_history)
        stock_price_history = task_get_stock_price_history.result()
        _ , _ , _ = task_refresh_financial_report.result()

    cache.set(stock_price_history_cache_key(ticker), stock_price_history)
    # Calculate yearly HIGH LOW AVERAGE last day  close share price
    stock_price_history['year'] = pd.DatetimeIndex(stock_price_history.index).year #pylint: disable=E1101
    stock_price_history['date'] = pd.DatetimeIndex(stock_price_history.index)
    yearly_close_price = stock_price_history[['year','Close']].loc[ stock_price_history.groupby('year').date.idxmax() ]
    yearly_close_price.rename(columns={'Close':'close'},inplace=True)
    yearly_stock_price = stock_price_history.groupby('year')['Close'].agg([('low','min'),('high','max'),'mean','count'])
    yearly_stock_price = pd.merge(yearly_stock_price, yearly_close_price, how='inner', on=['year'])
    logger.debug('refresh stock history and financial report cache take %s', str(datetime.now() - dt_start))
    return stock_price_history, yearly_stock_price


def get_financial_report(ticker):
    """
    Get the financial report for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        dict: The financial report.
    """
    financial_report = cache.get(financial_report_cache_key(ticker))
    if financial_report is None :
        financial_report, _ , _ = refresh_financial_report_cache(ticker)
    return financial_report

def get_financial_info(ticker) -> pd.DataFrame:
    """
    Get the financial information for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        dict: The financial information.
    """
    financial_info = cast(pd.DataFrame,
                          cache.get(financial_info_cache_key(ticker)) )
    if financial_info is None :
        _, financial_info, _ = refresh_financial_report_cache(ticker)
    return financial_info

def get_financial_warning_list(ticker):
    """
    Get the financial warning list for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        list: The financial warning list.
    """
    financial_warning_list = cache.get(financial_warning_list_cache_key(ticker))
    if (financial_warning_list is None ):
        _, _, financial_warning_list = refresh_financial_report_cache(ticker)
    return financial_warning_list

# Update Financial Report & Info Cache
def refresh_financial_report_cache(ticker) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
    """
    Refresh the financial report cache for a given stock ticker.
    
    Args:
        ticker (str): The ticker symbol of the stock.
        
    Returns:
        tuple: A tuple containing the financial report, financial info, and financial warning list.
    """
    dt_start = datetime.now()
    financial_report = get_stock_financial_report(ticker)
    financial_info = get_stock_financial_info_from_report(financial_report)
    #financial_report_np = financial_report.to_numpy()  # Convert DataFrame to NumPy array
    financial_report[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']] = np.round(
        financial_info[['roe', 'interestcoverageratio', 'epsgrowth', 'roa']], 2)
    financial_report = pd.DataFrame(financial_report, columns=financial_info.columns)  # Convert back to DataFrame
    financial_warning_list = eligibilitycheck(ticker, financial_info)
    cache.set(financial_report_cache_key(ticker), financial_report)
    cache.set(financial_info_cache_key(ticker), financial_info)
    cache.set(financial_warning_list_cache_key(ticker), financial_warning_list)
    logger.debug('refresh financial report cache take %s ', str(datetime.now() - dt_start))
    return financial_report, financial_info, financial_warning_list


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
    stock_price_history = get_stock_price_history(ticker)
    financial_info = get_financial_info(ticker)
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
