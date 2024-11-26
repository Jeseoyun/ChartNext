from django.urls import path
from .views import stock_data, stock_prediction, stock_current_price, stock_intraday_data, stock_indicators

urlpatterns = [
    path('stock/', stock_data, name='stock-data'),
    path('stock/<str:stock_code>/predict/', stock_prediction, name='stock-prediction'),
    path('stock/current/', stock_current_price, name='stock-current-price'),
    path('stock/intraday/', stock_intraday_data, name='stock-intraday-data'),
    path('stock/indicators/', stock_indicators, name='stock_indicators'),
] 