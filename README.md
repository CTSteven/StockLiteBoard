## Simple Value Investing Dashboard, using python 

This application , refer [Vincent Tatan's blog and project at GitHub ](https://towardsdatascience.com/value-investing-dashboard-with-python-beautiful-soup-and-dash-python-43002f6a97ca) , collect company's stock price history , financial summary information from professional financial website ( MarketWatch) and yahoo ( pandas' datareader) to do simple rule-based analysis and infer reasonable share price then give user a hint about sell or buy decision .

Value investment and technical analysis are two mainstream in stock market. To increase probability of winning , investors now should know more than that in this rapid change era . Maybe buy good funds is better idea for general investors.  Even professional fund managers face big challenge in collecting and interpreting information to make good decision , as soon as possible , in investment portfolio and when to buy or sell share . 

It's fun to develop application for investment activities. 

Python has lots of packages for data processing and visualization, it is easy to use too.  Thanks Vincent share his idea and project , I have learn a lot.  

Following are some changes I make from that project :
- Change UI layout and apply Bootstrap 4
- Could execute in Jupyter notebook
- File name are also changed and do some code refactoring
- Get data through API from stock market data company is more reliable and efficient than parsing web page from website , but this part left no modification.

.


It's great to design a system could auto collect and read information then give user more accurate suggestion of portfolio and market timing. Such system should already exist.  Big Data and AI technology will make them more powerful.  Join such project will be fun !

.

## Warning : ##
This application has not been rigorously tested and its domain rules are very simple which are hard to cover the complexity of real stock market. There may be also wrong information introduced by some not found some bugs.
## <span style='color:#a00000'>This application is not mature enough and risky to be your decision tool in real stock market !</span>



-------

### Screenshots : 

![](data/../assets/dashboard-s1.png)

![](data/../assets/dashboard-s2.png)

Main process :
1. Get stock ticker and name to be data source of dropdown control
2. Get stock price history from yahoo through pandas datareader when user choose a stock from dropdown control
3. Plot stock k chart , sma  , macd , rsi lines
4. Get stock financial information from financial website to do basic analysis and infer future value for trading decision.

Stock data sample from yahoo:
![](data/../assets/stockpricedata_from_yahoo.png)

### Parsing fincial information from MarketWatch web site
For example, to get Google's financial information from this url : https://www.marketwatch.com/investing/stock/GOOG/financials



.

.


Please refer to [Vincent Tatan's blog ](https://towardsdatascience.com/value-investing-dashboard-with-python-beautiful-soup-and-dash-python-43002f6a97ca) to learn complete explanation.