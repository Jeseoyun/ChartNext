from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import NewsArticle, NewsContent, NewsImage, Comment
from .serializers import NewsArticleSerializer, CommentSerializer
from django.db.models import Prefetch, Q
import logging
import openai
from django.conf import settings

# Create your views here.

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_news_by_category(request):
    category = request.GET.get('category', None)
    search_query = request.GET.get('search', None)
    limit = int(request.GET.get('limit', 8))
    offset = int(request.GET.get('offset', 0))
    
    queryset = NewsArticle.objects.prefetch_related(
        Prefetch('contents', queryset=NewsContent.objects.order_by('refid')),
        Prefetch('images', queryset=NewsImage.objects.order_by('refid'))
    )
    
    if category and category != 'all':
        queryset = queryset.filter(category=category)
        
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(contents__text__icontains=search_query)
        ).distinct()
    
    articles = queryset.order_by('-time')[offset:offset + limit]
    serializer = NewsArticleSerializer(articles, many=True)
    
    return Response(serializer.data)

@api_view(['GET'])
def get_news_detail(request, id):
    try:
        article = get_object_or_404(NewsArticle.objects.prefetch_related(
            Prefetch('contents', queryset=NewsContent.objects.order_by('refid')),
            Prefetch('images', queryset=NewsImage.objects.order_by('refid'))
        ), id=id)
        
        print(f"Found article: {article.title}")
        print(f"Contents count: {article.contents.count()}")
        print(f"Images count: {article.images.count()}")
        
        serializer = NewsArticleSerializer(article)
        return Response(serializer.data)
    except Exception as e:
        print(f"Error in get_news_detail: {str(e)}")
        raise

@api_view(['POST'])
def chatbot_response(request):
    question = request.data.get('question')
    context = request.data.get('context')
    
    if not question or not context:
        return Response({'error': '질문과 컨텍스트가 필요합니다.'}, status=400)
    
    try:
        # GPT-4 API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about news articles."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        return Response({'answer': answer})
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_comments(request, article_id):
    comments = Comment.objects.filter(article_id=article_id)
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_comment(request, article_id):
    article = get_object_or_404(NewsArticle, id=article_id)
    
    serializer = CommentSerializer(data={
        'article': article.id,
        'user': request.user.id,
        'text': request.data.get('text')
    })
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)
