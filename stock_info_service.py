import requests
from bs4 import BeautifulSoup
import pandas as pd
from pandas_datareader import data as pdr
from datetime import datetime as dt
import matplotlib.pyplot as plt
import cufflinks as cf
import plotly.offline as plyo

### Extract lists of the stocks with their tickers
def save_sp500_stocks_info():  
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
    stocks_info_df['seclabels'] = 'SP500'
    stocks_info_df['labels'] = stocks_info_df[['tickers','security', 'gics_industry','gics_sub_industry','seclabels']].apply(lambda x: ' '.join(x), axis=1)

    return stocks_info_df

def get_stocks_ipywidgets_options():
    #df =  save_sp500_stocks_info()
    df = get_taiwan_stocks_info()
    options = list(zip( df['labels'],df['tickers']+'.tw' ))
    options.insert(0,('',''))
    return  options

def get_stocks_dash_options():
    df =  save_sp500_stocks_info()
    dictlist = []
    for index, row in df.iterrows():
        dictlist.append({'value':row['tickers'], 'label':row['labels']})
    return dictlist

# Tickers from russell
# This function will return empty array until the csv file of Russell components is available.
def save_russell_info():
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

        dfrussel['labels'] = dfrussel[['tickers','security','gics_industry','gics_sub_industry','seclabels']].apply(lambda x: ' '.join(x), axis=1)

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
    stocks_info_df['labels'] = stocks_info_df[['tickers','security', 'gics_industry','gics_sub_industry','seclabels']].apply(lambda x: ' '.join(x), axis=1)

    return stocks_info_df


# self append other stock list
def save_self_stocks_info():
    print("Adding own list of stocks info")

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

### Get stock price record from yahoo
def get_stock_price(ticker,start_date,end_date=dt.now()):
    if (ticker != None):
        #ticker='2330.tw'
        #ticker='GOOG'
        return pdr.DataReader(
            ticker.strip(),data_source='yahoo',start=dt(2020,1,1),end=end_date
        )
    else:
        print('Need stock ticker parameter')

def plot_stock_chart(ticker,title,stockprice_df):
    plt.figure(figsize=(20,8))
    plt.plot(stockprice_df.index,stockprice_df.Close)
    #plt.plot(stockprice_df.index,stockprice_df.Open)
    #plt.plot(stockprice_df.index, (stockprice_df.Close + stockprice_df.Open) / 2.0 )
    plt.title('Google stock price',fontsize=18)
    plt.show()

### Draw classic stock K chart
def plot_stock_k_chart(ticker):
    title=''
    if (ticker==None or ticker.strip()==''):
        return None
    stockprice_df=get_stock_price(ticker,dt(2020,1,1),end_date=dt.now())  
    quotes = stockprice_df[['Open','High','Low','Close','Volume']]
    qf = cf.QuantFig(
        quotes,
        title=title,
        legend='top',
        name='K線圖',
        up_color='red',
        down_color='green'
    )
    qf.add_sma(
        periods=5,
        column='Close',
        name='sma-5',
        str='5日線',
        color='red'
    )
    qf.add_sma(
        periods=20,
        column='Close',
        name='sma-20',
        str='20日線'
    )
    #qf.add_volume()
    qf.add_macd()
    qf.add_rsi(periods=14, showbands=False)
    #print(ticker)
  #  fig = plyo.iplot(
  #      qf.iplot(asFigure=True,    dimensions=(800,600)),
  #      filename='qf_img'
  #  )
    #return qf.iplot(asFigure=True,    dimensions=(800,600))
    #return qf.iplot()
    return qf.iplot()
