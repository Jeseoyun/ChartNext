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
export default {
  name: 'MainView',
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
