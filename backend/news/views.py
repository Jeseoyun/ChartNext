from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import NewsArticle, NewsContent, NewsImage, Comment
from .serializers import NewsArticleSerializer, CommentSerializer
from django.db.models import Prefetch, Q
import logging
from django.conf import settings
from openai import OpenAI

# Create your views here.

logger = logging.getLogger(__name__)

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@api_view(['GET'])
def get_news_by_category(request):
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    limit = int(request.GET.get('limit', 8))
    offset = int(request.GET.get('offset', 0))
    
    queryset = NewsArticle.objects.prefetch_related(
        Prefetch('contents', queryset=NewsContent.objects.order_by('refid')),
        Prefetch('images', queryset=NewsImage.objects.order_by('refid'))
    )
    
    # 카테고리 매핑
    category_mapping = {
        'business': '기업',
        'politics': '정치',
        'economy': '경제',
        'stock': '증권',
        'society': '사회',
        'international': '국제',
        'culture': '문화',
        'it-science': 'IT·과학'
    }
    
    if category and category != 'all':
        mapped_category = category_mapping.get(category)
        if mapped_category:
            queryset = queryset.filter(category=mapped_category)
    
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
        response = client.chat.completions.create(
            model="gpt-4",
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

@api_view(['POST'])
def article_chatbot(request, article_id):
    try:
        # 현재 기사 가져오기
        article = get_object_or_404(NewsArticle.objects.prefetch_related('contents'), id=article_id)
        
        # 사용자 질문 가져오기
        question = request.data.get('question')
        if not question:
            return Response({'error': '질문이 필요합니다.'}, status=400)

        # 기사 컨텍스트 구성
        context = f"제목: {article.title}\n\n"
        context += "내용:\n"
        for content in article.contents.all():
            context += f"{content.text}\n"

        try:
            # GPT-4 API 호출
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """당신은 기사 내용에 대해 답변하는 AI 어시스턴트입니다.
                    다음 규칙을 반드시 따라주세요:
                    1. 기사의 내용만을 바탕으로 답변해주세요.
                    2. 답변은 한국어로 작성해주세요.
                    3. 각 문장은 줄바꿈 이후 새로운 줄에 작성해주세요.
                    4. 핵심 키워드는 **강조**해서 표시해주세요.
                    5. 목록이 필요한 경우 마크다운 리스트를 사용해주세요.
                    6. 답변은 짧고, 간단명료하게 작성해주세요."""},
                    {"role": "user", "content": f"기사 내용: {context}\n\n질문: {question}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            return Response({'answer': answer})
            
        except Exception as e:
            logger.error(f"OpenAI API 오류: {str(e)}")
            return Response(
                {'error': 'AI 응답 생성 중 오류가 발생했습니다.', 'detail': str(e)}, 
                status=500
            )
            
    except Exception as e:
        logger.error(f"챗봇 처리 중 오류 발생: {str(e)}")
        return Response(
            {'error': '서버 오류가 발생했습니다.', 'detail': str(e)}, 
            status=500
        )
