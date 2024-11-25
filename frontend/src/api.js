import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // Django 서버 주소 확인
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 추가
apiClient.interceptors.request.use(
  config => {
    console.log('API Request:', config.method.toUpperCase(), config.url);
    return config;
  },
  error => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 추가
apiClient.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.data);
    return response;
  },
  error => {
    console.error('API Response Error:', error.response || error);
    return Promise.reject(error);
  }
);

export default apiClient; 