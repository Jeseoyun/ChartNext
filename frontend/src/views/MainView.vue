<template>
  <div>
    <!-- 상단 로고 및 네비게이션 바 -->
    <header>
      <div class="logo">
        <!-- 로고 이미지 또는 텍스트 -->
        <img src="@/assets/logo.png" alt="Logo" />
      </div>
      <nav>
        <ul>
          <li><a href="#stocks">종목</a></li>
          <li><a href="#news">뉴스</a></li>
          <li><a href="#logout">로그아웃</a></li>
        </ul>
      </nav>
    </header>

    <!-- 메인 대시보드 -->
    <main>
      <h1>대시보드</h1>
      <!-- 대시보드 내용 추가 -->
    </main>
  </div>
</template>

<script>
import { onMounted } from 'vue'; // 수정: vue에서 onMounted 가져오기
import { useRouter } from 'vue-router'; // vue-router에서 useRouter 가져오기
import apiClient from '@/api'; // API 클라이언트 임포트

export default {
  name: 'MainView',
  setup() {
    const router = useRouter();

    const checkUserStocks = async () => {
      try {
        const response = await apiClient.get('/stocks/user-stocks/');
        if (response.data.length === 0) {
          alert('관심 주식이 없습니다. 초기 설정 페이지로 이동합니다.');
          router.push({ name: 'UserInit' });
        }
      } catch (error) {
        console.error('관심 주식 조회 실패:', error);
      }
    };

    onMounted(() => {
      checkUserStocks();
    });

    return {};
  },
};
</script>

<style scoped>
/* 스타일 추가 */
header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f8f9fa;
}

.logo img {
  height: 40px;
}

nav ul {
  list-style: none;
  display: flex;
  gap: 20px;
}

nav a {
  text-decoration: none;
  color: #333;
}

main {
  padding: 20px;
}
</style>
