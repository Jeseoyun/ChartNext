<script setup>
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

const refreshMain = () => router.push({ name: 'Main' });
const goStocks = () => router.push({ name: 'StockDetail' });
const goNews = () => router.push({ name: 'News' });
const editInterests = () => router.push({ name: 'Interests' });

const handleLogout = async () => {
  try {
    await userStore.logout();
    router.push({ name: 'Home' });
  } catch (error) {
    console.error('로그아웃 실패:', error);
  }
};
</script>

<template>
  <div class="header">
    <img src="@/assets/logo.png" alt="Logo" class="logo" @click="refreshMain" />
    <div class="header-right">

      <nav class="navbar">
        <button @click="goStocks">종목</button>
        <button @click="goNews">뉴스</button>
        <button @click="handleLogout">로그아웃</button>
      </nav>
    </div>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.logo {
  height: 100px;
  cursor: pointer;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 30px;
}

.edit-interests {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'AppleSDGothicNeoB', sans-serif;
  padding: 8px 16px;
  border-radius: 20px;
}

.edit-interests:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: #9350ff;
}

.navbar {
  display: flex;
  gap: 30px;
}

.navbar button {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-family: 'AppleSDGothicNeoB', sans-serif;
}

.navbar button:hover {
  background: linear-gradient(120deg, #9350ff, #765eff);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
</style> 