<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { debounce } from 'lodash';
import apiClient from '@/api';

// Props 정의
const props = defineProps({
  label: {
    type: String,
    default: '기업명 또는 종목코드로 검색'
  }
});

// Emits 정의
const emit = defineEmits(['result-selected']);

// Reactive 변수들
const searchQuery = ref('');
const normalSearchResults = ref([]);
const mlSearchResults = ref([]);
const isSearching = ref(false);

// 메서드들
const handleSearch = debounce(async () => {
  if (!searchQuery.value || searchQuery.value.length < 2) {
    normalSearchResults.value = [];
    mlSearchResults.value = [];
    return;
  }

  isSearching.value = true;
  try {
    const [searchResponse, mlSearchResponse] = await Promise.all([
      apiClient.get('/stocks/stocks/search/', {
        params: { query: searchQuery.value }
      }),
      apiClient.get('/stocks/stocks/ml-search/', {
        params: { query: searchQuery.value }
      })
    ]);

    normalSearchResults.value = searchResponse.data.results.slice(0, 5);
    mlSearchResults.value = mlSearchResponse.data.results
      .filter(result => result.similarity >= 0.4);
  } catch (error) {
    console.error('검색 실패:', error);
    normalSearchResults.value = [];
    mlSearchResults.value = [];
  } finally {
    isSearching.value = false;
  }
}, 300);

const handleSearchResultClick = (result) => {
  emit('result-selected', result);
  clearSearchResults();
};

const clearSearchResults = () => {
  searchQuery.value = '';
  normalSearchResults.value = [];
  mlSearchResults.value = [];
};

const handleClickOutside = (event) => {
  const searchContainer = event.target.closest('.search-container');
  if (!searchContainer) {
    clearSearchResults();
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div class="search-container">
    <v-text-field
      v-model="searchQuery"
      :label="label"
      prepend-inner-icon="mdi-magnify"
      clearable
      class="mb-4 search-field"
      variant="outlined"
      color="white"
      bg-color="rgba(0, 0, 0, 0.5)"
      @input="handleSearch"
      @click:clear="clearSearchResults"
    >
      <template v-slot:append-inner>
        <v-progress-circular
          v-if="isSearching"
          indeterminate
          size="20"
          color="white"
        ></v-progress-circular>
      </template>
    </v-text-field>

    <!-- 검색 결과 드롭다운 -->
    <v-card
      v-if="(normalSearchResults.length > 0 || mlSearchResults.length > 0)"
      class="search-results mb-4"
      elevation="2"
    >
      <v-list class="search-list">
        <!-- 일반 검색 결과 -->
        <template v-if="normalSearchResults.length > 0">
          <v-list-subheader class="search-subheader">일반 검색 결과</v-list-subheader>
          <v-list-item
            v-for="result in normalSearchResults"
            :key="`normal-${result.code}`"
            :title="`${result.name} (${result.code})`"
            :subtitle="`${result.industry} | ${result.sector}`"
            @click="handleSearchResultClick(result)"
            class="search-item"
            hover
          >
          </v-list-item>
        </template>

        <!-- ML 검색 결과 -->
        <template v-if="mlSearchResults.length > 0">
          <v-divider v-if="normalSearchResults.length > 0"></v-divider>
          <v-list-subheader class="search-subheader">유사도 기반 검색 결과</v-list-subheader>
          <v-list-item
            v-for="result in mlSearchResults"
            :key="`ml-${result.code}`"
            :title="`${result.name} (${result.code})`"
            :subtitle="`${result.industry} | ${result.sector} (유사도: ${(result.similarity * 100).toFixed(1)}%)`"
            @click="handleSearchResultClick(result)"
            class="search-item"
            hover
          >
          </v-list-item>
        </template>
      </v-list>
    </v-card>
  </div>
</template>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
}

.search-results {
  position: absolute;
  width: 100%;
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.9) !important;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  margin-top: -38px; /* mb-4 상쇄를 위한 음수 마진 */
}

:deep(.search-field) {
  .v-field__input {
    color: white !important;
  }

  .v-field__outline {
    color: rgba(255, 255, 255, 0.3) !important;
  }

  .v-label {
    color: rgba(255, 255, 255, 0.7) !important;
  }

  .v-icon {
    color: rgba(255, 255, 255, 0.7) !important;
  }
}

.search-list {
  background-color: transparent !important;
  padding: 8px 0;
}

.search-subheader {
  color: rgba(255, 255, 255, 0.7) !important;
  font-size: 0.875rem;
}

.search-item {
  transition: background-color 0.3s ease;
  
  &:hover {
    background-color: rgba(147, 80, 255, 0.1) !important;
  }

  :deep(.v-list-item-title) {
    color: white !important;
    font-size: 1rem;
  }

  :deep(.v-list-item-subtitle) {
    color: rgba(255, 255, 255, 0.7) !important;
    font-size: 0.875rem;
  }
}
</style> 