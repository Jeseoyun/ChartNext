<template>
  <v-container fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="10" md="8" lg="6" class="text-center">
        <h1 class="text-h3 font-weight-bold mb-4">
          Chart Next
        </h1>
        <p class="text-h5 mb-6">
          RAG 기반 뉴스 추천 및 주가 예측 시스템
        </p>
        <v-btn
          v-if="!isAuthenticated"
          color="primary"
          size="large"
          @click="$router.push({ name: 'Login' })"
        >
          시작하기
        </v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

export default {
  name: 'HomeView',
  setup() {
    const userStore = useUserStore()
    const isAuthenticated = computed(() => !!userStore.token)

    return {
      isAuthenticated
    }
  }
}
</script>