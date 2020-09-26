import pandas as pd
from pandas_datareader import data as pdr
import numpy as np
import numpy_financial as npf


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

    # print (dfformatted)
    # EPS increases over the year (consistent)
    for growth in dfformatted.epsgrowth:
        if growth < 0:
            legiblestock = False
            reasonlist.append('there is negative growth '+str(growth))
            break
    # ROE > 0.15
    if dfformatted.roe.mean() < 0.13:
        legiblestock = False
        reasonlist.append('roe mean is less than 0.13 ' +
                          str(dfformatted.roe.mean()))
    # ROA > 0.07 (also consider debt to equity cause Assets = liabilities + equity)
    if dfformatted.roa.mean() < 0.07:
        legiblestock = False
        reasonlist.append('roa mean is less than 0.07 ' +
                          str(dfformatted.roa.mean()))
    # Long term debt < 5 * income
    if dfformatted.longtermdebt.tail(1).values[0] > 5*dfformatted.netincome.tail(1).values[0]:
        legiblestock = False
        reasonlist.append('longtermdebt is 5 times the netincome ')
    # Interest Coverage Ratio > 3
    if dfformatted.interestcoverageratio.tail(1).values[0] < 3:
        legiblestock = False
        reasonlist.append('Interestcoverageratio is less than 3 ')
#     print ticker,legiblestock,reasonlist
    return reasonlist


def infer_reasonable_share_price(ticker, financialreportingdf, stockpricedf, discountrate, marginrate, after_years=10):
    years = after_years  # period
    #futureeps_column_name = 'futureeps(%d)' % (years)
    futureeps_column_name = 'futureeps'
    dfprice = pd.DataFrame(
        columns=['ticker', 'annualgrowthrate', 'lasteps', futureeps_column_name])
    pd.options.display.float_format = '{:20,.2f}'.format

    # Find EPS Annual Compounded Growth Rate
    # annualgrowthrate =  financialreportingdf.epsgrowth.mean() #growth rate

    # print('financialreportdf:\n',financialreportingdf)
    try:

        # Calcuate interest rate per period
        # parameter:  periods , payment, present value, future value
        annualgrowthrate = npf.rate(len(financialreportingdf.eps), 0, -1 *
                                    financialreportingdf.eps.iloc[0], financialreportingdf.eps.iloc[-1])
        #print("Annual Growth Rate %f" % annualgrowthrate)

        # Non Conservative
        lasteps = financialreportingdf.eps.tail(1).values[0]  # presentvalue

        # conservative
        # lasteps = financialreportingdf.eps.mean()

    # np.fv, compute the future value. parameters: interest rate , periods, payment, present value
        futureeps = abs(npf.fv(annualgrowthrate, years, 0, lasteps))
        dfprice.loc[0] = [ticker, annualgrowthrate, lasteps, futureeps]
    except:
        print('eps does not exist')
    dfprice.set_index('ticker', inplace=True)
    # conservative
    dfprice['peratio'] = findMinimumPER(stockpricedf, financialreportingdf)
    # future stock price
    dfprice['FV'] = dfprice[futureeps_column_name] * dfprice['peratio']
    # print('dfprice:\n',dfprice)
    dfprice['PV'] = abs(npf.pv(discountrate, years, 0, fv=dfprice['FV']))
    if dfprice['FV'].values[0] > 0:
        dfprice['marginprice'] = dfprice['PV']*(1-marginrate)
    else:
        dfprice['marginprice'] = 0
    dfprice['lastprice'] = stockpricedf.Close.tail(1).values[0]

    dfprice['suggestion'] = np.where(
        (dfprice['lastprice'] < dfprice['marginprice']), 'BUY', 'SELL')
    return dfprice


def findMinimumPER(stockpricedf, financialreportingdf):
    """ 
        Given the share price and eps of per year , calculate PE ration of each year then return the minimum one.
    """
    finrepdf = financialreportingdf.set_index('index')
    finrepdf.rename(columns={"index": "year"})
    stockpricedf['year'] = pd.DatetimeIndex(stockpricedf.index).year
    gframe = stockpricedf.groupby('year').head(1).set_index('year')
    pricebyyear = pd.DataFrame()
    pricebyyear['Close'] = gframe['Close']
    pricebyyear['eps'] = finrepdf['eps']
    pricebyyear['peratio'] = pricebyyear['Close']/pricebyyear['eps']
    
    return pricebyyear['peratio'].min()
