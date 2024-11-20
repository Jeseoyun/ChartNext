<template>
  <v-container fluid class="pa-0">
    <div class="home">
      <video autoplay loop muted playsinline class="background-video">
        <source src="@/assets/main_background.mp4" type="video/mp4" />
      </video>
      <div class="content">
        <img src="@/assets/logo.png" alt="Logo" class="logo" @click="goHome" />
        <div class="text-content">
          <h1>Chart Next</h1>
          <p>RAG 기반 뉴스 추천 및 주가 예측 시스템</p>
          <button class="start-button" @click="goLogin">시작하기</button>
        </div>
        <nav class="navbar">
          <button @click="goStocks">종목</button>
          <button @click="goNews">뉴스</button>
          <button @click="goLogin">로그인</button>
        </nav>
      </div>
    </div>
  </v-container>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    goHome() {
      this.$router.push({ name: 'Home' });
    },
    goStocks() {
      this.$router.push({ name: 'Interests' });
    },
    goNews() {
      this.$router.push({ name: 'News' });
    },
    goLogin() {
      this.$router.push({ name: 'Login' });
    },
  },
};
</script>

<style scoped>
@font-face {
  font-family: 'GmarketSansBold';
  src: url('@/assets/fonts/GmarketSansTTFBold.ttf') format('truetype');
}

@font-face {
  font-family: 'GmarketSansMedium';
  src: url('@/assets/fonts/GmarketSansTTFMedium.ttf') format('truetype');
}

.home {
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
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  height: 100%;
  color: white;
  text-align: left;
  padding-left: 300px;
  font-family: 'GmarketSansBold', sans-serif;
}

.logo {
  position: absolute;
  top: 0px;
  left: 20px;
  cursor: pointer;
}

.text-content h1 {
  font-size: 6rem;
  margin: 0;
}

.text-content p {
  font-size: 2rem;
  margin: -30px 10px 10px;
}

.start-button {
  margin-top: 20px;
  padding: 20px 40px;
  background: linear-gradient(90deg, #4131b1, #7a2cb5);
  border: none;
  border-radius: 50px;
  color: white;
  font-size: 2rem;
  cursor: pointer;
  font-family: 'GmarketSansMedium', sans-serif;
}

.navbar {
  position: absolute;
  top: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 20px;
  font-family: 'GmarketSansMedium', sans-serif;
}

.navbar button {
  background: transparent;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
}

.v-container, .v-main, .v-application {
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
}
</style>
