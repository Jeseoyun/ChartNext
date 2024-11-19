<template>
  <v-container>
    <h2>추천 뉴스</h2>
    <v-list>
      <v-list-item v-for="(news, index) in newsList" :key="index">
        <v-list-item-content>
          <v-list-item-title>
            <a :href="news.link" target="_blank">{{ news.title }}</a>
          </v-list-item-title>
          <v-list-item-subtitle>{{ news.snippet }}</v-list-item-subtitle>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script>
import apiClient from '@/api';

export default {
  name: 'NewsListView',
  data() {
    return {
      newsList: [],
    };
  },
  async created() {
    try {
      const response = await apiClient.get('companies/news/recommend/');
      this.newsList = response.data;
    } catch (error) {
      console.error(error);
    }
  },
};
</script>

<style scoped>
/* 필요한 스타일을 추가합니다 */
</style> 