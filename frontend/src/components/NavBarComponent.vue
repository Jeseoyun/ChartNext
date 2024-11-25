<template>
  <nav class="navbar">
    <button @click="goStocks">종목</button>
    <button @click="goNews">뉴스</button>
    <button @click="goLogin">로그인</button>
  </nav>
</template>

<script>
export default {
  name: 'NavBarComponent',
  methods: {
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