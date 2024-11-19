<template>
  <div>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { Chart } from 'chart.js';
import apiClient from '@/api';

export default {
  name: 'StockChart',
  props: {
    ticker: {
      type: String,
      required: true,
    },
  },
  setup(props) {
    const chartCanvas = ref(null);
    let chartInstance = null;

    const fetchStockData = async () => {
      try {
        const response = await apiClient.get(`companies/stock/${props.ticker}/`);
        const data = response.data.data;

        const labels = data.map(item => item.Date);
        const prices = data.map(item => item.Close);

        const predictionResponse = await apiClient.get(`companies/stock/${props.ticker}/predict/`);
        const futureData = predictionResponse.data.future_data;

        const futureLabels = futureData.map(item => item.Date);
        const futurePrices = futureData.map(item => item['Predicted Close']);

        const allLabels = [...labels, ...futureLabels];
        const actualPrices = [...prices, ...Array(futurePrices.length).fill(null)];
        const predictedPrices = [...Array(prices.length - 1).fill(null), prices[prices.length - 1], ...futurePrices];

        if (chartInstance) {
          chartInstance.destroy();
        }

        chartInstance = new Chart(chartCanvas.value, {
          type: 'line',
          data: {
            labels: allLabels,
            datasets: [
              {
                label: '실제 주가',
                data: actualPrices,
                borderColor: 'rgba(75, 192, 192, 1)',
                fill: false,
              },
              {
                label: '예측 주가',
                data: predictedPrices,
                borderColor: 'rgba(255, 99, 132, 1)',
                borderDash: [5, 5],
                fill: false,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              x: {
                display: true,
              },
              y: {
                display: true,
              },
            },
          },
        });
      } catch (error) {
        console.error(error);
      }
    };

    onMounted(() => {
      fetchStockData();
    });

    watch(() => props.ticker, () => {
      fetchStockData();
    });

    return { chartCanvas };
  },
};
</script>

<style scoped>
/* 필요한 스타일을 추가합니다 */
</style> 