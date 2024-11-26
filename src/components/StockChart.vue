<template>
  <div class="chart-container">
    <div class="stock-info-container">
      <div class="stock-info">
        {{ stockName }} ({{ stockCode }}) {{ currentPrice }}
        <span :class="['price-change', priceChange >= 0 ? 'positive' : 'negative']">
          {{ priceChange }}%
        </span>
      </div>
      <button 
        class="prediction-btn"
        @click="togglePrediction"
      >
        예상 차트 보기
      </button>
    </div>
    <div class="chart">
      <!-- 기존 차트 코드 -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { calculateBollingerBands, calculateRSI, calculateMACD } from '../utils/indicators';

const showPrediction = ref(false);

// 예측 데이터 계산 함수
const calculatePrediction = (historicalData) => {
  const bb = calculateBollingerBands(historicalData, 20, 2);
  const rsi = calculateRSI(historicalData, 14);
  const macd = calculateMACD(historicalData);
  
  // 마지막 데이터 포인트
  const lastPoint = historicalData[historicalData.length - 1];
  
  // 예측 로직
  let prediction = [];
  const days = 30; // 30일 예측
  
  for(let i = 1; i <= days; i++) {
    let predictedPrice = lastPoint.price;
    
    // RSI를 통한 과매수/과매도 체크
    if (rsi < 30) {
      predictedPrice *= 1.01; // 상승 예상
    } else if (rsi > 70) {
      predictedPrice *= 0.99; // 하락 예상
    }
    
    // MACD 신호 체크
    if (macd.macdLine > macd.signalLine) {
      predictedPrice *= 1.005; // 상승 트렌드
    } else {
      predictedPrice *= 0.995; // 하락 트렌드
    }
    
    // 볼린저 밴드 범위 내 조정
    const upperBand = bb.upper[bb.upper.length - 1];
    const lowerBand = bb.lower[bb.lower.length - 1];
    predictedPrice = Math.min(Math.max(predictedPrice, lowerBand), upperBand);
    
    prediction.push({
      date: new Date(lastPoint.date.getTime() + i * 24 * 60 * 60 * 1000),
      price: predictedPrice
    });
  }
  
  return prediction;
};

const togglePrediction = () => {
  showPrediction.value = !showPrediction.value;
  if (showPrediction.value) {
    const prediction = calculatePrediction(historicalData.value);
    // 차트에 예측선 추가
    updateChartWithPrediction(prediction);
  } else {
    // 예측선 제거
    removeChartPrediction();
  }
};

// 주식 정보를 위한 props 추가
const props = defineProps({
  stockName: String,
  stockCode: String,
  currentPrice: Number,
  priceChange: Number
});
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.stock-info-container {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 10px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.stock-info {
  font-size: 1.1rem;
  font-weight: 500;
  margin-right: 15px;
}

.price-change {
  font-weight: bold;
}

.price-change.positive {
  color: #d60000;
}

.price-change.negative {
  color: #0051c7;
}

.prediction-btn {
  padding: 6px 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.prediction-btn:hover {
  background-color: #45a049;
  transform: translateY(-1px);
  transition: all 0.2s ease;
}

.chart {
  margin-top: 10px;
}
</style> 