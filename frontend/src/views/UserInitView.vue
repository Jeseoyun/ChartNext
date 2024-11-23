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

              <!-- 해�� 주식 섹션 -->
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
        console.error('관심 기업 등록 �����:', error);
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
.fill-height {
  min-height: calc(100vh - 64px);
}

.selected-item {
  background-color: var(--v-primary-lighten5);
  border-left: 4px solid var(--v-primary-base);
}

.v-list-item:hover {
  cursor: pointer;
}

.selected-stocks-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: flex-start;
}

.scrollable-list {
  max-height: 400px;
  overflow-y: auto;
}

.search-results {
  position: absolute;
  z-index: 1000;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  background: white;
}

.search-results .v-list-item {
  cursor: pointer;
}

.search-results .v-list-item:hover {
  background-color: var(--v-primary-lighten5);
}

.v-list-subheader {
  background-color: var(--v-primary-lighten5);
  font-weight: bold;
}
</style>
