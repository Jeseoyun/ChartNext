from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.get_news_by_category, name='news-by-category'),
    path('news/<int:id>/', views.get_news_detail, name='news-detail'),
    path('news/<int:article_id>/chatbot/', views.article_chatbot, name='article-chatbot'),
    path('news/<int:article_id>/comments/', views.get_comments, name='get-comments'),
    path('news/<int:article_id>/comments/create/', views.create_comment, name='create-comment'),
] 