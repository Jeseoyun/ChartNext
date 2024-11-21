from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from .models import Stock
from .serializers import StockSerializer
from users.models import UserStock
from rest_framework import status

# Create your views here.

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

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_user_stock(request):
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
