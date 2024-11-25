import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false
});

// URL 끝에 슬래시 추가하는 인터셉터
apiClient.interceptors.request.use(
  config => {
    // URL 끝에 슬래시 추가
    if (config.url.substr(-1) !== '/') {
      config.url = config.url + '/';
    }
    
    // 요청 로깅
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