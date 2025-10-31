import axios from 'axios';
import { useAuthStore } from 'src/stores/auth-store';
import { LocalStorage } from 'quasar'; // Importa LocalStorage

// Cria a instância principal do Axios
const api = axios.create({
  baseURL: '/api/fleet', //
});

// Adiciona um interceptor para injetar o token
api.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore();
    // CORREÇÃO: Tenta pegar da store (accessToken)
    const token = authStore.accessToken || LocalStorage.getItem('token'); 

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

// Adiciona um interceptor de resposta para lidar com 401 (deslogar)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const authStore = useAuthStore();
      authStore.logoutAndRedirect(); // Chama a ação de logout da store
    }
    // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
    return Promise.reject(error);
  }
);

export default api;