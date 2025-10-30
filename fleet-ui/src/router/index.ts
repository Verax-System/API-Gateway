import { route } from 'quasar/wrappers';
import {
  createMemoryHistory,
  createRouter,
  createWebHistory,
  createWebHashHistory,
} from 'vue-router';
import routes from './routes';
import { useAuthStore } from 'src/stores/auth-store'; // Importe a store

export default route(function (/* { store, ssrContext } */) {
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

  // --- NOSSO GUARDA DE ROTA (FASE 2) ---
  Router.beforeEach((to, from, next) => {
    // Inicializa a auth store (Pinia)
    const authStore = useAuthStore();
    const isAuthenticated = authStore.isAuthenticated;

    // Rotas públicas que não exigem login
    const publicPaths = ['/login', '/register', '/forgot-password', '/reset-password'];
    const authRequired = !publicPaths.includes(to.path);

    if (authRequired && !isAuthenticated) {
      // O usuário não está logado e está tentando acessar uma página protegida
      // Redireciona para o HUB CENTRAL, passando a rota atual como 'redirect'
      // O '/fleet' é o VUE_ROUTER_BASE, que já é considerado pelo 'to.fullPath' se configurado no quasar.config.ts
      window.location.href = `http://localhost/login?redirect=${to.fullPath}`;
    } else if (!authRequired && isAuthenticated && publicPaths.includes(to.path)) {
      // Se usuário logado tentar acessar /login, redireciona para o dashboard
      next('/dashboard');
    } else {
      // O usuário está logado ou está acessando uma página pública
      next();
    }
  });
  // --- FIM DO GUARDA ---

  return Router;
});