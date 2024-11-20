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
          <!-- 국내 주식 섹션 -->
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title class="text-center">국내 주식</v-card-title>
              <v-card-text>
                <v-list select-strategy="multiple" v-model:selected="selectedDomestic">
                  <v-list-item
                    v-for="stock in domesticStocks"
                    :key="stock.code"
                    :value="stock"
                    :title="`${stock.name} (${stock.code})`"
                    :subtitle="stock.category"
                  >
                    <template v-slot:append>
                      <v-checkbox-btn v-model="selectedDomestic" :value="stock"></v-checkbox-btn>
                    </template>
                  </v-list-item>
                </v-list>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- 해외 주식 섹션 -->
          <v-col cols="12" md="6">
            <v-card>
              <v-card-title class="text-center">해외 주식</v-card-title>
              <v-card-text>
                <v-list select-strategy="multiple" v-model:selected="selectedInternational">
                  <v-list-item
                    v-for="stock in internationalStocks"
                    :key="stock.code"
                    :value="stock"
                    :title="`${stock.name} (${stock.code})`"
                    :subtitle="stock.category"
                  >
                    <template v-slot:append>
                      <v-checkbox-btn v-model="selectedInternational" :value="stock"></v-checkbox-btn>
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

    const domesticStocks = computed(() => 
      stocks.value.filter(stock => stock.market === 'domestic')
    );

    const internationalStocks = computed(() => 
      stocks.value.filter(stock => stock.market === 'international')
    );

    const selectedStocks = computed(() => [
      ...selectedDomestic.value,
      ...selectedInternational.value
    ]);

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
      selectedDomestic,
      selectedInternational,
      selectedStocks,
      handleSubmit,
    };
  },
};
</script>

<style scoped>
.fill-height {
  min-height: calc(100vh - 64px); /* 앱바 높이를 고려 */
}
</style>
