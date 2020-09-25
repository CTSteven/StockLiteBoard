from django.urls import path
from .views import HomePageView, AboutPageView, dashboardView, stockPriceHistoryView

urlpatterns = [
    #path('',homePageView, name='home') # function view
    path('home/',HomePageView.as_view(), name='home'), # Class view
    path('about/',AboutPageView.as_view(), name='about'),
    path('dashboard/',dashboardView, name='dashboard'),
    path('pages/stockPriceHistory',stockPriceHistoryView, name='stockPriceHistory'),
    path('',stockPriceHistoryView, name='stockPriceHistory')
]

