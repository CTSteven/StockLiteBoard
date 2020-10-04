from django.urls import path
from django.views.i18n import JavaScriptCatalog
from .views import HomePageView, AboutPageView, \
     dashboardView, stockPriceHistoryView, investmentSuggestionView, \
     financialReportView


urlpatterns = [
    #path('',homePageView, name='home') # function view
    path('home/',HomePageView.as_view(), name='home'), # Class view
    path('about/',AboutPageView.as_view(), name='about'),
    path('dashboard/',dashboardView, name='dashboard'),
    path('pages/stockPriceHistory',stockPriceHistoryView, name='stockPriceHistory'),
    path('',dashboardView, name='default'),
    path('pages/investmentSuggestion',investmentSuggestionView, name='investmentSuggestion'),
    path('pages/financialReport',financialReportView, name='financialReport'),
    path('jsi18n/',
         JavaScriptCatalog.as_view(),
         name='javascript-catalog'),
]

