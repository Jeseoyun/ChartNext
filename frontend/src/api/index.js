import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  withCredentials: false
});

// URL 끝에 슬래시 추가하는 인터셉터
apiClient.interceptors.request.use(
  request => {
    if (request.url.substr(-1) !== '/') {
      request.url = request.url + '/';
    }
    console.log('API Request:', request.method.toUpperCase(), request.url);
    return request;
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