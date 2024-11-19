<template>
  <v-container>
    <v-text-field
      v-model="searchQuery"
      label="관심 기업 검색"
      @input="searchCompanies"
    ></v-text-field>
    <v-list>
      <v-list-item
        v-for="company in searchResults"
        :key="company.id"
        @click="addInterest(company)"
      >
        <v-list-item-title>
          {{ company.name }} ({{ company.ticker }})
        </v-list-item-title>
      </v-list-item>
    </v-list>

    <v-divider class="my-4"></v-divider>

    <h2>내 관심 기업</h2>
    <v-list>
      <v-list-item
        v-for="interest in interests"
        :key="interest.id"
        :to="{
          name: 'InterestDetail',
          params: {
            ticker: interest.company.ticker,
            name: interest.company.name,
          },
        }"
        link
      >
        <v-list-item-title>
          {{ interest.company.name }} ({{ interest.company.ticker }})
        </v-list-item-title>
        <v-list-item-action>
          <v-btn icon @click.stop="removeInterest(interest.id)">
            <v-icon>mdi-delete</v-icon>
          </v-btn>
        </v-list-item-action>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script>
import apiClient from '@/api';

export default {
  name: 'InterestListView',
  data() {
    return {
      searchQuery: '',
      searchResults: [],
      interests: [],
    };
  },
  created() {
    this.getInterests();
  },
  methods: {
    async searchCompanies() {
      if (this.searchQuery.length < 2) {
        this.searchResults = [];
        return;
      }
      try {
        const response = await apiClient.get('companies/companies/', {
          params: {
            search: this.searchQuery,
          },
        });
        this.searchResults = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    async addInterest(company) {
      try {
        await apiClient.post('companies/interests/', {
          company: {
            name: company.name,
            ticker: company.ticker,
          },
        });
        this.getInterests();
      } catch (error) {
        console.error(error);
      }
    },
    async getInterests() {
      try {
        const response = await apiClient.get('companies/interests/');
        this.interests = response.data;
      } catch (error) {
        console.error(error);
      }
    },
    async removeInterest(interestId) {
      try {
        await apiClient.delete(`companies/interests/${interestId}/`);
        this.getInterests();
      } catch (error) {
        console.error(error);
      }
    },
  },
};
</script>

<style scoped>
/* 필요한 스타일을 추가합니다 */
</style> 