import { defineStore } from 'pinia';
import apiClient from '@/api';

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
  }),
  actions: {
    async login(username, password) {
      try {
        const response = await apiClient.post('auth/login/', {
          username,
          password,
        });
        this.token = response.data.key;
        localStorage.setItem('token', this.token);
        apiClient.defaults.headers.common['Authorization'] = `Token ${this.token}`;
        // 사용자 정보 가져오기 등 추가 작업
      } catch (error) {
        console.error(error);
        throw error;
      }
    },
    logout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('token');
      delete apiClient.defaults.headers.common['Authorization'];
    },
  },
  getters: {
    isLoggedIn: (state) => !!state.token,
  },
}); 