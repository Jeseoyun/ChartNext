<template>
  <v-container fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-form @submit.prevent="handleLogin" ref="loginForm">
          <v-text-field
            v-model="username"
            label="아이디"
            required
          ></v-text-field>
          <v-text-field
            v-model="password"
            label="비밀번호"
            type="password"
            required
          ></v-text-field>
          <v-btn type="submit" color="primary">로그인</v-btn>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { useUserStore } from '@/stores/user';

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
    };
  },
  setup() {
    const userStore = useUserStore();
    return { userStore };
  },
  methods: {
    async handleLogin() {
      try {
        await this.userStore.login(this.username, this.password);
        this.$router.push({ name: 'Home' });
      } catch (error) {
        console.error('로그인 실패:', error);
        // 에러 메시지 표시 등 추가 작업
      }
    },
  },
};
</script>

<style scoped>
/* 필요한 스타일을 추가합니다 */
</style> 