import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from 'src/stores/auth-store';
import { LocalStorage } from 'quasar'; // Importado para pegar o token inicial

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}

// CORRIGIDO: baseURL vazia, pois os stores já usam o caminho completo (ex: /api/v1/auth/token)
const api = axios.create({
  baseURL: '',
});

export default boot(({ app, router }) => {
  // Use 'pinia' para obter a store fora de um componente
  const authStore = useAuthStore(); 

  api.interceptors.request.use((config) => {
    // Tenta pegar o token da store, se não, do LocalStorage
    const token = authStore.token || LocalStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        authStore.logout();
        // Recarrega a página para o estado de login
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );

  app.config.globalProperties.$api = api;
  // Disponibiliza o router para a store de auth
  authStore.router = router;
});

export { api };