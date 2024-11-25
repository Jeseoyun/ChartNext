<template>
  <nav class="navbar">
    <button @click="goStocks">종목</button>
    <button @click="goNews">뉴스</button>
    <button v-if="!isLoggedIn" @click="goLogin">로그인</button>
    <button v-else @click="logout">로그아웃</button>
  </nav>
</template>

<script>
import { useUserStore } from '@/stores/user';
import { computed } from 'vue';

export default {
  name: 'NavBarComponent',
  setup() {
    const userStore = useUserStore();
    const isLoggedIn = computed(() => userStore.isLoggedIn);

    return {
      isLoggedIn
    };
  },
  methods: {
    goStocks() {
      this.$router.push({ name: 'Interests' });
    },
    goNews() {
      this.$router.push({ 
        name: 'News',
        query: { category: 'all' }
      });
    },
    goLogin() {
      this.$router.push({ name: 'Login' });
    },
    logout() {
      // 로그아웃 로직 구현
      this.$router.push({ name: 'Home' });
    }
  },
};
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 25px;
  width: 400px;
  left: 565px;
  display: flex;
  gap: 60px;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  z-index: 1000;
  justify-content: center;
}

.navbar button {
  background: transparent;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  background-clip: text;
  -webkit-background-clip: text;
}

.navbar button:hover {
  background: linear-gradient(120deg, #9350ff, #765eff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
</style> 