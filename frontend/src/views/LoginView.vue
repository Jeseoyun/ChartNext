<template>
  <v-container fluid class="d-flex align-center justify-center login-signup-background">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" sm="6" md="4" lg="3">
        <LogoComponent />
        <div class="signup-card">
          <h2 class="text-center login-title">로그인</h2>
          <v-form @submit.prevent="handleLogin" ref="loginForm">
            <v-text-field
              v-model="username"
              label="아이디"
              required
              class="mb-3"
            ></v-text-field>
            <v-text-field
              v-model="password"
              label="비밀번호"
              type="password"
              required
            ></v-text-field>
            <v-btn type="submit" color="white" class="black--text w-100 mt-3">로그인</v-btn>
          </v-form>
          <p class="text-center mt-4">
            계정이 없으신가요? 
            <router-link to="/signup" class="bold-link">회원가입하기</router-link>
          </p>
          <div class="social-login text-center mt-4">
            <v-icon class="social-icon" @click="socialLogin('google')">mdi-google</v-icon>
            <v-icon class="social-icon" @click="socialLogin('kakao')">mdi-chat</v-icon>
            <v-icon class="social-icon" @click="socialLogin('naver')">mdi-web</v-icon>
          </div>
        </div>
        <div class="footer text-center">
          <p>
            <router-link to="/terms" class="footer-link">이용약관</router-link>
            <span class="footer-separator">|</span>
            <router-link to="/privacy" class="footer-link">개인정보처리방침</router-link>
          </p>
          <p class="copyright">© 2024 Chart Next. All rights reserved.</p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import LogoComponent from '@/components/LogoComponent.vue';
import { useUserStore } from '@/stores/user';

export default {
  name: 'LoginView',
  components: {
    LogoComponent,
  },
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
    socialLogin(provider) {
      if (provider === 'google') {
        gapi.load('auth2', () => {
          const auth2 = gapi.auth2.init({
            client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
            redirect_uri: 'http://localhost:8000/login/oauth2/code/google',
          });
          auth2.signIn().then(googleUser => {
            const id_token = googleUser.getAuthResponse().id_token;
            // 백엔드로 토큰 전송
            apiClient.post('/api/auth/google/', { token: id_token })
              .then(response => {
                // 로그인 성공 처리
                alert('로그인 성공');
              })
              .catch(error => {
                // 로그인 실패 처리
                alert('로그인 실패');
              });
          });
        });
      } else {
        alert(`${provider} 로그인 기능은 아직 구현되지 않았습니다.`);
      }
    },
  },
};
</script>

<style scoped>
.login-signup-background {
  background-image: url('@/assets/sign_background.jpg');
  background-size: cover;
  background-position: center;
}
.fill-height {
  min-height: 100vh;
}
.signup-card {
  background-color: rgba(0, 0, 0, 0.1);
  color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0px 0px 100px #6439ff60;
  backdrop-filter: blur(10px);
}
.logo {
  position: absolute;
  top: 0px;
  left: 20px;
  cursor: pointer;
}
.text-center {
  text-align: center;
  color: white;
}
.mb-3 {
  margin-bottom: 16px;
}
.mt-3 {
  margin-top: 12px;
}
.mt-4 {
  margin-top: 16px;
}
.footer {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  color: gray;
  text-align: center;
  z-index: 10;
  font-weight: normal;
}
.footer-link {
  color: gray;
  text-decoration: none;
  font-weight: normal;
}
.footer-separator {
  margin: 0 10px;
  color: gray;
}
.bold-link {
  font-weight: bold;
  text-decoration: none;
  color: white;
}
.social-login {
  display: flex;
  justify-content: center;
  gap: 20px;
}
.social-icon {
  font-size: 24px;
  cursor: pointer;
}
.copyright {
  font-weight: normal;
}
.login-title {
  margin-bottom: 40px;
}

/* 자동완성 스타일 제거 */
:deep(input:-webkit-autofill),
:deep(input:-webkit-autofill:hover),
:deep(input:-webkit-autofill:focus),
:deep(input:-webkit-autofill:active) {
  -webkit-box-shadow: 0 0 0 30px transparent inset !important;
  -webkit-text-fill-color: white !important;
  transition: background-color 5000s ease-in-out 0s;
  background-color: transparent !important;
}
</style> 