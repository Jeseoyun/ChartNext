<script setup>
import { ref, onMounted, watch } from 'vue';
import { Line, Chart } from 'vue-chartjs';
import { 
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import apiClient from '@/api';
import 'chartjs-plugin-annotation';
import Swal from 'sweetalert2';

// Chart.js 등록
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const selectedOption = ref('6mo');
const options = [
  { value: '1d', label: '1일' },
  { value: '5d', label: '5일' },
  { value: '1mo', label: '1달' },
  { value: '3mo', label: '3달' },
  { value: '6mo', label: '6달' },
  { value: '1y', label: '1년' },
  { value: '2y', label: '2년' },
  { value: '5y', label: '5년' },
  { value: 'max', label: '최대' }
];
const chartData = ref(null);
const showPrediction = ref(false);
const predictionData = ref(null);
const sentimentData = ref(null);
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'category',
      ticks: {
        callback: function(value, index, values) {
          const date = new Date(this.getLabelForValue(index));
          if (date.getDate() === 1 || index === 0) {
            return `${date.getMonth() + 1}월`;
          }
          return '';
        },
        maxRotation: 0  // 레이블 회전 방지
      }
    },
    y: {
      beginAtZero: false
    }
  },
  plugins: {
    annotation: {
      annotations: {}
    },
    legend: {
      labels: {
        usePointStyle: true,
        pointStyle: 'line'
      }
    },
    tooltip: {
      callbacks: {
        title: function(context) {
          const date = new Date(context[0].label);
          return date.toISOString().split('T')[0];
        },
        label: function(context) {
          return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`;
        }
      }
    }
  }
});

// props 추가
const props = defineProps({
  ticker: {
    type: String,
    required: true
  }
});

watch(() => props.ticker, async (newTicker) => {
  if (newTicker) {
    showPrediction.value = false;  // 새로운 종목이 선택되면 예측 모드 해제
    await fetchChartData(selectedOption.value);
  }
}, { immediate: true });

async function fetchChartData(option) {
  try {
    // 1d, 5d는 intraday API 사용
    if (option === '1d' || option === '5d') {
      const response = await apiClient.get('/companies/stock/intraday/', {
        params: {
          stock_code: props.ticker,
          period: option
        }
      });
      
      // intraday 데이터 포맷팅
      chartData.value = {
        labels: response.data.data.map(item => item.datetime),
        datasets: [
          {
            label: '종가',
            data: response.data.data.map(item => item.close),
            borderColor: '#36A2EB',
            tension: 0.1
          }
        ]
      };
    } else {
      // 기존 일봉 데이터 API 사용
      const response = await apiClient.get('/companies/stock/', {
        params: {
          stock_code: props.ticker,
          period: option
        }
      });
      
      // 일봉 데이터 포맷팅
      chartData.value = {
        labels: response.data.map(item => item.Date),
        datasets: [
          {
            label: '종가',
            data: response.data.map(item => item.Close),
            borderColor: '#36A2EB',
            tension: 0.1
          }
        ]
      };
    }
  } catch (error) {
    console.error('데이터 불러오기 실패:', error);
  }
}

async function selectOption(option) {
  selectedOption.value = option.value;
  showPrediction.value = false;  // 새로운 기간이 선택되면 예측 모드 해제
  await fetchChartData(option.value);
}

async function calculatePrediction() {
  try {
    // 5일 이하 기간 체크
    if (selectedOption.value === '1d' || selectedOption.value === '5d') {
      await Swal.fire({
        title: '예측 불가',
        text: '5일 이하의 기간에서는 예측 기능을 사용할 수 없습니다.',
        icon: 'warning',
        confirmButtonText: '확인',
        background: 'rgba(32, 33, 36, 0.85)',
        color: '#fff',
        confirmButtonColor: '#9350FF',
        iconColor: '#FF9800',
        backdrop: 'rgba(0, 0, 0, 0.7)',
        customClass: {
          popup: 'custom-swal-popup',
          title: 'custom-swal-title',
          htmlContainer: 'custom-swal-html',
          confirmButton: 'custom-swal-confirm-button',
          icon: 'custom-swal-icon'
        }
      });
      showPrediction.value = false;
      return;
    }

    // 기술적 지표 데이터 가져오기
    const response = await apiClient.get('/companies/stock/indicators/', {
      params: {
        stock_code: props.ticker,
        period: selectedOption.value
      }
    });
    
    const indicators = response.data;
    const lastPrice = chartData.value.datasets[0].data[chartData.value.datasets[0].data.length - 1];
    
    // 기존 예측 계산
    const rsiSignal = indicators.rsi > 70 ? -1.5 : indicators.rsi < 30 ? 1.5 : 0;
    const macdSignal = indicators.macd > indicators.macd_signal ? 1.5 : -1.5;
    const bbSignal = (lastPrice - indicators.bb_lower) / (indicators.bb_upper - indicators.bb_lower);
    const predictionFactor = (rsiSignal * 0.4 + macdSignal * 0.4 + bbSignal * 0.2);
    const volatility = indicators.atr * 1.5;
    
    const predictionDays = 10;
    const predictions = [lastPrice];
    let currentPrice = lastPrice;

    // 기술적 분석 기반 예측 계산
    for (let i = 0; i < predictionDays; i++) {
      const trend = predictionFactor * volatility * 1.2;
      const oscillation = Math.sin(i * Math.PI / 3) * volatility * 0.5;
      const randomNoise = (Math.random() - 0.5) * volatility * 0.3;
      const bbPosition = (currentPrice - indicators.bb_middle) / (indicators.bb_upper - indicators.bb_middle);
      const meanReversion = (0.5 - bbPosition) * volatility * 0.3;
      const priceChange = trend + oscillation + meanReversion + randomNoise;
      
      currentPrice += priceChange;
      const maxPrice = indicators.bb_upper * 1.2;
      const minPrice = indicators.bb_lower * 0.8;
      currentPrice = Math.min(Math.max(currentPrice, minPrice), maxPrice);
      predictions.push(currentPrice);
    }

    // 미래 날짜 생성
    const predictionDates = generateFutureDates(chartData.value.labels[chartData.value.labels.length - 1], predictionDays);
    const originalData = chartData.value.datasets[0].data;

    // 감성 분석 결과 가져오기
    const sentimentResponse = await apiClient.get('/companies/news/sentiment/', {
      params: {
        stock_code: props.ticker
      }
    });
    
    // 차트 데이터 초기화
    let datasets = [
      {
        label: '종가',
        data: originalData,
        borderColor: '#36A2EB',
        tension: 0.1
      },
      {
        label: '기술적 예측',
        data: [...Array(originalData.length - 1).fill(null), ...predictions],
        borderColor: '#FF9999',
        borderDash: [5, 5],
        tension: 0.1
      }
    ];

    // 뉴스가 있는 경우에만 감성 예측선 추가
    if (sentimentResponse.data.analyzed_articles > 0) {
      const sentimentScore = sentimentResponse.data.sentiment_score;
      const sentimentPredictions = [lastPrice];
      let currentSentimentPrice = lastPrice;

      // 감성 점수 기반의 변동성 계산 (변동폭 축소)
      const sentimentWeight = (sentimentScore / 10) * 0.8;  // 감성 가중치 (-0.8 ~ 0.8)
      const baseVolatility = volatility * 0.6;  // 기본 변동성 축소
      
      // 감성 분석 ��� 측 계산
      for (let i = 0; i < predictionDays; i++) {
        // 1. 기본 감성 트렌드 (더 완만한 곡선)
        const sentimentCurve = Math.tanh(i / (predictionDays * 0.7)) * sentimentWeight;
        const baseTrend = sentimentCurve * baseVolatility;
        
        // 2. 주기적 변동 (작은 진폭)
        const shortCycle = Math.sin(i * Math.PI / 2.5) * baseVolatility * 0.2;
        const longCycle = Math.sin(i * Math.PI / 5) * baseVolatility * 0.15;
        const cyclicMovement = shortCycle + longCycle;
        
        // 3. 제한된 랜덤 변동
        const randomFactor = Math.abs(sentimentWeight) * 0.3;  // 랜덤성 감소
        const randomMovement = (Math.random() - 0.5) * baseVolatility * randomFactor;
        
        // 4. 가격 변화 계산
        const priceChange = (
          baseTrend +  // 기본 트렌드
          cyclicMovement +  // 주기적 변동
          randomMovement  // 랜덤 변동
        );
        
        // 5. 새로운 가격 계산
        currentSentimentPrice += priceChange;
        
        // 6. 범 좁은 범위로 제한
        const bandWidth = indicators.bb_upper - indicators.bb_lower;
        const maxPrice = indicators.bb_upper + (bandWidth * 0.15);  // 범위 축소
        const minPrice = indicators.bb_lower - (bandWidth * 0.15);  // 범위 축소
        currentSentimentPrice = Math.min(Math.max(currentSentimentPrice, minPrice), maxPrice);
        
        sentimentPredictions.push(currentSentimentPrice);
      }

      // 감성 예측선 추가 (부드러운 곡선)
      datasets.push({
        label: '뉴스 감성 예측',
        data: [...Array(originalData.length - 1).fill(null), ...sentimentPredictions],
        borderColor: '#99FF99',
        borderDash: [5, 5],
        tension: 0.35  // 더 부드러운 곡선
      });
    } else {
      console.log('뉴스 데이터가 없어 감성 예측선을 표시하지 않습니다.');
    }

    // 차트 데이터 업데이트
    chartData.value = {
      labels: [...chartData.value.labels, ...predictionDates],
      datasets: datasets
    };

    // 감성 점수에 따른 배경색 추가
    chartOptions.value.plugins.annotation.annotations = {
      box1: {
        type: 'box',
        xMin: chartData.value.labels[chartData.value.labels.length - predictionDays - 1],
        xMax: chartData.value.labels[chartData.value.labels.length - 1],
        yMin: 'min',
        yMax: 'max',
        backgroundColor: sentimentResponse.data.sentiment_score > 0 ? 'rgba(0, 255, 0, 0.1)' : 
                        sentimentResponse.data.sentiment_score < 0 ? 'rgba(255, 0, 0, 0.1)' : 
                        'rgba(128, 128, 128, 0.1)',
        borderWidth: 0
      }
    };
    
    showPrediction.value = true;

  } catch (error) {
    console.error('예측 계산 중 오류:', error);
    await Swal.fire({
      title: '오류',
      text: '예측을 계산하는 중 오류가 발생했습니다.',
      icon: 'error',
      confirmButtonText: '확인'
    });
  }
}

// 미래 날짜 생성 함수 추가
function generateFutureDates(lastDate, days) {
  const dates = [];
  let currentDate = new Date(lastDate);
  
  for (let i = 0; i < days; i++) {
    currentDate.setDate(currentDate.getDate() + 1);
    // 주말 건너뛰기
    while (currentDate.getDay() === 0 || currentDate.getDay() === 6) {
      currentDate.setDate(currentDate.getDate() + 1);
    }
    dates.push(currentDate.toISOString().split('T')[0]);
  }
  
  return dates;
}

async function togglePrediction() {
  if (!showPrediction.value) {
    if (selectedOption.value === '1d' || selectedOption.value === '5d') {
      await Swal.fire({
        title: '예측 불가',
        text: '5일 이하의 기간에서는 예측 기능을 사용할 수 없습니다.',
        icon: 'warning',
        confirmButtonText: '확인',
        background: 'rgba(32, 33, 36, 0.85)',
        color: '#fff',
        confirmButtonColor: '#9350FF',
        iconColor: '#FF9800',
        backdrop: 'rgba(0, 0, 0, 0.7)',
        customClass: {
          popup: 'custom-swal-popup',
          title: 'custom-swal-title',
          htmlContainer: 'custom-swal-html',
          confirmButton: 'custom-swal-confirm-button',
          icon: 'custom-swal-icon'
        }
      });
      return;
    }
  }
  
  showPrediction.value = !showPrediction.value;
  if (showPrediction.value) {
    await calculatePrediction();
  } else {
    await fetchChartData(selectedOption.value);
  }
}

// 예측 스무딩 함수
function smoothPredictions(predictions) {
  const windowSize = 3;
  return predictions.map((val, idx) => {
    if (idx < windowSize - 1) return val;
    const window = predictions.slice(Math.max(0, idx - windowSize + 1), idx + 1);
    return window.reduce((a, b) => a + b, 0) / window.length;
  });
}
</script>

<template>
  <div class="chart-container">
    <div class="chart-wrapper">
      <div class="chart" :class="{ 'with-prediction': showPrediction }">
        <Line 
          v-if="chartData"
          :data="chartData"
          :options="{
            ...chartOptions,
            maintainAspectRatio: false,
          }"
          style="width: calc(100% - 30px); height: 400px;"
        />
      </div>
      <div class="prediction-button-container">
        <v-btn
          class="prediction-button"
          :class="{ 'prediction-active': showPrediction }"
          variant="text"
          @click="togglePrediction"
        >
          <div v-if="!showPrediction" class="vertical-text">
            <span>C</span>
            <span>H</span>
            <span>A</span>
            <span>R</span>
            <span>T</span>
            <span class="mt-2">N</span>
            <span>E</span>
            <span>X</span>
            <span>T</span>
          </div>
          <v-icon v-else class="reset-icon">mdi-restore</v-icon>
        </v-btn>
      </div>
    </div>
    <div class="chart-controls">
      <div class="period-buttons">
        <div class="period-group">
          <button
            v-for="option in options"
            :key="option.value"
            :class="{ selected: option.value === selectedOption }"
            @click="selectOption(option)"
          >
            {{ option.label }}
          </button>
        </div>
        <div class="help-button">
          <v-btn
            icon
            variant="text"
            color="grey-lighten-1"
            @click="$emit('show-help')"
          >
            <v-icon>mdi-help-circle-outline</v-icon>
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
}

.chart-wrapper {
  position: relative;
  display: flex;
  height: 400px;
}

.chart {
  position: relative;
  width: calc(100% - 20px);
  height: 400px;
}

.prediction-button-container {
  position: absolute;
  top: 0;
  right: 0;
  width: 20px;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 3px 0;
}

.prediction-button {
  height: 100% !important;
  width: 20px !important;
  border: none !important;
  border-radius: 10px !important;
  background: rgba(147, 80, 255, 0.1) !important;
  backdrop-filter: blur(3px);
  transition: none !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  padding: 0 !important;
  margin: 0 !important;
  position: relative;
  overflow: hidden;
  box-shadow: none !important;
  outline: none !important;
}

/* 새로운 배경 애니메이션 */
.prediction-button::before,
.prediction-button::after {
  content: '';
  position: absolute;
  inset: -50%;
  background: radial-gradient(
    circle at center,
    rgba(147, 80, 255, 0.2),
    rgba(80, 150, 255, 0.2),
    transparent 70%
  );
  animation: moveGradient 6s ease-in-out infinite;
  z-index: 1;
}

.prediction-button::after {
  background: radial-gradient(
    circle at center,
    rgba(80, 150, 255, 0.2),
    rgba(147, 80, 255, 0.2),
    transparent 70%
  );
  animation: moveGradient 6s ease-in-out infinite reverse;
  filter: blur(3px);
}

@keyframes moveGradient {
  0% {
    transform: translateY(-30%) scale(2);
  }
  50% {
    transform: translateY(30%) scale(2.5);
  }
  100% {
    transform: translateY(-30%) scale(2);
  }
}

/* Vuetify 기본 스타일 제거 */
.prediction-button .v-btn__overlay {
  display: none !important;
}

/* 텍스트와 아이콘이 배경 위에 보이도록 z-index 조정 */
.vertical-text, .reset-icon {
  position: relative;
  z-index: 2;
}

/* 호버 효과 제거 */
.prediction-button:hover,
.prediction-button:focus,
.prediction-button:active {
  background: rgba(147, 80, 255, 0.1) !important;
}

.prediction-button.prediction-active {
  background: rgba(147, 80, 255, 0.2) !important;
}

.vertical-text {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.9);
  font-size: 10px;
  letter-spacing: 1px;
  font-weight: 500;
  transform: translateX(-12px);
  position: relative;
  z-index: 2;
}

.vertical-text span {
  opacity: 0;
  line-height: 1.2;
  text-align: center;
  animation: fadeInUp 0.5s forwards;
}

/* 각 글자별 애니메이션 딜레이 */
.vertical-text span:nth-child(1) { animation-delay: 0.1s; }
.vertical-text span:nth-child(2) { animation-delay: 0.2s; }
.vertical-text span:nth-child(3) { animation-delay: 0.3s; }
.vertical-text span:nth-child(4) { animation-delay: 0.4s; }
.vertical-text span:nth-child(5) { animation-delay: 0.5s; }
.vertical-text span:nth-child(6) { animation-delay: 0.7s; } /* N */
.vertical-text span:nth-child(7) { animation-delay: 0.8s; }
.vertical-text span:nth-child(8) { animation-delay: 0.9s; }
.vertical-text span:nth-child(9) { animation-delay: 1.0s; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mt-2 {
  margin-top: 8px;
}

.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.period-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.period-group {
  display: flex;
  flex-wrap: wrap;
}

.help-button {
  margin-left: auto;
}

button {
  margin: 3px;
  padding: 5px;
  border: none;
  background: transparent;
  color: gray;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'AppleSDGothicNeoB', sans-serif;
}

button:hover {
  background: linear-gradient(120deg, #b0b0b0, #d0d0d0);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

button.selected {
  background-color: #808080;
  color: white;
  border-radius: 15px;
}

.reset-icon {
  color: rgba(255, 255, 255, 0.9);
  font-size: 24px !important;
  transform: translateX(-12px);
  position: relative;
  z-index: 2;
  animation: rotateIn 0.5s ease-out;
}

@keyframes rotateIn {
  from {
    transform: translateX(-12px) rotate(-180deg);
    opacity: 0;
  }
  to {
    transform: translateX(-12px) rotate(0);
    opacity: 1;
  }
}

/* Swal 팝업 스타일 */
:deep(.swal2-popup) {
  background: rgba(32, 33, 36, 0.85) !important;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3) !important;
  backdrop-filter: blur(10px) !important;
}

:deep(.swal2-title) {
  color: #fff !important;
  font-size: 1.5rem !important;
  padding-bottom: 10px !important;
}

:deep(.swal2-html-container) {
  color: rgba(255, 255, 255, 0.8) !important;
  padding-top: 10px !important;
}

:deep(.swal2-confirm) {
  background-color: #9350FF !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  text-transform: none !important;
  letter-spacing: 0.5px !important;
  box-shadow: 0 0 10px rgba(147, 80, 255, 0.3) !important;
}

:deep(.swal2-icon.swal2-warning) {
  color: #FF9800 !important;
}
</style>