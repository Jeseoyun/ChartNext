<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api';
import SearchBar from '@/components/SearchBar.vue';
import NavBarComponent from '@/components/NavBarComponent.vue';
import LogoComponent from '@/components/LogoComponent.vue';

const router = useRouter();
const stocks = ref([]);
const userStocks = ref([]);

const domesticStocks = computed(() => 
  stocks.value.filter(stock => stock.market === 'Domestic').slice(0, 100)
);

const internationalStocks = computed(() => 
  stocks.value.filter(stock => stock.market === 'International').slice(0, 100)
);

const isUserStock = (stock) => {
  return userStocks.value.some(s => s.code === stock.code);
};

const fetchStocks = async () => {
  try {
    const response = await apiClient.get('/stocks/stocks/');
    stocks.value = response.data;
  } catch (error) {
    console.error('주식 데이터 로드 실패:', error);
    if (error.response?.status === 401) {
      router.push({ name: 'Login' });
    }
  }
};

const fetchUserStocks = async () => {
  try {
    const response = await apiClient.get('/stocks/user-stocks/');
    userStocks.value = response.data;
  } catch (error) {
    console.error('관심 종목 로드 실패:', error);
    if (error.response?.status === 401) {
      router.push({ name: 'Login' });
    }
  }
};

const addUserStock = async (stock) => {
  if (isUserStock(stock)) return;
  
  try {
    await apiClient.post('/stocks/user-stocks/', {
      stock_code: stock.code
    });
    await fetchUserStocks(); // 목록 새로고침
  } catch (error) {
    console.error('관심 기업 추가 실패:', error);
    if (error.response?.status === 401) {
      router.push({ name: 'Login' });
    }
  }
};

const removeUserStock = async (stock) => {
  try {
    await apiClient.delete(`/stocks/user-stocks/${stock.code}/`);
    await fetchUserStocks(); // 목록 새로고침
  } catch (error) {
    console.error('관심 기업 삭제 실패:', error);
    if (error.response?.status === 401) {
      router.push({ name: 'Login' });
    }
  }
};

const handleSearchResultClick = (stock) => {
  addUserStock(stock);
};

onMounted(() => {
  fetchStocks();
  fetchUserStocks();
});
</script>

<template>
  <v-container fluid class="fill-height">
    <!-- 네비게이션 바를 fixed header로 변경 -->
    <div class="fixed-header">
      <LogoComponent />
      <NavBarComponent />
    </div>

    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <div class="text-center mb-6">
          <h1 class="text-h4 font-weight-bold mb-2">관심 기업 관리</h1>
          <p class="text-subtitle-1 text-medium-emphasis">현재 등록된 관심 기업을 관리하고 새로운 기업을 추가할 수 있습니다</p>
          <p class="text-caption">등록된 기업: {{ userStocks.length }}개</p>
        </div>

        <v-row>
          <v-col cols="12">
            <!-- 현재 등록된 관심 기업 목록 -->
            <v-card class="mb-6">
              <v-card-title class="text-center py-4">
                <v-icon icon="mdi-heart" class="mr-2"></v-icon>
                내 관심 기업
              </v-card-title>
              <v-card-text>
                <div class="selected-stocks-grid">
                  <div
                    v-for="stock in userStocks"
                    :key="stock.code"
                    class="selected-stock-chip"
                  >
                    <span class="stock-name">{{ stock.name }}</span>
                    <span class="stock-code">({{ stock.code }})</span>
                    <v-btn
                      icon="mdi-close"
                      size="x-small"
                      color="white"
                      variant="text"
                      density="compact"
                      @click="removeUserStock(stock)"
                    ></v-btn>
                  </div>
                </div>
              </v-card-text>
            </v-card>

            <!-- 검색창 -->
            <search-bar
              class="mb-6"
              @result-selected="handleSearchResultClick"
            />

            <v-row>
              <!-- 국내 주식 섹션 -->
              <v-col cols="12" md="6">
                <v-card>
                  <v-card-title class="text-center py-4">
                    <v-icon icon="mdi-flag" class="mr-2"></v-icon>
                    국내 주식 Top 100
                  </v-card-title>
                  <v-card-text>
                    <v-list class="scrollable-list">
                      <v-list-item
                        v-for="(stock, index) in domesticStocks"
                        :key="stock.code"
                        :value="stock"
                        :title="`${stock.name} (${stock.code})`"
                        :subtitle="stock.category"
                        @click="addUserStock(stock)"
                        :class="{ 'selected-item': isUserStock(stock) }"
                        hover
                      >
                        <template v-slot:prepend>
                          <v-avatar
                            :color="isUserStock(stock) ? 'primary' : 'grey'"
                            size="32"
                            class="mr-3"
                          >
                            {{ index + 1 }}
                          </v-avatar>
                        </template>
                      </v-list-item>
                    </v-list>
                  </v-card-text>
                </v-card>
              </v-col>

              <!-- 해외 주식 섹션 -->
              <v-col cols="12" md="6">
                <v-card>
                  <v-card-title class="text-center py-4">
                    <v-icon icon="mdi-earth" class="mr-2"></v-icon>
                    해외 주식 Top 100
                  </v-card-title>
                  <v-card-text>
                    <v-list class="scrollable-list">
                      <v-list-item
                        v-for="(stock, index) in internationalStocks"
                        :key="stock.code"
                        :value="stock"
                        :title="`${stock.name} (${stock.code})`"
                        :subtitle="stock.category"
                        @click="addUserStock(stock)"
                        :class="{ 'selected-item': isUserStock(stock) }"
                        hover
                      >
                        <template v-slot:prepend>
                          <v-avatar
                            :color="isUserStock(stock) ? 'primary' : 'grey'"
                            size="32"
                            class="mr-3"
                          >
                            {{ index + 1 }}
                          </v-avatar>
                        </template>
                      </v-list-item>
                    </v-list>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.fill-height {
  min-height: 100vh;
}

.v-container {
  background-image: url('@/assets/sign_background.jpg');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
}

/* 카드 스타일 */
.v-card {
  background: linear-gradient(to right bottom, rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.5)) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

/* 텍스트 스타일 */
.text-h4, .text-subtitle-1, .text-caption {
  color: white !important;
}

/* 리스트 스타일 */
.v-list {
  background-color: transparent !important;
}

.selected-stocks-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.scrollable-list {
  max-height: 400px;
  overflow-y: auto;
}

/* 리스트 아이템 스타일 */
:deep(.v-list-item) {
  color: white !important;
}

:deep(.v-list-item-title) {
  color: white !important;
}

:deep(.v-list-item-subtitle) {
  color: rgba(255, 255, 255, 0.7) !important;
}

.selected-item {
  background: linear-gradient(to right, rgba(100, 57, 255, 0.3), rgba(100, 57, 255, 0.1)) !important;
  border-left: 4px solid #6439ff !important;
}

:deep(.v-list-item--hover) {
  background: rgba(255, 255, 255, 0.05) !important;
}

/* 스크롤바 스타일 */
.scrollable-list::-webkit-scrollbar {
  width: 6px;
}

.scrollable-list::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

.scrollable-list::-webkit-scrollbar-thumb {
  background: rgba(100, 57, 255, 0.3);
  border-radius: 3px;
}

.scrollable-list::-webkit-scrollbar-thumb:hover {
  background: rgba(100, 57, 255, 0.5);
}

/* 선택된 주식 칩 스타일 */
.selected-stock-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(100, 57, 255, 0.2), rgba(100, 57, 255, 0.1));
  border: 1px solid rgba(100, 57, 255, 0.3);
  border-radius: 20px;
  color: white;
  transition: all 0.3s ease;
}

.selected-stock-chip:hover {
  background: linear-gradient(135deg, rgba(100, 57, 255, 0.3), rgba(100, 57, 255, 0.2));
  transform: translateY(-2px);
}

.stock-name {
  font-weight: 500;
}

.stock-code {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9em;
}

/* 제목 스타일 */
.text-h4 {
  font-family: 'Pretendard', sans-serif;
  font-weight: 700 !important;
  background: linear-gradient(45deg, #fff, #e0e0e0);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.5px;
}

.text-subtitle-1 {
  font-family: 'Pretendard', sans-serif;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8) !important;
}

.text-caption {
  font-family: 'Pretendard', sans-serif;
  color: rgba(255, 255, 255, 0.6) !important;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .scrollable-list {
    height: 400px;
  }
}

@media (max-width: 600px) {
  .scrollable-list {
    height: 300px;
  }
}

/* 카드 타이틀과 텍스트 스타일 */
:deep(.v-card-title) {
  color: white !important;
}

:deep(.v-card-text) {
  color: white !important;
}

/* 리스트 아이템 스타일 */
:deep(.v-list-item) {
  color: white !important;
}

:deep(.v-list-item-title) {
  color: white !important;
}

:deep(.v-list-item-subtitle) {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* 검색바 스타일 */
:deep(.v-field__input) {
  color: white !important;
}

:deep(.v-field__outline) {
  color: rgba(255, 255, 255, 0.7) !important;
}

:deep(.v-label) {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* 자동완성 스타일 제거 */
:deep(input:-webkit-autofill),
:deep(input:-webkit-autofill:hover),
:deep(input:-webkit-autofill:focus),
:deep(input:-webkit-autofill:active) {
  -webkit-box-shadow: 0 0 0 30px transparent inset !important;
  -webkit-text-fill-color: white !important;
  transition: background-color 5000s ease-in-out 0s;
  background-color: transparent !important;
}

/* fixed header 스타일 추가 */
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  width: 1920px;
  height: 80px;
  background-color: transparent;
  z-index: 1000;
}

/* 컨텐츠 여백 조정 */
.v-row {
  margin-top: 80px;
}
</style>
