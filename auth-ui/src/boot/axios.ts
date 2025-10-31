// auth-ui/src/boot/axios.ts

import { boot } from 'quasar/wrappers';
import axios, { AxiosInstance } from 'axios';
import { useAuthStore } from 'src/stores/auth-store';
import { LocalStorage, Notify } from 'quasar'; 

declare module '@vue/runtime-core' {
  interface ComponentCustomProperties {
    $api: AxiosInstance;
  }
}

const api = axios.create({
  baseURL: '',
});

export default boot(({ app, router }) => {
  const authStore = useAuthStore(); 

  api.interceptors.request.use((config) => {
    // Busca o token da store, se não, do LocalStorage (necessário no primeiro boot/reload)
    const token = authStore.token || LocalStorage.getItem('token'); 
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response) {
          // Trata Erro de Não Autorizado
          if (error.response.status === 401) {
            authStore.logout();
            // Redireciona via window.location para limpar o estado e recarregar
            window.location.href = '/login'; 
          }
          // NOVO: Trata Erro de Proibido (Permissão)
          if (error.response.status === 403) {
             Notify.create({ 
                 type: 'negative', 
                 message: 'Acesso Proibido. Você não tem permissão para esta ação.' 
             });
             // Opcional: Redirecionar para uma página de erro 403/proibido.
             // Se houver uma página /unauthorized, use `router.push('/unauthorized')`
          }
      }
      return Promise.reject(error);
    }
  );

  app.config.globalProperties.$api = api;
  authStore.router = router;
});

export { api };