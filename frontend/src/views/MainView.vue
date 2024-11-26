<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import apiClient from '@/api';
import NavBarComponent from '@/components/NavBarComponent.vue';
import LogoComponent from '@/components/LogoComponent.vue';
import { marked } from 'marked';

const router = useRouter();
const userStocks = ref([]);
const stockPrices = ref({});
const trendingNews = ref([]);
const hotTopics = ref([]);

// 로딩 상태 변수 추가
const isLoadingStocks = ref(true);
const isLoadingNews = ref(true);
const isLoadingTopics = ref(true);

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
  router.push(`/news/${articleId}`);
};

// 핫 토픽 로드 함수
const loadHotTopics = async () => {
  isLoadingTopics.value = true;
  try {
    const response = await apiClient.get('/news/hot-topics/');
    hotTopics.value = response.data;
  } catch (error) {
    console.error('핫 토픽 로드 실패:', error);
  } finally {
    isLoadingTopics.value = false;
  }
};

const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

// 마크다운 포맷팅 함수 추가
const formatMarkdown = (text) => {
  if (!text) return '';
  return marked(text);
};

onMounted(() => {
  loadUserStocks();
  loadTrendingNews();
  loadHotTopics();
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
          <v-card class="dashboard-card hot-topics-card">
            <v-card-title>오늘의 핫 토픽</v-card-title>
            <v-card-text>
              <div v-if="isLoadingTopics" class="loading-container">
                <v-progress-circular
                  indeterminate
                  color="primary"
                  size="32"
                ></v-progress-circular>
                <span class="loading-text">핫 토픽을 분석하는 중...</span>
              </div>
              <div v-else-if="hotTopics.length > 0" class="hot-topics">
                <div v-for="(topic, index) in hotTopics" :key="index" class="topic-item">
                  <div class="topic-header">
                    <v-chip
                      size="small"
                      color="primary"
                      variant="outlined"
                      class="topic-category"
                    >
                      {{ topic.category }}
                    </v-chip>
                  </div>
                  <h3 class="topic-title">{{ topic.title }}</h3>
                  <div class="topic-summary" v-html="formatMarkdown(topic.summary)"></div>
                </div>
              </div>
              <div v-else class="no-topics">
                <v-icon size="40" color="grey">mdi-newspaper-variant-outline</v-icon>
                <p>오늘의 핫 토픽이 없습니다</p>
              </div>
            </v-card-text>
          </v-card>

          <v-card class="dashboard-card stock-card">
            <v-card-title>
              내 관심기업 주가
              <v-spacer></v-spacer>
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
              <v-list v-else-if="trendingNews.length > 0" class="news-list">
                <div v-for="news in trendingNews" :key="news.company" class="trending-news-item">
                  <div class="company-section">
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
                    
                    <div class="news-content-wrapper">
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

                      <div class="related-articles">
                        <v-carousel
                          v-if="news.articles.length > 0"
                          :show-arrows="news.articles.length > 1"
                          height="320"
                          hide-delimiter-background
                          delimiter-icon="mdi-circle"
                          class="news-carousel"
                          touch
                          continuous
                          draggable
                        >
                          <template v-slot:prev="{ props }">
                            <v-btn
                              variant="flat"
                              class="carousel-nav-btn prev-btn"
                              v-bind="props"
                            >
                              <v-icon>mdi-chevron-left</v-icon>
                            </v-btn>
                          </template>
                          
                          <template v-slot:next="{ props }">
                            <v-btn
                              variant="flat"
                              class="carousel-nav-btn next-btn"
                              v-bind="props"
                            >
                              <v-icon>mdi-chevron-right</v-icon>
                            </v-btn>
                          </template>

                          <v-carousel-item
                            v-for="article in news.articles"
                            :key="article.id"
                          >
                            <v-card
                              class="article-card mx-2"
                              @click="goToNewsDetail(article.id)"
                              elevation="0"
                            >
                              <div class="article-text">
                                <v-card-text class="article-title">
                                  {{ article.title }}
                                </v-card-text>
                                <v-card-subtitle class="article-time">
                                  {{ formatDate(article.time) }}
                                </v-card-subtitle>
                              </div>
                              <div class="article-image-container">
                                <v-img
                                  v-if="article.image_url"
                                  :src="article.image_url"
                                  height="220"
                                  cover
                                  class="article-image"
                                >
                                  <template v-slot:placeholder>
                                    <v-img
                                      src="@/assets/news_placeholder.jpg"
                                      height="220"
                                      cover
                                    ></v-img>
                                  </template>
                                </v-img>
                              </div>
                            </v-card>
                          </v-carousel-item>
                        </v-carousel>
                      </div>
                    </div>
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
/* 공통 스타일 */
:deep(.v-card-title) {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  color: white;
  font-size: 1.2rem;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-weight: 700;
  display: flex;
  align-items: center;
  height: 72px;
}

.dashboard-card .v-card-title span,
.dashboard-card .v-card-title {
  font-weight: 700;
}

/* 불필요한 중복 CSS 제거 및 통합 */

/* 나머지 스타일은 기존과 동일하게 유지 */

.main {
  position: relative;
  width: 100vw;
  min-height: 100vh;
  overflow-y: auto;
  background-color: black;
  z-index: 1;
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
  min-height: 100vh;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px;
  margin-top: 60px;
  background: linear-gradient(to bottom, transparent 0%, rgba(0, 0, 0, 0.2) 20px);
}

.dashboard-card {
  background-color: rgba(0, 0, 0, 0.5) !important;
  border-radius: 8px;
  backdrop-filter: blur(10px);
  overflow: visible !important;
}

:deep(.v-card-text) {
  color: rgba(255, 255, 255, 0.8);
  overflow: visible !important;
}

:deep(.v-list) {
  background-color: transparent !important;
  height: auto !important;
  overflow: visible !important;
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

/* 응형 디자인 */
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
  padding-right: 4px;
}

.stock-list-container::-webkit-scrollbar {
  width: 8px;
}

.stock-list-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.stock-list-container::-webkit-scrollbar-thumb {
  background: rgba(147, 80, 255, 0.5);
  border-radius: 4px;
}

.stock-list-container::-webkit-scrollbar-thumb:hover {
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

.edit-interests-btn {
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
  text-transform: none !important;
  letter-spacing: 0 !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  font-size: 1rem !important;
  padding: 0 20px !important;
  height: 40px !important;
  margin-left: auto !important;
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
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.3) 0%, rgba(0, 0, 0, 0.2) 100%);
  backdrop-filter: blur(8px);
  z-index: 1000;
}


.trending-news-item {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  height: 360px;
}

.trending-news-item:last-child {
  border-bottom: none;
}

.company-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  height: 32px;
}

.company-name {
  font-size: 1.1rem;
  color: #9350ff;
  margin: 0;
}

.mention-count {
  font-size: 0.8rem;
}

.news-content-wrapper {
  display: flex;
  gap: 24px;
  height: 320px;
  margin-top: 0;
}

.news-summary {
  flex: 0 0 300px;
  padding: 16px;
  background: rgba(147, 80, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(147, 80, 255, 0.2);
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-top: 40px;
}

.news-summary .headline {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #9350ff;
  line-height: 1.4;
}

.news-summary .detail {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  white-space: pre-line;
  flex-grow: 1;
  overflow-y: auto;
  padding-right: 8px;
}

.news-summary .detail::-webkit-scrollbar {
  width: 4px;
}

.news-summary .detail::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.news-summary .detail::-webkit-scrollbar-thumb {
  background: rgba(147, 80, 255, 0.3);
  border-radius: 2px;
}

.news-summary .detail::-webkit-scrollbar-thumb:hover {
  background: rgba(147, 80, 255, 0.5);
}

.related-articles {
  flex: 1;
  min-width: 0;
  height: 100%;
}

.article-card {
  height: 320px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
  user-select: none;
  -webkit-user-drag: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.article-text {
  flex: 1;
  padding: 16px;
  min-height: 140px;
  display: flex;
  flex-direction: column;
}

.article-title {
  font-size: 0.9rem;
  line-height: 1.4;
  max-height: 4.2em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  color: white;
  padding: 0;
  margin-bottom: 8px;
}

.article-time {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.6);
  padding: 0;
  margin-top: auto;
}

.article-image-container {
  width: 100%;
  height: 160px;
  overflow: hidden;
  position: relative;
}

.article-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.2);
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.news-carousel {
  height: 320px !important;
}

/* 캐러셀 내부 여백 제거 */
.news-carousel :deep(.v-window__container) {
  height: 100%;
}

.news-carousel :deep(.v-window-item) {
  padding: 0;
}

/* 반응형 디자인 수정 */
@media (max-width: 960px) {
  .news-content-wrapper {
    flex-direction: column;
    gap: 20px;
  }

  .news-summary, 
  .related-articles,
  .article-card,
  .news-carousel {
    height: 260px !important;
  }

  .article-text {
    min-height: 100px;
  }

  .article-image-container {
    height: 120px;
  }
}

@media (max-width: 600px) {
  .news-summary, 
  .related-articles,
  .article-card,
  .news-carousel {
    height: 240px !important;
  }

  .article-title {
    font-size: 0.9rem;
  }

  .article-text {
    padding: 12px;
    min-height: 90px;
  }

  .article-image-container {
    height: 110px;
  }
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
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.hot-topics {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.topic-item {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  height: 100%;
}

.topic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.topic-category {
  font-size: 0.8rem;
}

.topic-title {
  font-size: 1.4rem;
  color: white;
  margin-bottom: 16px;
  font-weight: 600;
}

.topic-summary {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
  white-space: pre-line;
}

/* 마크다운 스일 */
.topic-summary :deep(p) {
  margin-bottom: 1em;
}

.topic-summary :deep(strong) {
  color: #9350ff;
  font-weight: 600;
  font-size: 1.15rem;
}

.topic-summary :deep(ul), 
.topic-summary :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 0.8em;
}

.topic-summary :deep(li) {
  margin-bottom: 0.8em;
  font-size: 1.1rem;
}

.topic-summary :deep(em) {
  font-style: italic;
  color: rgba(255, 255, 255, 0.9);
}

.topic-summary :deep(code) {
  background: rgba(147, 80, 255, 0.1);
  padding: 0.2em 0.4em;
  border-radius: 4px;
  font-family: monospace;
}

.no-topics {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.5);
  text-align: center;
}

.no-topics p {
  margin-top: 12px;
}

.hot-topics-card {
  grid-column: span 2;
}

.related-articles {
  margin-top: 16px;
}

.news-carousel {
  background: transparent;
  position: relative;
}

.carousel-nav-btn {
  position: absolute;
  bottom: 40px;
  z-index: 10;
  background: rgba(147, 80, 255, 0.3) !important;
  border: 2px solid rgba(147, 80, 255, 0.5) !important;
  height: 36px !important;
  width: 36px !important;
  border-radius: 50% !important;
  padding: 0 !important;
  transition: all 0.3s ease;
  backdrop-filter: blur(4px);
  box-shadow: 0 2px 8px rgba(147, 80, 255, 0.2);
  pointer-events: auto !important;
}

.carousel-nav-btn:hover {
  background: rgba(147, 80, 255, 0.5) !important;
  border-color: rgba(147, 80, 255, 0.8) !important;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(147, 80, 255, 0.4);
}

.prev-btn {
  left: 12px;
}

.next-btn {
  right: 12px;
}

.carousel-nav-btn .v-icon {
  color: rgba(255, 255, 255, 1);
  font-size: 24px;
}

.news-carousel :deep(.v-carousel__controls) {
  background: none;
  margin-bottom: 8px;
}

.news-carousel :deep(.v-carousel__controls__item) {
  margin: 0 2px;
}

.news-carousel :deep(.v-carousel__controls__item .v-btn--icon) {
  color: rgba(255, 255, 255, 0.5);
  transform: scale(0.7);
}

.news-carousel :deep(.v-carousel__controls__item .v-btn--active) {
  color: rgba(147, 80, 255, 0.9) !important;
  transform: scale(0.8);
}

.article-card {
  height: 360px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  margin: 0 auto;
  max-width: 95%;
  display: flex;
  flex-direction: column;
  user-select: none;
  -webkit-user-drag: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.article-content {
  flex: 1;
  padding: 20px;
}

.article-text {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.article-title {
  font-size: 1.2rem;
  line-height: 1.5;
  max-height: 4.5em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  color: white;
  padding: 0;
  margin-bottom: 12px;
}

.article-time {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  padding: 0;
  margin-top: auto;
}

.article-image-container {
  width: 100%;
  height: 220px;
  overflow: hidden;
}

.article-image {
  width: 100%;
  height: 100%;
  transition: transform 0.3s ease;
}

.news-carousel {
  height: 400px !important;
}

/* 응형 디자인 수정 */
@media (max-width: 960px) {
  .news-content-wrapper {
    flex-direction: column;
    gap: 20px;
  }

  .news-summary {
    width: 100%;
  }

  .article-card {
    height: 340px;
  }

  .article-image-container {
    height: 200px;
  }
}

@media (max-width: 600px) {
  .article-card {
    height: 320px;
  }

  .article-title {
    font-size: 1.1rem;
  }

  .article-image-container {
    height: 180px;
  }
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 0;
  margin: 0;
}

.trending-news-item {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  padding: 0 20px 20px 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.company-section {
  display: flex;
  flex-direction: column;
}

.company-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
  height: 32px;
  padding-top: 20px;
}

.company-name {
  font-size: 1.1rem;
  color: #9350ff;
  margin: 0;
}

.mention-count {
  font-size: 0.8rem;
}

.news-content-wrapper {
  display: flex;
  gap: 24px;
  height: 280px;
}

.news-summary {
  flex: 0 0 300px;
  padding: 16px;
  background: rgba(147, 80, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(147, 80, 255, 0.2);
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-top: 16px;
}

.news-summary .headline {
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #9350ff;
  line-height: 1.4;
}

.news-summary .detail {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.85);
  line-height: 1.5;
  white-space: pre-line;
  flex-grow: 1;
}

.related-articles {
  flex: 1;
  min-width: 0;
  height: 100%;
}

.article-card {
  height: 280px;
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  margin: 0;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.news-carousel {
  height: 280px !important;
}

:deep(.v-card-text) {
  padding-top: 0 !important;
}

.news-carousel :deep(.v-window__container) {
  cursor: grab;
}

.news-carousel :deep(.v-window__container:active) {
  cursor: grabbing;
}

.article-card {
  pointer-events: none;
  user-select: none;
  -webkit-user-drag: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.news-carousel {
  cursor: grab;
}

.news-carousel:active {
  cursor: grabbing;
}

/* 캐러셀 테이너에 대한 스타일 */
.news-carousel :deep(.v-window__container) {
  pointer-events: auto;
  cursor: grab;
}

.news-carousel :deep(.v-window__container:active) {
  cursor: grabbing;
}

/* 캐러셀 이템에 대한 스타일 */
.news-carousel :deep(.v-window-item) {
  pointer-events: none;
}

/* 클릭 이벤트를 위한 예외 처리 */
.article-card {
  pointer-events: auto !important;
}

.news-carousel :deep(.v-window__container) {
  pointer-events: auto;
}

.news-carousel :deep(.v-window-item) {
  pointer-events: auto;
}

.article-card {
  pointer-events: auto !important;
}

.article-image {
  pointer-events: none;
}

/* 주식 관련 텍스트 스타일 */
.stock-name {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 1rem;
}

.stock-price {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.1rem;
}

.stock-change {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 0.9rem;
}

/* 섹션 제목 스타일 */
.section-title {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.4rem;
  margin-bottom: 16px;
}

/* 기사 카드 스타일 */
.article-title {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 1.1rem;
  line-height: 1.4;
}

.article-time {
  font-family: 'AppleSDGothicNeoL', sans-serif;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.6);
}

/* 핫토픽 스타일 */
.topic-title {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.4rem;
  color: white;
  margin-bottom: 16px;
  font-weight: 600;
}

.topic-summary {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.8;
  white-space: pre-line;
}

.topic-category {
  font-family: 'AppleSDGothicNeoL', sans-serif;
  font-size: 0.9rem;
}

/* 트렌딩 뉴스 스타일 */
.company-name {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.1rem;
  color: #9350ff;
}

.mention-count {
  font-family: 'AppleSDGothicNeoL', sans-serif;
  font-size: 0.8rem;
}

.news-summary .headline {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #9350ff;
}

.news-summary .detail {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 버튼 스타일 */
.edit-interests-btn {
  font-family: 'AppleSDGothicNeoB', sans-serif !important;
}

/* 상승/하락 텍스트 */
.rising-text, .falling-text {
  font-family: 'AppleSDGothicNeoM', sans-serif;
}

/* 카드 제목 트 스일 */
:deep(.v-card-title) {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  color: white;
  font-size: 1.2rem;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

/* 섹션 제목 스타일 */
.section-title, 
.dashboard-card .v-card-title {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
}

/* 핫토픽 제목 */
.topic-title {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.4rem;
  color: white;
  margin-bottom: 16px;
  font-weight: 600;
}

/* 기업명 */
.company-name {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.1rem;
  color: #9350ff;
}

/* 주가 보 */
:deep(.v-list-item-title) {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  color: white;
}

/* 뉴스 헤드라인 */
.news-summary .headline {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: #9350ff;
}

/* 로딩 텍스트 */
.loading-text {
  font-family: 'AppleSDGothicNeoB', sans-serif;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.dashboard-card .v-card-title {
  font-family: 'AppleSDGothicNeoM', sans-serif;
  font-size: 1.2rem;
  font-weight: 700; /* font-weight 값을 700으로 변경 */
}

/* 내 관심기업 주가 타이틀의 버튼 정렬을 위한 스타일 */
.dashboard-card .v-card-title .edit-interests-btn {
  margin: 0 !important;
}

.stock-card .v-card-title {
  justify-content: space-between;
}

.edit-interests-btn {
  margin-left: auto !important;
}
</style>
