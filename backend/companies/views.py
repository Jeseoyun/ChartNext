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
import FinanceDataReader as fdr
from django.http import JsonResponse
import yfinance as yf

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_data(request):
    stock_code = request.GET.get('stock_code', '')
    period = request.GET.get('period', '6mo')

    if not stock_code:
        return Response({'error': 'stock_code is required'}, status=400)

    try:
        # 기간을 날짜로 변환
        end_date = datetime.now()
        if period == '1d':
            start_date = end_date - timedelta(days=1)
        elif period == '5d':
            start_date = end_date - timedelta(days=5)
        elif period == '1mo':
            start_date = end_date - timedelta(days=30)
        elif period == '3mo':
            start_date = end_date - timedelta(days=90)
        elif period == '6mo':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        elif period == '2y':
            start_date = end_date - timedelta(days=730)
        elif period == '5y':
            start_date = end_date - timedelta(days=1825)
        else:  # max
            start_date = datetime(1990, 1, 1)

        # 주식 코드가 숫자로만 이루어져 있는지 확인 (한국 주식)
        is_korean = stock_code.isdigit()
        
        if is_korean:
            df = fdr.DataReader(stock_code, start_date, end_date)
        else:
            # yfinance를 사용하여 해외 주식 데이터 가져오기
            ticker = yf.Ticker(stock_code)
            df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return Response({'error': 'No data found for the given stock code'}, status=404)
            
        # 인덱스를 데이터 컬럼으로 변환
        df = df.reset_index()
        
        # 날짜 형식 변환
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        
        # 필요한 컬럼만 선택하고 컬럼명 통일
        if is_korean:
            result = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict('records')
        else:
            # yfinance의 컬럼명 통일
            result = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict('records')
        
        return Response(result)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_prediction(request, stock_code):
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