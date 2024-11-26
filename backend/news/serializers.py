from rest_framework import serializers
from .models import NewsArticle, NewsImage, NewsContent, Comment

class NewsContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsContent
        fields = ['refid', 'text']

class NewsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsImage
        fields = ['refid', 'src', 'caption']

class NewsArticleSerializer(serializers.ModelSerializer):
    contents = NewsContentSerializer(many=True)
    images = NewsImageSerializer(many=True)
    
    class Meta:
        model = NewsArticle
        fields = ['id', 'category', 'title', 'url', 'authors', 'time', 'contents', 'images']

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'username', 'text', 'created_at']
        read_only_fields = ['user']