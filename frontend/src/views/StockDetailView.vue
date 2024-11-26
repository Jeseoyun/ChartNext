<script setup>
import NavBarComponent from '@/components/NavBarComponent.vue';
import LogoComponent from '@/components/LogoComponent.vue';
import { ref, onMounted, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import apiClient from '@/api';
import StockChart from '@/components/StockChart.vue';
import SearchBar from '@/components/SearchBar.vue';

const router = useRouter();
const userStore = useUserStore();

const selectedStock = ref(null);
const userStocks = ref([]);
const selectedStockPrice = ref(null);
const stockChartRef = ref(null);

// 예측 설명 다이얼로그 상태
const showPredictionHelp = ref(false);

// 검색 결과 클릭 핸들러
const handleSearchResultClick = (stock) => {
  selectedStock.value = stock;
};

// 관심 종목 선택 핸들러
const selectStock = (stock) => {
  selectedStock.value = stock;
};

// 관심 기업 추가/삭제 핸들러
const toggleInterest = async (stock) => {
  try {
    if (isInterested(stock)) {
      // 관심 기업 삭제
      await apiClient.delete(`/stocks/user-stocks/${stock.code}/`);
    } else {
      // 관심 기업 추가
      await apiClient.post('/stocks/user-stocks/', {
        stock_code: stock.code
      });
    }
    await loadUserStocks(); // 목록 새로고침
  } catch (error) {
    console.error('관심 기업 처리 실패:', error);
  }
};

// 관심 기업 여부 확인
const isInterested = (stock) => {
  return userStocks.value.some(s => s.code === stock.code);
};

// 사용자의 관심 종목 로드
const loadUserStocks = async () => {
  try {
    const response = await apiClient.get('/stocks/user-stocks/');
    userStocks.value = response.data;
  } catch (error) {
    console.error('관심 종목 로드 실패:', error);
  }
};

// 주식 현재가 데이터 로드
const loadStockPrice = async (stock) => {
  if (!stock) return;
  
  try {
    const response = await apiClient.get('/companies/stock/current/', {
      params: { stock_code: stock.code }
    });
    selectedStockPrice.value = response.data;
  } catch (error) {
    console.error('주식 현재가 로드 실패:', error);
  }
};

// selectedStock이 변경될 때마다 현재가 데이터 로드
watch(selectedStock, (newStock) => {
  loadStockPrice(newStock);
});

onMounted(() => {
  loadUserStocks();
});
</script>

<template>
  <v-container fluid class="pa-0">
    <div class="main">
      <video autoplay loop muted playsinline class="background-video">
        <source src="@/assets/main_background.mp4" type="video/mp4" />
      </video>
      <div class="content">
        <div class="fixed-header">
          <LogoComponent />
          <NavBarComponent />
          <div class="search-container">
            <search-bar
              @result-selected="handleSearchResultClick"
            />
          </div>
        </div>
        
        <!-- 메인 콘텐츠 영역 -->
        <v-container class="content-container">
          <v-row>
            <v-col cols="12" md="9">
              <v-card class="chart-card">
                <v-card-title v-if="selectedStock" class="d-flex align-center justify-space-between">
                  <div>
                    <span>{{ selectedStock.name }} ({{ selectedStock.code }})</span>
                    <template v-if="selectedStockPrice">
                      <span class="ml-4 text-h6">
                        {{ selectedStockPrice.current_price.toLocaleString() }}
                      </span>
                      <span 
                        :class="[
                          'ml-2',
                          selectedStockPrice.change_ratio > 0 ? 'text-red' : 'text-blue'
                        ]"
                      >
                        {{ selectedStockPrice.change_ratio.toFixed(2) }}%
                      </span>
                    </template>
                  </div>
                  <div>
                    <!-- 예아요 버튼만 남김 -->
                    <v-btn
                      icon
                      variant="text"
                      color="grey-lighten-1"
                      @click="toggleInterest(selectedStock)"
                    >
                      <v-icon>{{ isInterested(selectedStock) ? 'mdi-heart' : 'mdi-heart-outline' }}</v-icon>
                    </v-btn>
                  </div>
                </v-card-title>
                <v-card-text>
                  <stock-chart
                    v-if="selectedStock"
                    ref="stockChartRef"
                    :ticker="selectedStock.code"
                    @show-help="showPredictionHelp = true"
                  ></stock-chart>
                  <div v-else class="text-center pa-4">
                    종목을 검색하여 차트를 확인하세요
                  </div>
                </v-card-text>
              </v-card>
            </v-col>

            <v-col cols="12" md="3">
              <v-card class="interest-list-card">
                <v-card-title>내 관심 기업</v-card-title>
                <v-card-text class="interest-list-container">
                  <v-list class="interest-list">
                    <v-list-item
                      v-for="stock in userStocks"
                      :key="stock.code"
                      :title="`${stock.name} (${stock.code})`"
                      :subtitle="stock.industry"
                      @click="selectStock(stock)"
                      hover
                    >
                      <template v-slot:append>
                        <v-btn
                          icon="mdi-heart"
                          size="small"
                          color="white"
                          variant="text"
                          @click.stop="toggleInterest(stock)"
                        ></v-btn>
                      </template>
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </div>

    <!-- 예측 설명 다이얼로그 -->
    <v-dialog v-model="showPredictionHelp" max-width="500">
      <v-card class="prediction-help-dialog">
        <v-card-title class="text-h6">
          기술적 지표 설명
          <v-btn
            icon
            variant="text"
            @click="showPredictionHelp = false"
            class="float-right"
          >
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-card-title>
        <v-card-text>
          <p class="mb-4">차트에서 사용되는 주요 기술적 지표들에 대한 설명입니다:</p>
          
          <h3 class="mb-2 text-subtitle-1">기술적 지표</h3>
          <ul class="mb-4">
            <li><strong>RSI (상대강도지수)</strong>: 14일 기준으로 계산되며, 상승폭과 하락폭의 비율을 통해 과매수/과매도 상태를 판단합니다.</li>
            <li><strong>MACD (이동평균수렴확산)</strong>: 12일 EMA와 26일 EMA의 차이를 계산하고, 9일 EMA를 시그널 라인으로 사용하여 추세를 분석합니다.</li>
            <li><strong>볼린저 밴드</strong>: 20일 이동평균을 중심으로 ±2 표준편차 범위를 보여주어 가격 변동성을 표시합니다.</li>
            <li><strong>ATR (평균진폭)</strong>: 14일 동안의 고가, 저가, 종가를 기반으로 가격 변동성을 측정합니다.</li>
          </ul>

          <p class="text-caption">
            * 각 지표는 서로 다른 기간의 데이터를 사용하여 계산되며, 종합적인 분석에 활용됩니다.<br>
            * 투자 결정시에는 기본적 분석과 함께 고려하시기 바랍니다.
          </p>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.main {
  position: relative;
  width: 100vw;
  min-height: 100vh;
  background-color: black;
  z-index: 1;
  overflow-y: auto;
}

.background-video {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 2;
  opacity: 0.2;
}

.content {
  position: relative;
  z-index: 3;
  width: 100%;
  min-height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.content-container {
  margin-top: 180px;
}

.chart-card, .interest-list-card {
  background-color: rgba(0, 0, 0, 0.5) !important;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

:deep(.v-card-title) {
  color: white;
  font-size: 1.2rem;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.v-card-text) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.v-list) {
  background-color: transparent !important;
}

:deep(.v-list-item) {
  color: white !important;
}

:deep(.v-list-item-title) {
  color: white !important;
}

:deep(.v-list-item-subtitle) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.interest-list-container {
  max-height: 400px;  /* 또는 원하는 높이 */
  overflow-y: auto;
  padding: 0;
}

.interest-list {
  padding: 0;
}

/* 스크롤바 스타일링 */
.interest-list-container::-webkit-scrollbar {
  width: 8px;
}

.interest-list-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.interest-list-container::-webkit-scrollbar-thumb {
  background: rgba(147, 80, 255, 0.5);
  border-radius: 4px;
}

.interest-list-container::-webkit-scrollbar-thumb:hover {
  background: rgba(147, 80, 255, 0.7);
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .content-container {
    padding: 0;
    margin-top: 160px;
  }

  .search-container {
    padding: 0 20px;
    margin-top: 10px;
  }

  .search-results {
    width: calc(100% - 40px);
  }
}

.text-red {
  color: #ff5252 !important;
}

.text-blue {
  color: #2196f3 !important;
}

.ml-2 {
  margin-left: 8px;
}

.ml-4 {
  margin-left: 16px;
}

.text-h6 {
  font-size: 1.25rem;
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  background-color: transparent;
  z-index: 1000;
  padding: 20px;
}

.search-container {
  max-width: 1160px;
  margin: 0 auto;
  margin-top: 100px;
}

.prediction-help-dialog {
  background-color: rgba(0, 0, 0, 0.8) !important;
  color: white !important;
}

.prediction-help-dialog :deep(.v-card-title) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.prediction-help-dialog ul {
  list-style-type: none;
  padding-left: 0;
}

.prediction-help-dialog li {
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
}

.prediction-help-dialog li::before {
  content: "•";
  position: absolute;
  left: 0;
  color: #FF9800;
}

.text-caption {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.75rem;
  line-height: 1.25;
}

.float-right {
  position: absolute;
  right: 8px;
  top: 8px;
}
</style>
