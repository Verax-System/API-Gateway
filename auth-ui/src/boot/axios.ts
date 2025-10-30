import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from 'src/stores/auth-store';

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}

// CORREÇÃO: O baseURL deve ser vazio.
// O frontend já usa os caminhos completos (ex: /api/v1/auth/token)
const api = axios.create({
  baseURL: '', // <-- CORRIGIDO AQUI
});

export default boot(({ app, router }) => {
  const authStore = useAuthStore();

  api.interceptors.request.use((config) => {
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`;
    }
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        authStore.logout();
        router.push('/login');
      }
      return Promise.reject(error);
    }
  );

  app.config.globalProperties.$api = api;
});

export { api };