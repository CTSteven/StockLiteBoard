""" Services for Stock Information """
from pandas_datareader import data as pdr
from datetime import datetime as dt
from typing import cast, Dict
import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
yf.pdr_override()

from .utils import *

logger = logging.getLogger(__name__)

### Extract lists of the stocks with their tickers
def save_sp500_stocks_info():
    """
    Save S&P 500 stock information.
    """
    # Code implementation here
    resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(resp.text,'lxml')
    table = soup.find('table',{'class':'wikitable sortable'})
    stocks_info=[]
    tickers, securities, gics_industries, gics_sub_industries = [],[],[],[]
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[0].text
        security = row.findAll('td')[1].text
        gics_industry = row.findAll('td')[3].text
        gics_sub_industry = row.findAll('td')[4].text
        
        tickers.append(ticker.replace(r"\n","").strip())
        securities.append(security)
        gics_industries.append(gics_industry)
        gics_sub_industries.append(gics_sub_industry)

    stocks_info.append(tickers)
    stocks_info.append(securities)
    stocks_info.append(gics_industries)
    stocks_info.append(gics_sub_industries)

    stocks_info_df = pd.DataFrame(stocks_info).T
    stocks_info_df.columns=['tickers','security','gics_industry','gics_sub_industry']
    stocks_info_df['seclabels'] = 'SP500'

    stocks_info_df['labels'] = stocks_info_df[['tickers','security', 'gics_industry','gics_sub_industry']].apply(lambda x: ',  '.join(x), axis=1)

    return stocks_info_df

def get_stocks_ipywidgets_options():
    """
    Get options for stocks in IPywidgets format.
    """
    #df =  save_sp500_stocks_info()
    df = get_taiwan_stocks_info()
    options = list(zip( df['labels'],df['tickers']+'.tw' ))
    options.insert(0,('',''))
    return  options

def get_stocks_dash_options():
    """
    Get options for stocks in Dash format.
    """
    df =  save_sp500_stocks_info()
    #df = get_taiwan_stocks_info()
    dictlist = []
    for index, row in df.iterrows():
        dictlist.append({'value':row['tickers'], 'label':row['labels']})
    return dictlist

# Tickers from russell
# This function will return empty array until the csv file of Russell components is available.
def save_russell_info():
    """
    Save Russell stock information.
    """
    print("Getting russell stocks info")
    russell_csv_url = None
    dictlist = []
    if (russell_csv_url != None):
        dfrussel=pd.read_csv(russell_csv_url,index_col='Symbol')
        dfrussel['tickers'] = dfrussel.index.str.upper()
        dfrussel['tickers'] = dfrussel['tickers'].replace(r"\n", " ")
        dfrussel['security'] = dfrussel.Description.str.title()
        dfrussel['gics_industry'] = dfrussel.Sector.str.lower()
        dfrussel['gics_sub_industry'] = dfrussel.Industry.str.lower()
        dfrussel['seclabels'] = 'RUSSELL'

        dfrussel['labels'] = dfrussel[['tickers','security','gics_industry','gics_sub_industry','seclabels']].apply(lambda x: ' - '.join(x), axis=1)

        for index, row in dfrussel.iterrows():
            dictlist.append({'value':row['tickers'], 'label':row['labels']})
    else:
        print("Warning ! Russell stock list csv file not found !")

    return dictlist

### Extract lists of the stocks with their tickers
def get_taiwan_stocks_info():  
    #resp = requests.get('https://isin.twse.com.tw/isin/C_public.jsp?strMode=2')
    #soup = BeautifulSoup(resp.text,'lxml')
    url = "./data/taiwan_stock_list_20200906.html"
    page = open(url,encoding='ms950')
    soup = BeautifulSoup(page.read())
    rows = [row for row in soup.find_all('tr') if len(row.findAll('td'))>5 and row.findAll('td')[5].text=='ESVUFR'  ]
    stocks_info=[]
    tickers, securities, gics_industries, gics_sub_industries = [],[],[],[]
    for row in rows:
        company = row.findAll('td')[0].text.split()
        ticker = company[0]
        security = company[1]
        gics_industry = row.findAll('td')[3].text
        gics_sub_industry = row.findAll('td')[4].text
        
        tickers.append(ticker.replace(r"\n"," "))
        securities.append(security)
        gics_industries.append(gics_industry)
        gics_sub_industries.append(gics_sub_industry)

    stocks_info.append(tickers)
    stocks_info.append(securities)
    stocks_info.append(gics_industries)
    stocks_info.append(gics_sub_industries)

    stocks_info_df = pd.DataFrame(stocks_info).T
    stocks_info_df.columns=['tickers','security','gics_industry','gics_sub_industry']
    stocks_info_df['seclabels'] = 'TWSE'
    stocks_info_df['labels'] = stocks_info_df[['tickers','security', 'gics_industry','gics_sub_industry','seclabels']].apply(' - '.join, axis=1)

    return stocks_info_df


# self append other stock list
def save_self_stocks_info():
    """
    Save self stocks information.
    """

    dictlist = []

    dictlist.append({'value':'ajbu', 'label':'AJBU Keppel DC Reit Data REITS SA'})
    dictlist.append({'value':'gme', 'label':'GME Game Stop Corp SA'})
    dictlist.append({'value':'aeg', 'label':'AEG Aegon Insurance SA'})
    dictlist.append({'value':'ntic', 'label':'NTIC Northern Technologies International SA'})
    dictlist.append({'value':'sq', 'label':'SQ Square SA'})
    dictlist.append({'value':'kbsty', 'label':'Kobe steel'})
    dictlist.append({'value':'NESN', 'label':'Nestle'})
    dictlist.append({'value':'BN', 'label':'Danone'})
    dictlist.append({'value': 'DATA', 'label': 'Tableau Software Data Visualization'})
    dictlist.append({'value': 'S58','label':'SATS'})

    return dictlist


def get_stock_price(ticker, start_date, end_date=dt.now()) -> pd.DataFrame:
    """
    Get the stock price data for a given ticker and date range from yahoo.
    
    Args:
        ticker (str): The stock ticker symbol.
        start_date (datetime): The start date of the price data.
        end_date (datetime, optional): The end date of the price data. Defaults to the current date.
    
    Returns:
        pd.DataFrame: The stock price data.
    """
    if ticker is not None:
        # ticker='2330.tw'
        # ticker='GOOG'
        try:
            logger.debug("ticker : %s, start_date : %s, end_date : %s", ticker,start_date, end_date)
            stock_price_data = pdr.get_data_yahoo(ticker.strip(), start=start_date, end=end_date)
            logger.debug("total %d  stock price records of ticker %s from yahoo \n", stock_price_data.size, ticker)
            return cast(pd.DataFrame,
                        stock_price_data
            )
        except Exception as e:
            logger.error("Exception : %s", e)
            raise ValueError('Retrieve stock price data from yahoo failed') from e
    else:
        raise ValueError('Missing stock ticker parameter')


def get_stock_financial_report(ticker) -> pd.DataFrame:
    """
      Get stock's financial information by parsing web page in MarketWatch website.
    """
    if ticker is not None:
        # ticker='2330.tw'
        # ticker='GOOG'
        try:
            ticker = ticker.strip()
            financial_url = 'https://www.marketwatch.com/investing/stock/%s/financials'%ticker
            balancesheet_url = 'https://www.marketwatch.com/investing/stock/%s/financials/balance-sheet'%ticker

            text_soup_financials = BeautifulSoup(requests.get(financial_url).text,"lxml")
            text_soup_balancesheet = BeautifulSoup(requests.get(balancesheet_url, timeout=10).text,"lxml")

            # Income Statement
            titlesfinancials = text_soup_financials.findAll('td',{'class':'fixed--column'})

            financial_info : Dict[str,list]= {
                'eps': [],
                'netincome': [],
                'shareholderequity':[],
                'longtermdebt': [],
                'interestexpense': [],
                'ebitda': []
            }

            for title in titlesfinancials:
                if 'EPS (Basic)' in title.text:
                    financial_info['eps'].append([td.text for td in title.parent.findAll('td')[1:6]])
                if 'Net Income' in title.text:
                    financial_info['netincome'].append([td.text for td in title.parent.findAll('td')[1:6]])
                if 'Interest Expense' in title.text:
                    financial_info['interestexpense'].append ([td.text for td in title.parent.findAll('td')[1:6]])
                if 'EBITDA' in title.text:
                    financial_info['ebitda'].append ([td.text for td in title.parent.findAll('td')[1:6]])

            # Balance sheet
            titlesbalancesheet = text_soup_balancesheet.findAll('td', {'class': 'fixed--column'})

            for title in titlesbalancesheet:
                if 'Total Shareholders\' Equity' in title.text:
                    financial_info['shareholderequity'].append( [td.text for td in title.parent.findAll('td')[1:6]])
                if 'Long-Term Debt' in title.text:
                    financial_info['longtermdebt'].append( [td.text for td in title.parent.findAll('td')[1:6]])

            ## Make it into Dataframes
            #df= pd.DataFrame({'eps': eps,'epsgrowth': epsgrowth,'netincome': netincome,'shareholderequity':shareholderequity,'roa': roa,'longtermdebt': longtermdebt,'interestexpense':interestexpense,'ebitda': ebitda},index=range(dt.today().year-5,dt.today().year))
            df= pd.DataFrame({'eps': financial_info['eps'][0],
                            'epsgrowth': financial_info['eps'][1],
                            'netincome': financial_info['netincome'][0],
                            'shareholderequity':financial_info['shareholderequity'][0],
                            'roa': financial_info['shareholderequity'][1],
                            'longtermdebt': financial_info['longtermdebt'][0],
                            'interestexpense':financial_info['interestexpense'][0],
                            'ebitda': financial_info['ebitda'][0],
                            'year':range(dt.today().year-5,dt.today().year)})
            df = df.set_index('year')
            # convert financial report money format to numeric
            #dfformatted = df.apply(financial_report_format)

            # Adding roe, interest coverage ratio
            #dfformatted['roe'] = dfformatted.netincome/dfformatted.shareholderequity
            #dfformatted['interestcoverageratio'] = dfformatted.ebitda/dfformatted.interestexpense
            return df
        except Exception as e:
            logger.error("Exception : %s", e)
            raise ValueError('Retrieve stock financial report data from marketwatch failed') from e
    else:
        raise ValueError('Missing stock ticker parameter')

# Convert report formatted currency to number and add row , interestcoverageratio
def get_stock_financial_info_from_report(stock_financial_report: pd.DataFrame) -> pd.DataFrame:
    """
    Get stock's financial information from the given financial report.
    
    Args:
        stock_financial_report (pd.DataFrame): The financial report of the stock.
    
    Returns:
        pd.DataFrame: The formatted financial information with added ROE and interest coverage ratio.
    """
    # Format all the number in dataframe
    dfformatted = stock_financial_report.apply(financial_report_format)

    # Adding roe, interest coverage ratio
    dfformatted['roe'] = dfformatted.netincome/dfformatted.shareholderequity
    dfformatted['interestcoverageratio'] = dfformatted.ebitda/dfformatted.interestexpense
    
    return dfformatted