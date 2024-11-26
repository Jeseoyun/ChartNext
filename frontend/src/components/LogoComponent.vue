<template>
  <div class="logo">
    <img src="@/assets/logo.png" alt="Logo" @click="goHome" class="logo-image" />
  </div>
</template>

<script>
import { useUserStore } from '@/stores/user';

export default {
  name: 'LogoComponent',
  methods: {
    goHome() {
      const userStore = useUserStore();
      if (userStore.isLoggedIn) {
        this.$router.push({ name: 'Main' });
      } else {
        this.$router.push({ name: 'Home' });
      }
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