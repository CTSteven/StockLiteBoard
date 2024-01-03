"""
This module contains the URL patterns for the pages app.
"""
from django.urls import path
from django.views.i18n import JavaScriptCatalog
from .views import HomePageView, AboutPageView, \
     dashboard_view, stock_price_history_view, investment_suggestion_view, \
     financial_report_view

urlpatterns = [
    #path('',homePageView, name='home') # function view
    path('home/',HomePageView.as_view(), name='home'), # Class view
    path('about/',AboutPageView.as_view(), name='about'),
    path('dashboard/',dashboard_view, name='dashboard'),
    path('pages/stockPriceHistory',stock_price_history_view, name='stockPriceHistory'),
    path('',dashboard_view, name='default'),
    path('pages/investmentSuggestion',investment_suggestion_view, name='investmentSuggestion'),
    path('pages/financialReport',financial_report_view, name='financialReport'),
    path('jsi18n/',
         JavaScriptCatalog.as_view(),
         name='javascript-catalog'),
]

