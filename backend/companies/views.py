from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import UserInterest, Company
from .serializers import UserInterestSerializer, CompanySerializer
import pandas_datareader.data as web
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np
from .utils import get_latest_news
import openai
from django.conf import settings
from .ml_models import train_models  

# Create your views here.

class UserInterestViewSet(viewsets.ModelViewSet):
    serializer_class = UserInterestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserInterest.objects.filter(user=self.request.user)

class CompanyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'ticker']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_data(request, ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 지난 1년간 데이터
    try:
        df = web.DataReader(ticker, 'yahoo', start_date, end_date)
        df.reset_index(inplace=True)
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        data = df[['Date', 'Close']].to_dict(orient='records')
        return Response({'ticker': ticker, 'data': data})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_prediction(request, ticker):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)  # 지난 1년간 데이터

    try:
        # 주가 데이터 불러오기
        df = web.DataReader(ticker, 'yahoo', start_date, end_date)
        df.reset_index(inplace=True)
        df['DateOrdinal'] = df['Date'].map(datetime.toordinal)

        # 입력 변수(X)와 목표 변수(y) 설정
        X = df[['DateOrdinal']]
        y = df['Close']

        # 머신러닝 모델 학습
        models = train_models(X, y)

        # 모델 성능 평가 및 최적 모델 선택
        best_model = None
        best_score = float('inf')

        for name, model in models.items():
            predictions = model.predict(X)
            mse = mean_squared_error(y, predictions)
            if mse < best_score:
                best_score = mse
                best_model = model

        # 미래 날짜 생성
        future_dates = [end_date + timedelta(days=i) for i in range(1, 31)]  # 향후 30일
        future_date_ordinals = np.array([date.toordinal() for date in future_dates]).reshape(-1, 1)

        # 최적 모델로 미래 주가 예측
        future_predictions = best_model.predict(future_date_ordinals)

        # 결과 정리
        future_data = [
            {'Date': date.strftime('%Y-%m-%d'), 'Predicted Close': pred}
            for date, pred in zip(future_dates, future_predictions)
        ]

        return Response({'ticker': ticker, 'future_data': future_data})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def recommended_news(request):
    user_interests = UserInterest.objects.filter(user=request.user)
    news_list = []
    for interest in user_interests:
        company_name = interest.company.name
        news = get_latest_news(company_name)
        news_list.extend(news)
    return Response(news_list)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def chatbot(request):
    question = request.data.get('question')
    if not question:
        return Response({'error': '질문을 입력해주세요.'}, status=400)
    
    # 기업명 추출 (예: 간단한 방법으로 처리)
    company_name = question.strip()
    
    # 해당 기업의 최신 뉴스 가져오기
    news = get_latest_news(company_name)
    if not news:
        return Response({'answer': '해당 기업에 대한 최신 뉴스를 찾을 수 없습니다.'})
    
    # 뉴스 내용을 하나의 문자열로 결합
    context = ' '.join([item['title'] for item in news])
    
    # OpenAI API 설정
    openai.api_key = settings.OPENAI_API_KEY
    
    # 프롬프트 생성
    prompt = f"사용자 질문: {question}\n\n관련 뉴스: {context}\n\n답변:"
    
    # GPT-4o-mini 모델을 사용하여 답변 생성
    response = openai.Completion.create(
        engine='gpt-4o-mini',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
        n=1,
        stop=None,
    )
    
    answer = response.choices[0].text.strip()
    return Response({'answer': answer})