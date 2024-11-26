<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import apiClient from '@/api';
import NavBarComponent from '@/components/NavBarComponent.vue';
import LogoComponent from '@/components/LogoComponent.vue';

const router = useRouter();
const userStocks = ref([]);
const stockPrices = ref({});
const trendingNews = ref([]);

// 로딩 상태 변수 추가
const isLoadingStocks = ref(true);
const isLoadingNews = ref(true);

// 사용자의 관심 종목 로드
const loadUserStocks = async () => {
  isLoadingStocks.value = true;
  try {
    const response = await apiClient.get('/stocks/user-stocks/');
    userStocks.value = response.data;
    await loadStockPrices();
  } catch (error) {
    console.error('관심 종목 로드 실패:', error);
  } finally {
    isLoadingStocks.value = false;
  }
};

// 주식 현재가 데이터 로드
const loadStockPrices = async () => {
  try {
    const promises = userStocks.value.map(stock => 
      apiClient.get('/companies/stock/current/', {
        params: { stock_code: stock.code }
      })
    );
    
    const responses = await Promise.all(promises);
    responses.forEach((response, index) => {
      stockPrices.value[userStocks.value[index].code] = response.data;
    });
  } catch (error) {
    console.error('주가 데이터 로드 실패:', error);
  }
};

const goToStockDetail = (stock) => {
  if (stock) {
    router.push({
      name: 'StockDetail',
      params: { stockCode: stock.code }
    });
  }
};

// 상승/하락 종목 필터링 및 정렬
const risingStocks = computed(() => 
  userStocks.value
    .filter(stock => stockPrices.value[stock.code]?.change_ratio > 0)
    .sort((a, b) => 
      (stockPrices.value[b.code]?.change_ratio || 0) - 
      (stockPrices.value[a.code]?.change_ratio || 0)
    )
);

const fallingStocks = computed(() => 
  userStocks.value
    .filter(stock => stockPrices.value[stock.code]?.change_ratio <= 0)
    .sort((a, b) => 
      (stockPrices.value[a.code]?.change_ratio || 0) - 
      (stockPrices.value[b.code]?.change_ratio || 0)
    )
);

const editInterests = () => router.push({ name: 'Interests' });

// 뉴스 데이터 로드 함수
const loadTrendingNews = async () => {
  isLoadingNews.value = true;
  try {
    const response = await apiClient.get('/news/trending/');
    trendingNews.value = response.data;
  } catch (error) {
    console.error('뉴스 데이터 로드 실패:', error);
  } finally {
    isLoadingNews.value = false;
  }
};

// 기사 상세 페이지로 이동하는 함수
const goToNewsDetail = (articleId) => {
  router.push({
    name: 'NewsDetail',
    params: { id: articleId }
  });
};

onMounted(() => {
  loadUserStocks();
  loadTrendingNews();
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
        </div>
        
        <div class="dashboard">
        <!--
          <v-card class="dashboard-card">
            <v-card-title>오늘의 이슈</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item v-for="i in 3" :key="i">
                  <v-list-item-title>주요 이슈 {{ i }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card class="dashboard-card">
            <v-card-title>내 관심기업 뉴스 동향</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item v-for="i in 3" :key="i">
                  <v-list-item-title>뉴스 동향 {{ i }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
          -->
          <v-card class="dashboard-card stock-card">
            <v-card-title class="d-flex align-center justify-space-between">
              <span>내 관심기업 주가</span>
              <v-btn
                class="edit-interests-btn"
                @click="editInterests"
                prepend-icon="mdi-pencil"
                variant="outlined"
                color="white"
                size="default"
              >
                관심 기업 수정
              </v-btn>
            </v-card-title>
            <v-card-text>
              <div v-if="isLoadingStocks" class="loading-container">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  size="32"
                ></v-progress-circular>
                <span class="loading-text">데이터를 불러오는 중...</span>
              </div>
              <div v-else class="stock-section">
                <div class="stock-category" v-if="risingStocks.length > 0">
                  <h3 class="stock-category-title rising">
                    상승장
                  </h3>
                  <div class="stock-list-container">
                    <v-list>
                      <v-list-item
                        v-for="stock in risingStocks"
                        :key="stock.code"
                        @click="goToStockDetail(stock)"
                        link
                      >
                        <template v-slot:prepend>
                          <v-icon color="red">mdi-trending-up</v-icon>
                        </template>
                        <v-list-item-title>{{ stock.name }}</v-list-item-title>
                        <v-list-item-subtitle>
                          {{ stockPrices[stock.code]?.current_price.toLocaleString() }}
                          {{ stockPrices[stock.code]?.currency }}
                          <span class="rising-text">
                            +{{ stockPrices[stock.code]?.change_ratio.toFixed(2) }}%
                          </span>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </div>
                </div>

                <div class="stock-category" v-if="fallingStocks.length > 0">
                  <h3 class="stock-category-title falling">
                    하락장
                  </h3>
                  <div class="stock-list-container">
                    <v-list>
                      <v-list-item
                        v-for="stock in fallingStocks"
                        :key="stock.code"
                        @click="goToStockDetail(stock)"
                        link
                      >
                        <template v-slot:prepend>
                          <v-icon color="blue">mdi-trending-down</v-icon>
                        </template>
                        <v-list-item-title>{{ stock.name }}</v-list-item-title>
                        <v-list-item-subtitle>
                          {{ stockPrices[stock.code]?.current_price.toLocaleString() }}
                          {{ stockPrices[stock.code]?.currency }}
                          <span class="falling-text">
                            {{ stockPrices[stock.code]?.change_ratio.toFixed(2) }}%
                          </span>
                        </v-list-item-subtitle>
                      </v-list-item>
                    </v-list>
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <v-card class="dashboard-card">
            <v-card-title>내 관심기업 관련 뉴스</v-card-title>
            <v-card-text>
              <div v-if="isLoadingNews" class="loading-container">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  size="32"
                ></v-progress-circular>
                <span class="loading-text">뉴스를 불러오는 중...</span>
              </div>
              <v-list v-else-if="trendingNews.length > 0">
                <div v-for="news in trendingNews" :key="news.company" class="trending-news-item">
                  <div class="company-header">
                    <h3 class="company-name">{{ news.company }}</h3>
                    <v-chip
                      size="small"
                      color="primary"
                      variant="outlined"
                      class="mention-count"
                    >
                      {{ news.mention_count }}건의 관련 기사
                    </v-chip>
                  </div>
                  
                  <div class="news-summary">
                    <p class="headline">
                      {{ 
                        news.summary?.split('\n')?.[0]?.replace('1. 헤드라인: ', '') || 
                        news.summary || 
                        '제목 정보가 없습니다'
                      }}
                    </p>
                    <p class="detail">
                      {{ 
                        news.summary?.split('\n\n')?.[1]?.replace('2. 상세 요약: ', '') || 
                        (news.summary?.split('\n')?.[1] || '').replace('2. 상세 요약: ', '') || 
                        '상세 내용이 없습니다'
                      }}
                    </p>
                  </div>

                  <div class="article-links">
                    <v-btn
                      v-for="articleId in news.article_ids"
                      :key="articleId"
                      variant="text"
                      density="compact"
                      color="primary"
                      @click="goToNewsDetail(articleId)"
                    >
                      기사 {{ news.article_ids.indexOf(articleId) + 1 }} 보기
                    </v-btn>
                  </div>
                </div>
              </v-list>
              <div v-else class="no-news">
                <v-icon size="40" color="grey">mdi-newspaper-variant-outline</v-icon>
                <p>관련 뉴스가 없습니다</p>
              </div>
            </v-card-text>
          </v-card>
        </div>
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

.dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px;
  overflow-y: auto;
  margin-top: 80px;
}

.dashboard-card {
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

/* 반응형 디자인 */
@media (max-width: 960px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
}

.stock-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stock-category {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  padding: 12px 8px 12px 12px;
  margin-bottom: 16px;
  height: 300px;
  display: flex;
  flex-direction: column;
}

.stock-list-container {
  flex: 1;
  overflow-y: auto;
  margin-right: 2px;
}

.stock-list-container :deep(::-webkit-scrollbar) {
  width: 8px;
}

.stock-list-container :deep(::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.stock-list-container :deep(::-webkit-scrollbar-thumb) {
  background: rgba(147, 80, 255, 0.5);
  border-radius: 4px;
}

.stock-list-container :deep(::-webkit-scrollbar-thumb:hover) {
  background: rgba(147, 80, 255, 0.7);
}

.stock-category-title {
  font-size: 1rem;
  margin-bottom: 8px;
  padding-left: 12px;
  flex-shrink: 0;
}

:deep(.v-list) {
  height: 100%;
  padding: 0;
}

.rising-text {
  color: #ff5252;
  font-weight: 500;
}

.falling-text {
  color: #2196f3;
  font-weight: 500;
}

.rising {
  color: #ff5252;
  border-left: 3px solid #ff5252;
}

.falling {
  color: #2196f3;
  border-left: 3px solid #2196f3;
}

:deep(.v-list-item) {
  border-radius: 8px;
  margin-bottom: 4px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.1) !important;
  }
}

.stock-card {
  max-height: none !important;
}

:deep(.v-list) {
  max-height: none !important;
  overflow-y: visible;
}

.edit-interests-btn {
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  font-size: 1rem !important;
  padding: 0 20px !important;
  height: 40px !important;
}

.edit-interests-btn:hover {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: #9350ff !important;
}

.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 1920px;
  height: 80px;
  background-color: transparent;
  z-index: 1000;
}

.trending-news-item {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.trending-news-item:last-child {
  border-bottom: none;
}

.company-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.company-name {
  font-size: 1.1rem;
  color: #9350ff;
  margin: 0;
}

.mention-count {
  font-size: 0.8rem;
}

.news-summary {
  margin: 12px 0;
}

.news-summary .headline {
  font-weight: 500;
  margin-bottom: 8px;
  color: white;
}

.news-summary .detail {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.5;
}

.article-links {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}

.no-news {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
}

.no-news p {
  margin-top: 12px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  height: 300px;
  gap: 16px;
}

.loading-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  font-family: 'AppleSDGothicNeoB', sans-serif;
}
</style>
