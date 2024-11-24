<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api';
import SearchBar from '@/components/SearchBar.vue';

const router = useRouter();
const stocks = ref([]);
const selectedDomestic = ref([]);
const selectedInternational = ref([]);

const domesticStocks = computed(() => 
  stocks.value.filter(stock => stock.market === 'Domestic').slice(0, 100)
);

const internationalStocks = computed(() => 
  stocks.value.filter(stock => stock.market === 'International').slice(0, 100)
);

const selectedStocks = computed(() => [
  ...selectedDomestic.value,
  ...selectedInternational.value
]);

const isSelected = (stock) => {
  return selectedStocks.value.some(s => s.code === stock.code);
};

const toggleStock = (stock, type) => {
  const selectedArray = type === 'Domestic' ? selectedDomestic : selectedInternational;
  const index = selectedArray.value.findIndex(s => s.code === stock.code);
  
  if (index === -1) {
    selectedArray.value.push(stock);
  } else {
    selectedArray.value.splice(index, 1);
  }
};

const removeStock = (stock) => {
  const domesticIndex = selectedDomestic.value.findIndex(s => s.code === stock.code);
  if (domesticIndex !== -1) {
    selectedDomestic.value.splice(domesticIndex, 1);
    return;
  }
  
  const internationalIndex = selectedInternational.value.findIndex(s => s.code === stock.code);
  if (internationalIndex !== -1) {
    selectedInternational.value.splice(internationalIndex, 1);
  }
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

const handleSubmit = async () => {
  try {
    // 선택된 주식들을 user_stock 테이블에 저장
    const promises = selectedStocks.value.map(stock => 
      apiClient.post('/stocks/user-stocks/', {
        stock_code: stock.code
      })
    );
    
    await Promise.all(promises);
    router.push({ name: 'Main' });
  } catch (error) {
    console.error('관심 기업 등록 실패:', error);
    if (error.response?.status === 401) {
      router.push({ name: 'Login' });
    }
  }
};

const handleSearchResultClick = (stock) => {
  const type = stock.market === 'Domestic' ? 'domestic' : 'international';
  toggleStock(stock, type);
};

onMounted(() => {
  fetchStocks();
});
</script>

<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <div class="text-center mb-6">
          <h1 class="text-h4 font-weight-bold mb-2">관심 기업 등록</h1>
          <p class="text-subtitle-1 text-medium-emphasis">투자에 관심있는 기업을 3개 이상 선택해주세요</p>
          <p class="text-caption">선택된 기업: {{ selectedStocks.length }}개</p>
        </div>

        <v-row>
          <v-col cols="12">
            <!-- 검색창 -->
            <search-bar
              class="mb-6"
              @result-selected="handleSearchResultClick"
              :selected-stocks="selectedStocks"
              :hide-selected="true"
            />

            <!-- 선택된 기업 목록을 카드 형태로 변경 -->
            <v-row class="mb-6">
              <v-col cols="12">
                <div class="selected-stocks-grid">
                  <div
                    v-for="stock in selectedStocks"
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
                      @click="removeStock(stock)"
                    ></v-btn>
                  </div>
                </div>
              </v-col>
            </v-row>

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
                        @click="toggleStock(stock, 'domestic')"
                        :class="{ 'selected-item': isSelected(stock) }"
                        hover
                      >
                        <template v-slot:prepend>
                          <v-avatar
                            :color="isSelected(stock) ? 'primary' : 'grey'"
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
                        @click="toggleStock(stock, 'international')"
                        :class="{ 'selected-item': isSelected(stock) }"
                        hover
                      >
                        <template v-slot:prepend>
                          <v-avatar
                            :color="isSelected(stock) ? 'primary' : 'grey'"
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

            <div class="text-center mt-6">
              <v-btn
                color="primary"
                size="large"
                :disabled="selectedStocks.length < 3"
                @click="handleSubmit"
              >
                등록하기
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
/* 기존 스타일을 InterestListView 스타일로 업데이트 */
.fill-height {
  min-height: 100vh;
}

.v-container {
  background-image: url('@/assets/sign_background.jpg');
  background-size: cover;
  background-position: center;
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

.selected-stocks-list {
  background-color: rgba(0, 0, 0, 0.5) !important;
  padding: 8px;
  border-radius: 8px;
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

/* 검색 필드 스타일 */
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

/* 카드 내부 스타일 */
:deep(.v-card-title) {
  color: white;
  font-size: 1.2rem;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.v-card-text) {
  color: rgba(255, 255, 255, 0.8);
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .scrollable-list {
    height: 400px;
  }
  
  .stock-list-card {
    margin-bottom: 16px;
  }
}

@media (max-width: 600px) {
  .scrollable-list {
    height: 300px;
  }
}

/* 선택된 주식 그리드 스타일 */
.selected-stocks-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

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

/* 제목 스타일 개선 */
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

/* 버튼 스타일 개선 */
:deep(.v-btn.v-btn--size-large) {
  background: linear-gradient(135deg, #6439ff, #4f29cc) !important;
  box-shadow: 0 4px 20px rgba(100, 57, 255, 0.4);
  font-weight: 600;
  letter-spacing: 0.5px;
  border-radius: 12px;
  transition: all 0.3s ease;
}

:deep(.v-btn.v-btn--size-large:hover) {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(100, 57, 255, 0.5);
}

:deep(.v-btn.v-btn--size-large:disabled) {
  background: linear-gradient(135deg, #4a4a4a, #3a3a3a) !important;
  opacity: 0.7;
}
</style>