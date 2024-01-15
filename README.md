## Implement Simple Stock Investment Dashboard with python 
---

### Go to [ demo site ](https://stock-dashboard-c2s6b2cyea-de.a.run.app)

### Purpose

This project is a practice to learn how to build web application in Python after finished some Deep Learning courses with Jupyter Notebook. 
I found Vincent's blog about using python to build investment tool to analyze and predict stock's reasonable price based on predicted future value. I am interest in investment. I start to build 1st version , mainly refer to  Vincent's project. 
( You can go to [Vincent Tatan's blog and GitHub project ](https://towardsdatascience.com/value-investing-dashboard-with-python-beautiful-soup-and-dash-python-43002f6a97ca) to get more information. )
 
After 1st version , I migrate web framework , redesign  UI , improve performance, add technical analysis charts , try to make this tool more easy to use.  You can go to [ demo site ](https://stock-dashboard-c2s6b2cyea-de.a.run.app) to try it out.

This application implement simplified model to predict expected stock price. 
1. Annual_growth
   - npf.rate(4, 0 , - 1st_year_eps , 5th_year_eps ) , npf is numpy financial package 
2. PE Ratio
   - yearly mean stock price /  EPS , and select minimum of recent 5 year
3. EPS after 2 years later , Future EPS
   - npf.fv( Annual_growth, 2 years , 0, 5th_year_eps)
4. Future Value
   -  Future EPS x PR Ratio
5. Present Value 
   -  npf.pv( Dicount Rate , 2 years, 0, Future Value)
6. Expected Reasonable Price Range , add on +/- margin rate 
   -  Present Value x ( 1  +/- Margin Rate )
  
If you try out at demo site, you'll find most price prediction are very different from real market behavior. These business rules are obviously not enough. It's only POC.

So, don't use this application in real market decision ! ! ! 

Some experts have already developed models and software to solve financial market challenges, like the true story introduced in this book ["The Man Who Solved the Market"](https://www.amazon.com/Man-Who-Solved-Market-Revolution/dp/073521798X). Though the book touch lightly on tech details, many resource around similar topic are available on Web and GitHub.  I have found some links : 
- [Awesome AI in Finance](https://github.com/georgezouq/awesome-ai-in-finance)
- [Machine Learning for Algorithmic Trading](https://github.com/PacktPublishing/Machine-Learning-for-Algorithmic-Trading-Second-Edition)

Lots of domain knowledge and skills are required to build similar system.

[The Wall Street Journal (2021-01-18) : <br>Quant hedge fund tells clients that drop of 20% to 30% was partly due to increased volatility.  ](https://www.wsj.com/articles/renaissance-says-losses-should-have-been-expected-at-some-point-11611008784)
<br> Wow, even the best model won't always beat the market ...

---
## Warning : ##
This application has not been rigorously tested and its domain rules are very simple which are hard to cover the complexity of real stock market. There may be also incorrect data introduced by some not found bugs or data sources .
### <span style='color:#a00000'>This application is not mature enough and risky to be your decision tool in real stock market !</span>


-------

### Screenshots : 

![](data/../assets/dashboard-s1.png)

![](data/../assets/dashboard-s2.png)

-------

### Develop tools and main packages  
1. Visual Studio Code
2. Python 3.8
3. pipenv
4. Web framework :  from Dash migrate to Django
5. Django Rest Framework
6. Stock chart :  from cufflinks.quant_figure change to HighCharts Stock
7. jQuery : through ajax update information and stock chart
8. pandas datareader : to get stock price history 
9. BeautifulSoup : parse web page
10. gunicorn web server
11. dj-static for static file process in gunicorn 
12. Web UI apply Bootstrap 4.x with responsive design
13. Fontawesome : icon
14. 2 Slider components :
    - ootstrap-slider :  https://github.com/seiyria/bootstrap-slider
    - Ion.RangeSlider : http://ionden.com/a/plugins/ion.rangeSlider/index.html
    


## Run and Deploy
1. No requirement for database 
2. Stock price and financial data are retrieved from other web site or service in real time, if data sources are blocked or data specs are changed that will cause service error
3. Stock information will be cached in memory for 12 hr after first accessed
4. Demo site is deploy to Google Cloud Run, it may need a few seconds to start application if it already auto shutdown after long idle. 
5. It may take a few seconds to refresh stock information if it's the first access of selected stock in last 12 hours

 
### Run in development mode
1. config/settings.py will read OS environment variable to set logger level, set 'LOGGER_LOG_LEVLE=DEBUG' will enable debug mode
1. python manage.py runserver


### Run in gunicorn
1. python manage.py collectstatic  // this will copy css js image ... files to staticfiles folder
2. gunicorn --bind 0.0.0.0:change_to_prefered_port config.wsgi:application
   
### Deploy to Google Cloud Run
1. Apply for Google Cloud Service account
2. Install Google Cloud SDK for python, follow instruction on official document
3. Install Google Cloud extend module for Visual Studio Code
4. Use Cloud Run to deploy application in Visual Studio Code


What's new or fixed issues:

2024-01-03
1. Refactor codes to follow pylint and mypy rules
2. Fixed issue: Error occured when retrieve stock data from yahoo

2024-01-15
1. Add Copilot usage guidelines and improve logging in investment_suggestion_view
2. Refactor dashboard.js to asynchronously update charts when stock is selected.

2024-01-16
1. Refactor code to prevent from invoking duplicated requests to access same stock data from outside website  