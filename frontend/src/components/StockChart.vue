<script setup>
import { ref, onMounted, watch, defineExpose } from 'vue';
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
  await fetchChartData(option.value);
}

async function calculatePrediction() {
  try {
    const response = await apiClient.get('/companies/stock/indicators/', {
      params: {
        stock_code: props.ticker,
        period: selectedOption.value
      }
    });
    
    const indicators = response.data;
    const lastPrice = chartData.value.datasets[0].data[chartData.value.datasets[0].data.length - 1];
    
    // RSI, MACD, 볼린저 밴드를 기반으로 예측 계산
    const rsiSignal = indicators.rsi > 70 ? -1 : indicators.rsi < 30 ? 1 : 0;
    const macdSignal = indicators.macd > indicators.macd_signal ? 1 : -1;
    const bbSignal = (lastPrice - indicators.bb_lower) / (indicators.bb_upper - indicators.bb_lower);
    
    // 각 지표의 가중치를 적용한 예측값 계산
    const predictionFactor = (rsiSignal * 0.3 + macdSignal * 0.4 + bbSignal * 0.3);
    const volatility = indicators.atr; // ATR을 변동성 측정에 사용
    
    // 향후 10일간의 예측 데이터 생성
    const predictionDays = 10;
    const predictions = [lastPrice];  // 마지막 실제 가격을 예측 배열의 첫 번째 값으로 추가
    let currentPrice = lastPrice;
    
    for (let i = 0; i < predictionDays; i++) {
      currentPrice += (predictionFactor * volatility);
      predictions.push(currentPrice);
    }
    
    // 예측 데이터 추가
    const originalData = chartData.value.datasets[0].data;
    const predictionDates = generateFutureDates(chartData.value.labels[chartData.value.labels.length - 1], predictionDays);
    
    chartData.value = {
      labels: [...chartData.value.labels, ...predictionDates],
      datasets: [
        {
          ...chartData.value.datasets[0],
          data: originalData
        },
        {
          label: '예측',
          data: [...Array(originalData.length - 1).fill(null), ...predictions],  // 마지막 실제 데이터 포인트부터 시작
          borderColor: '#FF9800',
          borderDash: [5, 5],
          tension: 0.4
        }
      ]
    };
  } catch (error) {
    console.error('예측 계산 실패:', error);
  }
}

function generateFutureDates(lastDate, days) {
  const dates = [];
  let currentDate = new Date(lastDate);
  
  for (let i = 0; i < days; i++) {
    currentDate.setDate(currentDate.getDate() + 1);
    dates.push(currentDate.toISOString().split('T')[0]);
  }
  
  return dates;
}

async function togglePrediction() {
  showPrediction.value = !showPrediction.value;
  if (showPrediction.value) {
    await calculatePrediction();
  } else {
    await fetchChartData(selectedOption.value);
  }
}

defineExpose({
  togglePrediction
});
</script>

<template>
  <div>
    <div class="chart" style="height: 400px;">
      <Line 
        v-if="chartData"
        :data="chartData"
        :options="chartOptions"
      />
    </div>
    <div class="chart-controls">
      <div class="period-buttons">
        <button
          v-for="option in options"
          :key="option.value"
          :class="{ selected: option.value === selectedOption }"
          @click="selectOption(option)"
        >
          {{ option.label }}
        </button>
      </div>
      <v-btn
        icon
        variant="text"
        color="grey-lighten-1"
        size="small"
        @click="$emit('show-help')"
      >
        <v-icon>mdi-help-circle-outline</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<style scoped>
.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.period-buttons {
  display: flex;
  flex-wrap: wrap;
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
</style>