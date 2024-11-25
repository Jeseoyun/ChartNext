from django.urls import path
from .views import stock_data, stock_prediction

urlpatterns = [
    path('stock/', stock_data, name='stock-data'),
    path('stock/<str:stock_code>/predict/', stock_prediction, name='stock-prediction'), 
] 