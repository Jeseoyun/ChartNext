<template>
  <v-container fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-form @submit.prevent="handleSignup">
          <v-text-field
            v-model="username"
            label="아이디"
            required
          ></v-text-field>
          <v-text-field
            v-model="password1"
            label="비밀번호"
            type="password"
            required
          ></v-text-field>
          <v-text-field
            v-model="password2"
            label="비밀번호 확인"
            type="password"
            required
          ></v-text-field>
          <v-btn type="submit" color="primary">회원가입</v-btn>
        </v-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import apiClient from '@/api';

export default {
  name: 'SignupView',
  data() {
    return {
      username: '',
      password1: '',
      password2: '',
    };
  },
  methods: {
    async handleSignup() {
      if (this.password1 !== this.password2) {
        alert('비밀번호가 일치하지 않습니다.');
        return;
      }
      try {
        const signupData = {
          username: this.username,
          password1: this.password1,
          password2: this.password2,
          email: `${this.username}@example.com`
        };
        
        console.log('회원가입 시도:', signupData);
        
        const response = await apiClient.post('/auth/registration/', signupData);
        
        console.log('회원가입 응답:', response.data);
        alert('회원가입이 완료되었습니다.');
        this.$router.push({ name: 'Login' });
      } catch (error) {
        console.error('회원가입 실패 상세:', {
          error: error,
          response: error.response,
          status: error.response?.status,
          data: error.response?.data,
          message: error.message,
          url: error.config?.url
        });
        alert('회원가입에 실패하였습니다. 콘솔을 확인해주세요.');
      }
    },
  },
};
</script>

<style scoped>
/* 필요한 스타일을 추가합니다 */
</style> 