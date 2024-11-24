<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import apiClient from '@/api';

const router = useRouter();
const userStore = useUserStore();
const userStocks = ref([]);

// 사용자의 관심 종목 로드
const loadUserStocks = async () => {
  try {
    const response = await apiClient.get('/stocks/user-stocks/');
    userStocks.value = response.data;
  } catch (error) {
    console.error('관심 종목 로드 실패:', error);
  }
};

const goToStockDetail = (stock) => {
  if (stock) {
    router.push({ 
      name: 'StockDetail',
      state: { selectedStock: stock }
    });
  }
};

const refreshMain = () => {
  router.go(0);
};

const goStocks = () => {
  router.push({ name: 'StockDetail' });
};

const goNews = () => {
  router.push({ name: 'News' });
};

const handleLogout = async () => {
  try {
    await userStore.logout();
    router.push({ name: 'Home' });
  } catch (error) {
    console.error('로그아웃 실패:', error);
  }
};

const editInterests = () => {
  router.push({ name: 'Interests' });
};

onMounted(() => {
  loadUserStocks();
});
</script>

<template>
  <v-container fluid class="pa-0">
    <div class="main">
      <video autoplay loop muted playsinline class="background-video">
        <source src="@/assets/main_background.mp4" type="video/mp4" />
      </video>
      <div class="content">
        <div class="header">
          <img src="@/assets/logo.png" alt="Logo" class="logo" @click="refreshMain" />
          <div class="header-right">
            <button class="edit-interests" @click="editInterests">
              <v-icon>mdi-pencil</v-icon>
              관심 기업 수정
            </button>
            <nav class="navbar">
              <button @click="goStocks">종목</button>
              <button @click="goNews">뉴스</button>
              <button @click="handleLogout">로그아웃</button>
            </nav>
          </div>
        </div>

        <div class="dashboard">
          <v-card class="dashboard-card">
            <v-card-title>오늘의 이슈</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item v-for="i in 3" :key="i">
                  <v-list-item-title>주요 이슈 {{ i }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card class="dashboard-card">
            <v-card-title>내 관심기업 뉴스 동향</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item v-for="i in 3" :key="i">
                  <v-list-item-title>뉴스 동향 {{ i }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card class="dashboard-card">
            <v-card-title>내 관심기업 주가</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item v-for="i in 3" :key="i" @click="goToStockDetail(userStocks[i-1])" link>
                  <v-list-item-title>기업 {{ i }} 주가</v-list-item-title>
                  <v-list-item-subtitle>현재가: ₩00,000</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>

          <v-card class="dashboard-card">
            <v-card-title>내 관심기업 관련 뉴스</v-card-title>
            <v-card-text>
              <v-list>
                <v-list-item v-for="i in 3" :key="i">
                  <v-list-item-title>관련 뉴스 {{ i }}</v-list-item-title>
                  <v-list-item-subtitle>뉴스 내용 요약</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-card-text>
          </v-card>
        </div>
      </div>
    </div>
  </v-container>
</template>

<style scoped>
.main {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: black;
  z-index: 1;
}

.background-video {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  z-index: 2;
  opacity: 0.2;
}

.content {
  position: relative;
  z-index: 3;
  width: 100%;
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

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

.dashboard {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  padding: 20px;
  overflow-y: auto;
}

.dashboard-card {
  background-color: rgba(0, 0, 0, 0.5) !important;
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

:deep(.v-card-title) {
  color: white;
  font-size: 1.2rem;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

:deep(.v-card-text) {
  color: rgba(255, 255, 255, 0.8);
}

:deep(.v-list) {
  background-color: transparent !important;
}

:deep(.v-list-item) {
  color: white !important;
}

:deep(.v-list-item-title) {
  color: white !important;
}

:deep(.v-list-item-subtitle) {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* 반응형 디자인 */
@media (max-width: 960px) {
  .dashboard {
    grid-template-columns: 1fr;
  }
}
</style>
