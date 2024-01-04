import pandas as pd
from pandas_datareader import data as pdr
import numpy as np
import numpy_financial as npf
import logging

logger = logging.getLogger(__name__)

def eligibilitycheck(ticker, dfformatted):
    """
    Given list of the companies, find out the feasibility to invest

    Check stock's financial health and prospect
    Warning Signs List based on value investing logic ###

    1. Been in market minimal 10 years
    2. Have the track records (EPS per year)
    3. Have efficiency (ROE > 15%) — Net income / shareholder equity
    4. Determine manipulation (ROA > 7%) — Net income / Total Asset
    5. Have small long term debt (Long term debt <5* total income)
    6. Low Debt to Equity
    7. Ability to pay interest: (Interest Coverage Ratio >3) — EBIT / Interest expenses

    return : array
    """
    pd.options.display.float_format = '{:,.2f}'.format
    legiblestock = True
    reasonlist = []

    # EPS increases over the year (consistent)
    for growth in dfformatted.epsgrowth:
        if growth < 0:
            legiblestock = False
            reasonlist.append(f'There is negative growth: {growth:.2f}')
            break
    # ROE > 0.15
    if dfformatted.roe.mean() < 0.13:
        legiblestock = False
        reasonlist.append(f'ROE mean is less than 0.13: {dfformatted.roe.mean():.2f}')
    # ROA > 0.07 (also consider debt to equity cause Assets = liabilities + equity)
    if dfformatted.roa.mean() < 0.07:
        legiblestock = False
        reasonlist.append('ROA mean is less than 0.07 : ' +
                          str('{:.2f}'.format(dfformatted.roa.mean())))
    # Long term debt < 5 * income
    if dfformatted.longtermdebt.tail(1).values[0] > 5*dfformatted.netincome.tail(1).values[0]:
        legiblestock = False
        reasonlist.append('Longterm Debt is 5 times the Net Income ')
    # Interest Coverage Ratio > 3
    if dfformatted.interestcoverageratio.tail(1).values[0] < 3:
        legiblestock = False
        reasonlist.append('Interest Coverage Ratio is less than 3 ')
    logger.debug('ticker %s, legiblestock %s, reasonlist %s', ticker, legiblestock, reasonlist)
    return reasonlist


def infer_reasonable_share_price(ticker, financialreportingdf, stockpricedf, discountrate, marginrate):
    """
    Infer the reasonable share price for a given ticker based on financial reporting data, stock price data, discount rate, and margin rate.

    Parameters:
    ticker (str): The ticker symbol of the stock.
    financialreportingdf (pandas.DataFrame): The financial reporting data for the stock.
    stockpricedf (pandas.DataFrame): The stock price data for the stock.
    discountrate (float): The discount rate used for valuation.
    marginrate (float): The margin rate used for valuation.

    Returns:
    float: The inferred reasonable share price.
    """
    # Add your code here

    years = 2  # period
    dfprice = pd.DataFrame(
        columns=['ticker', 'annualgrowthrate', 'lasteps', 'futureeps'])
    pd.options.display.float_format = '{:20,.2f}'.format

    # Find EPS Annual Compounded Growth Rate
    # annualgrowthrate =  financialreportingdf.epsgrowth.mean() #growth rate

    try:

        # Calcuate the rate per period
        # parameter:  periods , payment, present value, future value
        first_eps = financialreportingdf.eps.iloc[0]
        last_eps = financialreportingdf.eps.iloc[-1]
        # Adjust firstEPS at least 1 , prevent npf.rate get NaN
        if first_eps<1:
            adj = 1 - first_eps
            first_eps = first_eps + adj
            last_eps =  last_eps + adj
            
        annualgrowthrate = npf.rate(len(financialreportingdf.eps)-1, 0, -1 * first_eps,last_eps)

        # Non Conservative

        lasteps = financialreportingdf.eps.tail(1).values[0]  # presentvalue
        # conservative
        # lasteps = financialreportingdf.eps.mean()

    # np.fv, compute the future value. parameters: interest rate , periods, payment, present value
        futureeps = abs(npf.fv(annualgrowthrate, years, 0, lasteps))
        logger.debug('futureeps %s, annualgrowthrate %s, years %s, lasteps %s ', futureeps,annualgrowthrate, years, lasteps)
        dfprice.loc[0] = [ticker, annualgrowthrate, lasteps, futureeps]
    except Exception as e:
        logger.error('eps does not exist: %s', str(e))
    dfprice.set_index('ticker', inplace=True)
    # conservative
    dfprice['peratio'] = find_minimum_PER(stockpricedf, financialreportingdf)
    # future stock price
    dfprice['FV'] = dfprice['futureeps'] * dfprice['peratio']
    #print('dfprice:\n',dfprice)
    #print('discountrate: %s' % discountrate)
    dfprice['PV'] = abs(npf.pv(discountrate, years, 0, fv=dfprice['FV']))
    if dfprice['FV'].values[0] > 0:
        dfprice['marginprice'] = dfprice['PV']*(1-marginrate)
    else:
        dfprice['marginprice'] = 0
    dfprice['lastprice'] = stockpricedf.Close.tail(1).values[0]

    dfprice['suggestion'] = np.where(
        (dfprice['lastprice'] < dfprice['marginprice']), 'BUY', 'SELL')
    return dfprice


def find_minimum_PER(stockpricedf, financialreportingdf):
    """ 
        Given the share price and eps of per year , calculate PE ration of each year then return the minimum one.
    """
    #finrepdf = financialreportingdf.set_index('index')
  #  finrepdf.rename(columns={"index": "year"})
    stockpricedf['year'] = pd.DatetimeIndex(stockpricedf.index).year
    logger.debug("stockpricedf['year'] %s, pd.DatetimeIndex(stockpricedf.index).year %s",stockpricedf['year'],pd.DatetimeIndex(stockpricedf.index).year)
    # base on yearly mean close price 
    #gframe = stockpricedf.groupby('year').head(1).set_index('year')
    gframe = stockpricedf.groupby('year')['Close'].agg(['mean'])
    pricebyyear = pd.DataFrame()
    pricebyyear['Close'] = gframe['mean']
    pricebyyear['eps'] = financialreportingdf['eps']
    pricebyyear['peratio'] = pricebyyear['Close']/pricebyyear['eps']
    
    return pricebyyear['peratio'].min()
