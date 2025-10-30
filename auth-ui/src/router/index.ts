// src/router/index.ts

import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHashHistory,
  createWebHistory,
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from 'src/stores/auth-store';

export default route(function ({ store }) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  // A guarda de rota é a polícia de fronteira da sua aplicação.
  Router.beforeEach(async (to) => {
    const authStore = useAuthStore(store);

    // Essencial para recarregar a página e continuar logado.
    if (authStore.token && !authStore.user) {
      await authStore.fetchUser();
    }

    const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);

    // Se a rota exige login e o usuário NÃO está autenticado...
    if (requiresAuth && !authStore.isAuthenticated) {
      // ...redireciona para o login.
      return { path: '/login', query: { redirect: to.fullPath } };
    }
  });

  return Router;
});