<template>
  <v-container>
    <h1>{{ company.name }} ({{ company.ticker }})</h1>
    <stock-chart :ticker="company.ticker"></stock-chart>
  </v-container>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import StockChart from '@/components/StockChart.vue';

export default {
  name: 'InterestDetailView',
  components: {
    StockChart,
  },
  setup() {
    const route = useRoute();
    const company = ref({
      name: route.params.name,
      ticker: route.params.ticker,
    });

    return {
      company,
    };
  },
};
</script>

<style scoped>
/* 필요한 스타일을 추가합니다 */
</style> 