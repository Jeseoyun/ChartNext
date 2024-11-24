<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useUserStore } from '@/stores/user';
import apiClient from '@/api';
import StockChart from '@/components/StockChart.vue';
import SearchBar from '@/components/SearchBar.vue';
import NavigationBar from '@/components/NavigationBar.vue';

const router = useRouter();
const userStore = useUserStore();

const selectedStock = ref(null);
const userStocks = ref([]);

// 검색 결과 클릭 핸들러
const handleSearchResultClick = (stock) => {
  selectedStock.value = stock;
};

// 관심 종목 선택 핸들러
const selectStock = (stock) => {
  selectedStock.value = stock;
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
        <navigation-bar />
        
        <!-- 검색 영역 -->
        <v-container class="search-container">
          <search-bar
            @result-selected="handleSearchResultClick"
          />
        </v-container>

        <!-- 메인 콘텐츠 영역 -->
        <v-container class="content-container">
          <v-row>
            <v-col cols="12" md="9">
              <v-card class="chart-card">
                <v-card-title v-if="selectedStock">
                  {{ selectedStock.name }} ({{ selectedStock.code }})
                </v-card-title>
                <v-card-text>
                  <stock-chart
                    v-if="selectedStock"
                    :ticker="selectedStock.code"
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
                    </v-list-item>
                  </v-list>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </div>
    </div>
  </v-container>
</template>

<style scoped>
.main {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: black;
  z-index: 1;
}

.background-video {
  position: absolute;
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
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.content-container {
  margin-top: 20px;
  overflow-y: auto;
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
  }

  .search-container {
    padding: 0 20px;
  }

  .search-results {
    width: calc(100% - 40px);
  }
}
</style>
