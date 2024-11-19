from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserInterestViewSet, CompanyViewSet, stock_data, stock_prediction, recommended_news, chatbot

router = DefaultRouter()
router.register(r'interests', UserInterestViewSet, basename='userinterest')
router.register(r'companies', CompanyViewSet, basename='company')

urlpatterns = [
    path('', include(router.urls)),
    path('stock/<str:ticker>/', stock_data, name='stock-data'),
    path('stock/<str:ticker>/predict/', stock_prediction, name='stock-prediction'), 
    path('news/recommend/', recommended_news, name='recommended-news'),
    path('chatbot/', chatbot, name='chatbot'),
] 