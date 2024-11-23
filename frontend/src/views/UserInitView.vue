<template>
  <v-container fluid class="fill-height">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8">
        <div class="text-center mb-6">
          <h1 class="text-h4 mb-2">관심 기업 등록</h1>
          <p class="text-subtitle-1">투자에 관심있는 기업을 3개 이상 선택해주세요</p>
          <p class="text-caption">선택된 기업: {{ selectedStocks.length }}개</p>
        </div>

        <v-row>
          <!-- 주식 선택 영역 -->
          <v-col cols="12">
            <!-- 검색창 -->
            <v-text-field
              v-model="searchQuery"
              label="기업명 또는 종목코드로 검색"
              prepend-inner-icon="mdi-magnify"
              clearable
              class="mb-4"
              @input="handleSearch"
              @click:clear="clearSearchResults"
            >
              <template v-slot:append-inner>
                <v-progress-circular
                  v-if="isSearching"
                  indeterminate
                  size="20"
                ></v-progress-circular>
              </template>
            </v-text-field>

            <!-- 검색 결과 드롭다운 -->
            <v-card
              v-if="(normalSearchResults.length > 0 || mlSearchResults.length > 0)"
              class="search-results mb-4"
              elevation="2"
            >
              <v-list class="scrollable-list">
                <!-- 일반 검색 결과 -->
                <template v-if="normalSearchResults.length > 0">
                  <v-list-subheader>일반 검색 결과</v-list-subheader>
                  <v-list-item
                    v-for="result in normalSearchResults"
                    :key="`normal-${result.code}`"
                    :title="`${result.name} (${result.code})`"
                    :subtitle="`${result.industry} | ${result.sector}`"
                    @click="handleSearchResultClick(result)"
                    hover
                    v-show="!isSelected(result)"
                  >
                  </v-list-item>
                </template>

                <!-- ML 검색 결과 -->
                <template v-if="mlSearchResults.length > 0">
                  <v-divider v-if="normalSearchResults.length > 0"></v-divider>
                  <v-list-subheader>유사도 기반 검색 결과</v-list-subheader>
                  <v-list-item
                    v-for="result in mlSearchResults"
                    :key="`ml-${result.code}`"
                    :title="`${result.name} (${result.code})`"
                    :subtitle="`${result.industry} | ${result.sector} (유사도: ${(result.similarity * 100).toFixed(1)}%)`"
                    @click="handleSearchResultClick(result)"
                    hover
                    v-show="!isSelected(result)"
                  >
                  </v-list-item>
                </template>
              </v-list>
            </v-card>

            <!-- 선택된 기업 목록 -->
            <v-row>
              <v-col cols="12">
                <v-list class="selected-stocks-list">
                  <v-list-item
                    v-for="stock in selectedStocks"
                    :key="stock.code"
                    :title="`${stock.name} (${stock.code})`"
                    :subtitle="stock.category"
                  >
                    <template v-slot:append>
                      <v-btn
                        icon="mdi-close"
                        size="xx-small"
                        @click="removeStock(stock)"
                        color="grey"
                      ></v-btn>
                    </template>
                  </v-list-item>
                </v-list>
              </v-col>
            </v-row>

            <v-row>
              <!-- 국내 주식 섹션 -->
              <v-col cols="12" md="6">
                <v-card>
                  <v-card-title class="text-center">국내 주식 Top 100</v-card-title>
                  <v-card-text>
                    <v-list class="scrollable-list">
                      <v-list-item
                        v-for="(stock, index) in domesticStocks"
                        :key="stock.code"
                        :value="stock"
                        :title="`${index + 1}. ${stock.name} (${stock.code})`"
                        :subtitle="stock.category"
                        @click="toggleStock(stock, 'domestic')"
                        :class="{ 'selected-item': isSelected(stock) }"
                        hover
                      >
                      </v-list-item>
                    </v-list>
                  </v-card-text>
                </v-card>
              </v-col>

              <!-- 해외 주식 섹션 -->
              <v-col cols="12" md="6">
                <v-card>
                  <v-card-title class="text-center">해외 주식 Top 100</v-card-title>
                  <v-card-text>
                    <v-list class="scrollable-list">
                      <v-list-item
                        v-for="(stock, index) in internationalStocks"
                        :key="stock.code"
                        :value="stock"
                        :title="`${index + 1}. ${stock.name} (${stock.code})`"
                        :subtitle="stock.category"
                        @click="toggleStock(stock, 'international')"
                        :class="{ 'selected-item': isSelected(stock) }"
                        hover
                      >
                      </v-list-item>
                    </v-list>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-col>
        </v-row>

        <div class="text-center mt-6">
          <v-btn
            color="white"
            class="black--text"
            size="large"
            :disabled="selectedStocks.length < 3"
            @click="handleSubmit"
          >
            등록하기
          </v-btn>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api';
import { debounce } from 'lodash';

export default {
  name: 'UserInitView',
  setup() {
    const router = useRouter();
    const stocks = ref([]);
    const selectedDomestic = ref([]);
    const selectedInternational = ref([]);
    const searchQuery = ref('');
    const normalSearchResults = ref([]);
    const mlSearchResults = ref([]);
    const isSearching = ref(false);

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

    const handleSearch = debounce(async () => {
      if (!searchQuery.value || searchQuery.value.length < 2) {
        normalSearchResults.value = [];
        mlSearchResults.value = [];
        return;
      }

      isSearching.value = true;
      try {
        // 일반 검색과 ML 검색 동시 실행
        const [searchResponse, mlSearchResponse] = await Promise.all([
          apiClient.get('/stocks/stocks/search/', {
            params: { query: searchQuery.value }
          }),
          apiClient.get('/stocks/stocks/ml-search/', {
            params: { query: searchQuery.value }
          })
        ]);

        // 각각의 검색 결과를 별도로 저장
        normalSearchResults.value = searchResponse.data.results.slice(0, 5); // 상위 5개
        
        // ML 검색 결과에서 유사도 40% 이상인 결과만 필터링
        mlSearchResults.value = mlSearchResponse.data.results
          .filter(result => result.similarity >= 0.4); // 40% = 0.4
      } catch (error) {
        console.error('검색 실패:', error);
        normalSearchResults.value = [];
        mlSearchResults.value = [];
      } finally {
        isSearching.value = false;
      }
    }, 300);

    const handleSearchResultClick = (stock) => {
      const type = stock.market === 'Domestic' ? 'domestic' : 'international';
      toggleStock(stock, type);
      normalSearchResults.value = []; // 결과 목록 닫기
      mlSearchResults.value = []; // 결과 목록 닫기
      searchQuery.value = ''; // 검색어 초기화
    };

    const clearSearchResults = () => {
      normalSearchResults.value = [];
      mlSearchResults.value = [];
    };

    onMounted(() => {
      fetchStocks();
    });

    return {
      domesticStocks,
      internationalStocks,
      selectedDomestic,
      selectedInternational,
      selectedStocks,
      searchQuery,
      handleSubmit,
      toggleStock,
      removeStock,
      isSelected,
      normalSearchResults,
      mlSearchResults,
      isSearching,
      handleSearch,
      handleSearchResultClick,
      clearSearchResults,
    };
  },
};
</script>

<style scoped>
/* 기존 스타일 대체 */
.fill-height {
  min-height: 100vh;
}

.v-container {
  background-image: url('@/assets/sign_background.jpg');
  background-size: cover;
  background-position: center;
}

/* 카드 스타일 수정 */
.v-card {
  background-color: rgba(0, 0, 0, 0.1) !important;
  color: white !important;
  border-radius: 8px;
  box-shadow: 0px 0px 200px #6439ff60 !important;
  backdrop-filter: blur(10px);
}

/* 텍스트 색상 수정 */
.text-h4, .text-subtitle-1, .text-caption {
  color: white !important;
}

/* 검색 결과 카드 스타일 */
.search-results {
  background-color: rgba(0, 0, 0, 0.1) !important;
  backdrop-filter: blur(10px);
}

.search-results .v-list-item {
  color: white !important;
}

.search-results .v-list-subheader {
  color: white !important;
  background-color: rgba(100, 57, 255, 0.1) !important;
  font-weight: bold;
}

/* 리스트 아이템 스타일 */
.v-list-item {
  color: white !important;
}

.selected-item {
  background-color: rgba(100, 57, 255, 0.2) !important;
  border-left: 4px solid #6439ff !important;
}

.v-list-item:hover {
  cursor: pointer;
  background-color: rgba(100, 57, 255, 0.1) !important;
}

/* 스크롤 리스트 */
.scrollable-list {
  max-height: 400px;
  overflow-y: auto;
}

/* 선택된 주식 리스트 */
.selected-stocks-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-start;
  background-color: transparent !important;
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

/* 스크롤바 스타일링 */
:deep(.scrollable-list::-webkit-scrollbar) {
  width: 8px;
}

:deep(.scrollable-list::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.1);
}

:deep(.scrollable-list::-webkit-scrollbar-thumb) {
  background-color: rgba(100, 57, 255, 0.5);
  border-radius: 4px;
}

:deep(.scrollable-list::-webkit-scrollbar-thumb:hover) {
  background-color: rgba(100, 57, 255, 0.7);
}

/* 리스트 관련 스타일 수정/추가 */

/* 리스트 컨테이너 배경 */
.v-list {
  background-color: rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(10px);
  border-radius: 8px;
}

/* 검색 결과 리스트 */
.search-results {
  background-color: rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(10px);
}

.search-results .v-list {
  background-color: transparent !important;
}

/* 선택된 주식 리스트 */
.selected-stocks-list {
  background-color: rgba(0, 0, 0, 0.5) !important;
  padding: 8px;
  border-radius: 8px;
}

/* 스크롤 리스트 배경 */
.scrollable-list {
  background-color: rgba(0, 0, 0, 0.5) !important;
}

/* 리스트 아이템 hover 효과 */
.v-list-item:hover {
  background-color: rgba(100, 57, 255, 0.2) !important;
}

/* 선택된 아이템 스타일 */
.selected-item {
  background-color: rgba(100, 57, 255, 0.3) !important;
  border-left: 4px solid #6439ff !important;
}

/* 카드 내부 리스트 영역 */
.v-card-text {
  background-color: rgba(0, 0, 0, 0.3) !important;
  border-radius: 0 0 8px 8px;
}

/* 리스트 서브헤더 */
.v-list-subheader {
  background-color: rgba(0, 0, 0, 0.3) !important;
  color: white !important;
}
</style>