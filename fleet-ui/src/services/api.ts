import axios from 'axios';
import { useAuthStore } from 'src/stores/auth-store';

// Cria a instância principal do Axios
const api = axios.create({
  baseURL: '/api/fleet', // <-- CORRIGIDO (Caminho do Gateway)
});

// Adiciona um interceptor para injetar o token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    const token = authStore.token;

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
    return Promise.reject(error);
  }
);

// (Opcional, mas recomendado) Adiciona um interceptor de resposta para lidar com 401 (deslogar)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore();
      authStore.logout(); // Você precisará do store de auth aqui
      // Redireciona para o login (o ideal é fazer isso no router-guard)
      window.location.href = '/login'; 
    }
    // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
    return Promise.reject(error);
  }
);

export default api;