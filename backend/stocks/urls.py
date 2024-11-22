from django.urls import path
from .views import get_stock_info, get_all_stocks, search_stocks, ml_search_stocks, user_stocks

urlpatterns = [
    path('stock/<str:code>/', get_stock_info, name='get-stock-info'),
    path('stocks/', get_all_stocks, name='get-all-stocks'),
    path('stocks/search/', search_stocks, name='search-stocks'),
    path('stocks/ml-search/', ml_search_stocks, name='ml-search-stocks'),
    path('user-stocks/', user_stocks, name='user-stocks'),
] 