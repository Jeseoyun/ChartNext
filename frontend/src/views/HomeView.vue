<template>
  <v-container fluid class="pa-0">
    <div class="home">
      <video autoplay loop muted playsinline class="background-video">
        <source src="@/assets/main_background.mp4" type="video/mp4" />
      </video>
      <div class="content">
        <LogoComponent />
        <NavBarComponent />
        <div class="text-content">
          <h1>Chart Next</h1>
          <p>RAG 기반 뉴스 추천 및 주가 예측 시스템</p>
          <button class="start-button" @click="goLogin">시작하기</button>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script>
import LogoComponent from '@/components/LogoComponent.vue';
import NavBarComponent from '@/components/NavBarComponent.vue';

export default {
  name: 'HomeView',
  components: {
    LogoComponent,
    NavBarComponent,
  },
  methods: {
    goLogin() {
      this.$router.push({ name: 'Login' });
    },
  },
};
</script>

<style scoped>
@font-face {
  font-family: 'AppleSDGothicNeoH';
  src: url('@/assets/fonts/AppleSDGothicNeoH.ttf') format('truetype');
}

@font-face {
  font-family: 'AppleSDGothicNeoB';
  src: url('@/assets/fonts/AppleSDGothicNeoB.ttf') format('truetype');
}

.home {
  position: relative;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: black;
  z-index: 1;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
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

.text-content h1 {
  font-size: 7rem;
  margin: 0;
  opacity: 0;
  transform: translateY(50px);
  animation: slideUp 0.8s ease forwards;
  font-family: 'AppleSDGothicNeoH', sans-serif;
}

.text-content p {
  font-size: 2rem;
  margin: -30px 10px 10px;
  opacity: 0;
  transform: translateY(50px);
  animation: slideUp 0.8s ease forwards;
  animation-delay: 0.3s;
  font-family: 'AppleSDGothicNeoB', sans-serif;
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
  font-family: 'AppleSDGothicNeoB', sans-serif;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  box-shadow: 0 0 10px rgba(123, 44, 181, 0.5);
  opacity: 0;
  transform: translateY(50px);
  animation: slideUp 0.8s ease forwards;
  animation-delay: 0.6s;
}

.start-button::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    45deg,
    transparent 0%,
    rgba(255, 255, 255, 0.3) 50%,
    transparent 100%
  );
  transform: rotate(45deg);
  transition: all 0.5s ease;
  opacity: 0;
}

.start-button:hover {
  box-shadow: 0 0 20px rgba(123, 44, 181, 0.8);
}

.start-button:hover::before {
  opacity: 1;
  animation: shine 1.5s infinite;
}

@keyframes slideUp {
  0% {
    opacity: 0;
    transform: translateY(50px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes shine {
  0% {
    transform: rotate(45deg) translateX(-200%);
  }
  100% {
    transform: rotate(45deg) translateX(200%);
  }
}

.v-container, .v-main, .v-application {
  padding: 0 !important;
  margin: 0 !important;
  border: none !important;
}
</style>
