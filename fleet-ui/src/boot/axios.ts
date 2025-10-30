import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from 'src/stores/auth-store';
import { LocalStorage } from 'quasar';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}

// CORRIGIDO: A baseURL deve ser /api/fleet
const api = axios.create({
  baseURL: '/api/fleet',
});

export default boot(({ app, store }) => {
  const authStore = useAuthStore(store);

  api.interceptors.request.use((config) => {
    // CORRIGIDO: Usa 'accessToken' (do auth-store) ou 'token' (do LocalStorage)
    const token = authStore.accessToken || LocalStorage.getItem('token');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        // Se não autorizado, chama a ação de logout
        authStore.logoutAndRedirect();
      }
      // eslint-disable-next-line @typescript-eslint/prefer-promise-reject-errors
      return Promise.reject(error);
    }
  );

  app.config.globalProperties.$api = api;
});

export { api };