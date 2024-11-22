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
            ></v-text-field>

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
                        v-for="(stock, index) in filteredDomesticStocks"
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
                        v-for="(stock, index) in filteredInternationalStocks"
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

export default {
  name: 'UserInitView',
  setup() {
    const router = useRouter();
    const stocks = ref([]);
    const selectedDomestic = ref([]);
    const selectedInternational = ref([]);
    const searchQuery = ref('');

    const domesticStocks = computed(() => 
      stocks.value.filter(stock => stock.market === 'Domestic').slice(0, 100)
    );

    const internationalStocks = computed(() => 
      stocks.value.filter(stock => stock.market === 'International').slice(0, 100)
    );

    const filteredDomesticStocks = computed(() => {
      if (!searchQuery.value) return domesticStocks.value;
      const query = searchQuery.value.toLowerCase();
      return domesticStocks.value.filter(stock => 
        stock.name.toLowerCase().includes(query) || 
        stock.code.toLowerCase().includes(query)
      );
    });

    const filteredInternationalStocks = computed(() => {
      if (!searchQuery.value) return internationalStocks.value;
      const query = searchQuery.value.toLowerCase();
      return internationalStocks.value.filter(stock => 
        stock.name.toLowerCase().includes(query) || 
        stock.code.toLowerCase().includes(query)
      );
    });

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
        router.push({ name: 'Home' });
      } catch (error) {
        console.error('관심 기업 등록 실패:', error);
        if (error.response?.status === 401) {
          router.push({ name: 'Login' });
        }
      }
    };

    onMounted(() => {
      fetchStocks();
    });

    return {
      domesticStocks,
      internationalStocks,
      filteredDomesticStocks,
      filteredInternationalStocks,
      selectedDomestic,
      selectedInternational,
      selectedStocks,
      searchQuery,
      handleSubmit,
      toggleStock,
      removeStock,
      isSelected,
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
  max-height: 400px; /* 원하는 높이로 설정 */
  overflow-y: auto;
}
</style>
