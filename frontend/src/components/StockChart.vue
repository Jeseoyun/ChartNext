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
const options = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max'];
const chartData = ref(null);
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: false
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
    const response = await apiClient.get('/companies/stock/', {
      params: {
        stock_code: props.ticker,
        period: option
      }
    });
    
    // 데이터 포맷팅
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
  } catch (error) {
    console.error('데이터 불러오기 실패:', error);
  }
}

async function selectOption(option) {
  selectedOption.value = option;
  await fetchChartData(option);
}
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
    <div>
      <button
        v-for="option in options"
        :key="option"
        :class="{ selected: option === selectedOption }"
        @click="selectOption(option)"
      >
        {{ option }}
      </button>
    </div>
  </div>
</template>

<style scoped>
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