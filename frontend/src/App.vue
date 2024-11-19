<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title>
        <router-link to="/" class="text-decoration-none" style="color: inherit; text-decoration: none;">
          Chart Next
        </router-link>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn text @click="$router.push({ name: 'Interests' })">관심 기업</v-btn>
      <v-btn text @click="$router.push({ name: 'News' })">추천 뉴스</v-btn>
      <v-btn text @click="$router.push({ name: 'Chatbot' })">챗봇</v-btn>
      <template v-if="isAuthenticated">
        <v-btn text @click="logout">로그아웃</v-btn>
      </template>
      <template v-else>
        <v-btn text @click="$router.push({ name: 'Signup' })">회원가입</v-btn>
        <v-btn text @click="goToLogin">로그인</v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { computed } from 'vue';
import { useUserStore } from '@/stores/user';

export default {
  name: 'App',
  setup() {
    const userStore = useUserStore();
    const isAuthenticated = computed(() => !!userStore.token);

    const logout = () => {
      userStore.logout();
    };

    return {
      isAuthenticated,
      logout,
    };
  },
  methods: {
    goToLogin() {
      this.$router.push({ name: 'Login' });
    },
  },
};
</script>

<style>
/* 필요에 따라 스타일 추가 */
</style>
