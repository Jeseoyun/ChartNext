from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import Stock
from .serializers import StockSerializer
from users.models import UserStock
from rest_framework import status
from django.db.models import Q
from django.http import JsonResponse
import os
import joblib
from backend import settings
from sklearn.metrics.pairwise import cosine_similarity


# 경로 정의
vectorizer_path = os.path.join(settings.DATA_ROOT, 'vectorizer.pkl')
matrix_path = os.path.join(settings.DATA_ROOT, 'tfidf_matrix.pkl')
ids_path = os.path.join(settings.DATA_ROOT, 'ids.pkl')

# 벡터와 데이터 로드
vectorizer = joblib.load(vectorizer_path)
tfidf_matrix = joblib.load(matrix_path)
ids = joblib.load(ids_path)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_stock_info(request, code):
    try:
        stock = Stock.objects.get(code=code)
        serializer = StockSerializer(stock)
        return Response(serializer.data)
    except Stock.DoesNotExist:
        return Response({'error': 'Stock not found'}, status=404)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_all_stocks(request):
    stocks = Stock.objects.all()
    serializer = StockSerializer(stocks, many=True)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def user_stocks(request):
    if request.method == 'GET':
        try:
            user_stocks = UserStock.objects.filter(user=request.user)
            stocks = [user_stock.stock for user_stock in user_stocks]
            serializer = StockSerializer(stocks, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    elif request.method == 'POST':
        try:
            stock_code = request.data.get('stock_code')
            if not stock_code:
                return Response({'error': '주식 코드가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 주식 존재 여부 확인
            stock = Stock.objects.get(code=stock_code)
            
            # 이미 등록된 관심 주식인지 확인
            if UserStock.objects.filter(user=request.user, stock=stock).exists():
                return Response({'error': '이미 등록된 관심 주식입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # UserStock 생성
            user_stock = UserStock.objects.create(
                user=request.user,
                stock=stock
            )
            
            return Response({'message': '관심 주식이 등록되었습니다.'}, status=status.HTTP_201_CREATED)
            
        except Stock.DoesNotExist:
            return Response({'error': '존재하지 않는 주식입니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
def search_stocks(request):
    query = request.GET.get('query', '')
    # 문자열 매치 알고리즘
    stocks = Stock.objects.filter(Q(name__icontains=query) | Q(code__icontains=query))
    serializer = StockSerializer(stocks, many=True)
    return Response({'results': serializer.data})

@api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
def ml_search_stocks(request):
    query = request.GET.get('query', '')
    if not query:
        return JsonResponse({'results': []})

    # 1. 사용자 입력 벡터화
    query_vector = vectorizer.transform([query])

    # 2. 코사인 유사도 계산
    similarities = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # 3. 상위 유사도 5개 추출
    top_indices = similarities.argsort()[::-1][:5]
    results = []
    for index in top_indices:
        stock_id = ids[index]
        stock = Stock.objects.get(id=stock_id)
        results.append({
            'id': stock.id,
            'code': stock.code,
            'name': stock.name,
            'industry': stock.industry,
            'sector': stock.sector,
            'market': stock.market,
            'similarity': float(similarities[index]),
        })

    return JsonResponse({'results': results})