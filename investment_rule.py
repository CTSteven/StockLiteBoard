import pandas as pd
from pandas_datareader import data as pdr
import numpy as np
import numpy_financial as npf

### Check stock's financial health and prospect
def eligibilitycheck(dfformatted):
    
    legiblestock = True
    reasonlist=[]

    # print (dfformatted)
    # EPS increases over the year (consistent)
    for growth in dfformatted.epsgrowth:
        if growth<0:
            legiblestock = False
            reasonlist.append('there is negative growth '+str(growth))
            break
    # ROE > 0.15
    if dfformatted.roe.mean()<0.13:
            legiblestock = False
            reasonlist.append('roe mean is less than 0.13 '+ str(dfformatted.roe.mean()))
    # ROA > 0.07 (also consider debt to equity cause Assets = liabilities + equity)
    if dfformatted.roa.mean()<0.07:
            legiblestock = False
            reasonlist.append('roa mean is less than 0.07 ' + str(dfformatted.roa.mean()))
    # Long term debt < 5 * income
    if dfformatted.longtermdebt.tail(1).values[0]>5*dfformatted.netincome.tail(1).values[0]:
            legiblestock = False
            reasonlist.append('longtermdebt is 5 times the netincome ')
    # Interest Coverage Ratio > 3
    if dfformatted.interestcoverageratio.tail(1).values[0]<3:
            legiblestock = False
            reasonlist.append('Interestcoverageratio is less than 3 ')
#     print ticker,legiblestock,reasonlist
    return reasonlist

def generate_price_df(ticker,financialreportingdf,stockpricedf,discountrate,marginrate,after_years=10):
	dfprice = pd.DataFrame(columns =['ticker','annualgrowthrate','lasteps','futureeps'])
	pd.options.display.float_format = '{:20,.2f}'.format

	# Find EPS Annual Compounded Growth Rate
	# annualgrowthrate =  financialreportingdf.epsgrowth.mean() #growth rate

	try:
		print("1st year EPS %f "%financialreportingdf.eps.iloc[0])
		print("5th year EPS %f"%financialreportingdf.eps.iloc[-1])
        # Calcuate interest rate per period
        # parameter:  periods , payment, present value, future value
		annualgrowthrate =  npf.rate(5, 0, -1*financialreportingdf.eps.iloc[0], financialreportingdf.eps.iloc[-1])
		print("Annual Growth Rate %f"%annualgrowthrate)

		# Non Conservative
		lasteps = financialreportingdf.eps.tail(1).values[0] #presentvalue

		# conservative
		# lasteps = financialreportingdf.eps.mean()

		years  = after_years #period
        # np.fv, compute the future value. parameters: interest rate , periods, payment, present value
		futureeps = abs(npf.fv(annualgrowthrate,years,0,lasteps))
		dfprice.loc[0] = [ticker,annualgrowthrate,lasteps,futureeps]
	except:
		print('eps does not exist')
	    
	dfprice.set_index('ticker',inplace=True)

	#conservative
	dfprice['peratio'] = findMinimumEPS(stockpricedf,financialreportingdf)
    
    # future stock price
	dfprice['FV'] = dfprice['futureeps']*dfprice['peratio']

	dfprice['PV'] = abs(npf.pv(discountrate,years,0,fv=dfprice['FV']))

	if dfprice['FV'].values[0] > 0:
		dfprice['marginprice'] = dfprice['PV']*(1-marginrate)
	else:
		dfprice['marginprice'] = 0

	dfprice['lastshareprice']=stockpricedf.Close.tail(1).values[0]

	dfprice['decision'] = np.where((dfprice['lastshareprice']<dfprice['marginprice']),'BUY','SELL')

	return dfprice


def findMinimumEPS (stockpricedf,financialreportingdf):
    # Given the share price
    #finrepdf = financialreportingdf.set_index('index')
    finrepdf = financialreportingdf
    stockpricedf['year'] = pd.DatetimeIndex(stockpricedf.index).year
    gframe = stockpricedf.groupby('year').head(1).set_index('year')
    pricebyyear = pd.DataFrame()
    pricebyyear['Close']  = gframe['Close']
    pricebyyear['eps'] = finrepdf['eps']
    pricebyyear['peratio'] = pricebyyear['Close']/pricebyyear['eps']
    print("PE ration %f"%pricebyyear['peratio'].min())
    return pricebyyear['peratio'].min()


