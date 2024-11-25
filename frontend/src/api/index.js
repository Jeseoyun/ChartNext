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
apiClient.interceptors.request.use(request => {
  if (request.url.substr(-1) !== '/') {
    request.url = request.url + '/';
  }
  return request;
});

export default apiClient; 