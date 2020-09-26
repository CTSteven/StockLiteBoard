from django.urls import path
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
]

