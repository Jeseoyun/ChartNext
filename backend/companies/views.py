from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import UserInterest, Company, StockPrice
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
from pykrx import stock
import pandas as pd
import requests
import jwt
import hashlib
import time
import os
import pandas_ta as ta

# 전역 변수로 토큰 정보 저장
_access_token = None
_token_expires_at = None
_last_token_request = None
_token_refresh_interval = 6 * 3600  # 6시간 (초 단위)

def get_access_token():
    """한국투자증권 API 접근 토큰 발급 (캐싱 및 재사용)"""
    global _access_token, _token_expires_at, _last_token_request
    
    current_time = time.time()
    
    # 1. 유효한 토큰이 있는 경우
    if _access_token and _token_expires_at and current_time < _token_expires_at:
        return _access_token
        
    # 2. 마지막 요청으로부터 6시간이 지나지 않은 경우
    if _last_token_request and (current_time - _last_token_request) < _token_refresh_interval:
        if _access_token:  # 기존 토큰이 있다면 재사용
            return _access_token
    
    # 3. 새로운 토큰 발급이 필요한 경우
    try:
        url = "https://openapi.koreainvestment.com:9443/oauth2/tokenP"
        data = {
            "grant_type": "client_credentials",
            "appkey": os.getenv('KIS_APP_KEY'),
            "appsecret": os.getenv('KIS_APP_SECRET'),
        }
        headers = {
            "content-type": "application/json; charset=utf-8"
        }
        
        response = requests.post(url, json=data, headers=headers, verify=False)
        
        if response.status_code == 200:
            response_data = response.json()
            _access_token = response_data.get("access_token")
            expires_in = response_data.get("expires_in", 86400)  # 기본값 24시간
            _token_expires_at = current_time + expires_in - 60  # 1분 여유
            _last_token_request = current_time
            return _access_token
            
        print(f"토큰 발급 실패 - Status: {response.status_code}")
        print(f"Response: {response.text}")
        return None
        
    except Exception as e:
        print(f"토큰 발급 중 오류 발생: {str(e)}")
        return None

def get_hash_key(data, key):
    """한국투자증권 API 해시키 생성"""
    path = data["tr_id"] + data["custtype"] + data["zipcd"] + timestamp
    hash_key = hashlib.sha256(path.encode()).hexdigest()
    return hash_key

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

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_current_price(request):
    stock_code = request.GET.get('stock_code', '')
    
    if not stock_code:
        return Response({'error': '종목 코드가 필요합니다.'}, status=400)
        
    try:
        is_korean = stock_code.isdigit()
        
        if is_korean:
            # 한국 주식 데이터 가져오기
            df = fdr.DataReader(stock_code)
            if df.empty:
                return Response({'error': '해당 종목의 데이터를 찾을 수 없습니다.'}, status=404)
            
            today_data = df.iloc[-1]
            yesterday_data = df.iloc[-2]
        else:
            # 해외 주식 데이터 가져오기
            ticker = yf.Ticker(stock_code)
            
            # 오늘 데이터
            today_df = ticker.history(period='1d')
            if today_df.empty:
                return Response({'error': '해당 종목의 데이터를 찾을 수 없습니다.'}, status=404)
            
            # 어제 데이터 (5일 데이터를 가져와서 마지막에서 두 번째 데이터 사용)
            past_df = ticker.history(period='5d')
            
            today_data = today_df.iloc[-1]
            yesterday_data = past_df.iloc[-2]
        
        price_change = today_data['Close'] - yesterday_data['Close']
        change_ratio = (price_change / yesterday_data['Close']) * 100
        
        result = {
            'current_price': float(today_data['Close']),
            'price_change': float(price_change),
            'change_ratio': float(change_ratio),
            'volume': int(today_data['Volume']),
            'high': float(today_data['High']),
            'low': float(today_data['Low']),
            'open': float(today_data['Open']),
            'date': today_df.index[-1].strftime('%Y-%m-%d') if not is_korean else df.index[-1].strftime('%Y-%m-%d'),
            'currency': 'KRW' if is_korean else 'USD'
        }
        
        return Response(result)
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def stock_intraday_data(request):
    stock_code = request.GET.get('stock_code', '')
    period = request.GET.get('period', '1d')
    
    if not stock_code:
        return Response({'error': '종목 코드가 필요합니다.'}, status=400)
    
    if period not in ['1d', '5d']:
        return Response({'error': '유효하지 않은 기간입니다. 1d 또는 5d만 가능합니다.'}, status=400)
    
    try:
        is_korean = stock_code.isdigit()
        
        if is_korean:
            # 한국 주식의 경우 코드에 .KS 추가
            ticker = yf.Ticker(f"{stock_code}.KS")
        else:
            ticker = yf.Ticker(stock_code)
            
        if period == '1d':
            df = ticker.history(period='1d', interval='1m')
        else:  # 5d
            df = ticker.history(period='5d', interval='5m')
        
        if df.empty:
            return Response({'error': '데이터를 찾을 수 없습니다.'}, status=404)
        
        df = df.reset_index()
        df = df.rename(columns={
            'Datetime': 'datetime',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        df['datetime'] = pd.to_datetime(df['datetime']).dt.strftime('%Y-%m-%d %H:%M:%S')
        result = df[['datetime', 'open', 'high', 'low', 'close', 'volume']].to_dict('records')
        
        return Response({
            'stock_code': stock_code,
            'period': period,
            'currency': 'KRW' if is_korean else 'USD',
            'data': result
        })
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def stock_indicators(request):
    stock_code = request.GET.get('stock_code')
    period = request.GET.get('period', '6mo')
    
    try:
        # 기간에 따른 날짜 범위 계산
        end_date = datetime.now()
        if period == '1mo':
            start_date = end_date - timedelta(days=30)
        elif period == '3mo':
            start_date = end_date - timedelta(days=90)
        elif period == '6mo':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=180)  # 기본값

        # yfinance를 사용하여 데이터 가져오기
        is_korean = stock_code.isdigit()
        if is_korean:
            ticker = yf.Ticker(f"{stock_code}.KS")
        else:
            ticker = yf.Ticker(stock_code)
            
        df = ticker.history(start=start_date, end=end_date)
        
        if len(df) < 20:
            return Response({
                'error': '충분한 데이터가 없습니다.'
            }, status=400)

        # RSI 계산 (14일)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD 계산
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # 볼린저 밴드 계산
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['STD20'] = df['Close'].rolling(window=20).std()
        df['Upper_Band'] = df['MA20'] + (df['STD20'] * 2)
        df['Lower_Band'] = df['MA20'] - (df['STD20'] * 2)

        # ATR 계산
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        df['ATR'] = true_range.rolling(14).mean()

        # 결측치 처리
        df = df.fillna(method='ffill').fillna(method='bfill')

        # 마지막 데이터 포인트의 지표값 추출
        latest = df.iloc[-1]
        
        return Response({
            'rsi': float(latest['RSI']),
            'macd': float(latest['MACD']),
            'macd_signal': float(latest['Signal_Line']),
            'bb_upper': float(latest['Upper_Band']),
            'bb_middle': float(latest['MA20']),
            'bb_lower': float(latest['Lower_Band']),
            'atr': float(latest['ATR']),
            'last_price': float(latest['Close']),
            'last_date': latest.name.strftime('%Y-%m-%d')
        })
        
    except Exception as e:
        print(f"Error in stock_indicators: {str(e)}")  # 디버깅을 위한 로그 추가
        return Response({
            'error': str(e)
        }, status=500)