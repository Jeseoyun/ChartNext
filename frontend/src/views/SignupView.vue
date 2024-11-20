<template>
  <v-container fluid class="d-flex align-center justify-center login-signup-background">
    <v-row align="center" justify="center" class="fill-height">
      <v-col cols="12" sm="6" md="4" lg="3">
        <div class="logo">
          <img src="@/assets/logo.png" alt="Logo" @click="goToHome" />
        </div>
        <div class="signup-card">
          <h2 class="text-center">회원가입</h2>
          <p class="text-center welcome-message">Chart Next에 오신 것을 환영합니다</p>
          <v-form @submit.prevent="handleSignup">
            <v-text-field
              v-model="username"
              label="아이디"
              required
              class="mb-3"
            ></v-text-field>
            <p class="password-info">8자 이상, 숫자 및 특수문자 포함</p>
            <v-text-field
              v-model="password1"
              label="비밀번호"
              type="password"
              required
              @input="checkPasswordStrength"
              :error-messages="passwordErrors"
              class="mb-3"
            ></v-text-field>
            <v-text-field
              v-model="password2"
              label="비밀번호 확인"
              type="password"
              required
              class="mb-3"
            ></v-text-field>
            <div v-if="passwordStrength" :class="['password-strength', passwordStrengthClass]">
              <p>비밀번호 안전성: {{ passwordStrength }}</p>
            </div>
            <v-btn type="submit" color="white" class="black--text w-100 mt-3">가입하기</v-btn>
          </v-form>
          <p class="text-center mt-4">
            이미 계정이 있으신가요? 
            <router-link to="/login" class="bold-link">로그인하기</router-link>
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
          <p>© 2024 Chart Next. All rights reserved.</p>
        </div>
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
      passwordStrength: '',
      passwordErrors: [],
    };
  },
  computed: {
    passwordStrengthClass() {
      switch (this.passwordStrength) {
        case '강함':
          return 'strong';
        case '보통':
          return 'medium';
        case '약함':
          return 'weak';
        default:
          return '';
      }
    },
  },
  methods: {
    checkPasswordStrength() {
      const password = this.password1;
      this.passwordErrors = [];
      if (password.length < 8) {
        this.passwordErrors.push('비밀번호는 소 8자 이상이어야 합니다.');
      }
      if (!/\d/.test(password)) {
        this.passwordErrors.push('비번호에는 숫자가 포함되어야 합니다.');
      }
      if (!/[!@#$%^&*]/.test(password)) {
        this.passwordErrors.push('비밀번호에는 특수문자가 포함되어야 합니다.');
      }
      this.passwordStrength = this.calculatePasswordStrength(password);
    },
    calculatePasswordStrength(password) {
      if (password.length >= 8 && /\d/.test(password) && /[!@#$%^&*]/.test(password)) {
        return '강함';
      } else if (password.length >= 6) {
        return '보통';
      } else {
        return '약함';
      }
    },
    async handleSignup() {
      if (this.password1 !== this.password2) {
        alert('비밀번호가 일치지 않습니다.');
        return;
      }
      if (this.passwordErrors.length > 0) {
        alert('비밀번호가 안전하지 않습니다. 조건을 확인하세요.');
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
        alert(`회원가입에 실패하였습니다: ${error.response?.data?.detail || '알 수 없는 오류'}`);
      }
    },
    socialLogin(provider) {
      if (provider === 'google') {
        gapi.load('auth2', async () => {
          try {
            let auth2 = gapi.auth2.getAuthInstance();
            
            if (!auth2) {
              auth2 = await gapi.auth2.init({
                client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
                cookiepolicy: 'single_host_origin',
                scope: 'profile email',
                hosted_domain: 'localhost',
                redirect_uri: 'http://localhost:8000/accounts/google/login/callback/'
              });
            }

            const googleUser = await auth2.signIn({
              prompt: 'select_account'
            });
            const id_token = googleUser.getAuthResponse().id_token;
            
            try {
              const response = await apiClient.post('/accounts/google/login/', { 
                access_token: id_token 
              });
              console.log('Google 로그인 성공:', response);
              this.$router.push({ name: 'Home' });
            } catch (error) {
              console.error('Google 로그인 에러:', error);
              alert('로그인 실패: ' + (error.response?.data?.detail || error.message));
            }
          } catch (error) {
            console.error('Google 인증 에러:', error);
            alert('Google 인증 실패: ' + error.message);
          }
        });
      } else {
        alert(`${provider} 로그인 기능은 아직 구현되지 않았습니다.`);
      }
    },
    goToHome() {
      this.$router.push({ name: 'Home' });
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
  box-shadow: 0px 0px 200px #6439ff60;
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
.welcome-message {
  margin-bottom: 20px;
  color: white;
}
.mb-3 {
  margin-bottom: 16px;
}
.password-info {
  margin-bottom: 10px;
  color: gray;
  font-size: 0.9em;
}
.password-strength {
  margin-top: 10px;
  padding: 5px;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}
.strong {
  background-color: #d4edda;
  color: #155724;
}
.medium {
  background-color: #fff3cd;
  color: #856404;
}
.weak {
  background-color: #f8d7da;
  color: #721c24;
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
}
.footer-link {
  color: gray;
  text-decoration: none;
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