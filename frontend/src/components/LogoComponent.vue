<template>
  <div class="logo">
    <img src="@/assets/logo.png" alt="Logo" @click="goHome" class="logo-image" />
  </div>
</template>

<script>
export default {
  name: 'LogoComponent',
  methods: {
    goHome() {
      this.$router.push({ name: 'Home' });
    },
  },
};
</script>

<style scoped>
.logo {
  position: absolute;
  top: 0px;
  left: 20px;
  cursor: pointer;
  z-index: 1000;
}

.logo-image {
  height: 80px;
  width: auto;
}
</style> 