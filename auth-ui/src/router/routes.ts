// src/router/routes.ts

import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    // Redireciona a raiz para o /hub/dashboard
    redirect: '/hub/dashboard',
  },
  
  // Rota de Login (Pública)
  {
    path: '/login',
    name: 'login', 
    component: () => import('pages/LoginPage.vue'),
  },
  
  // --- ROTAS DO HUB (REQUER AUTENTICAÇÃO) ---
  {
    path: '/hub',
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true }, // Protege rotas do Hub
    children: [
      { 
        path: 'dashboard', 
        name: 'dashboard', 
        component: () => import('pages/DashboardPage.vue') 
      },
      // ROTAS DE USUÁRIOS REMOVIDAS: users, users/:id
      // Se você precisar delas no futuro, crie os arquivos UsersPage.vue e UserDetailsPage.vue
      
      // --- ROTAS DE CONFIGURAÇÕES ANINHADAS ---
      { 
        path: 'settings', 
        // Assumindo que SettingsPage.vue é o componente de layout/navegação lateral (que você precisará criar)
        component: () => import('pages/SettingsPage.vue'), 
        children: [
          { 
            path: '', 
            redirect: { name: 'security-settings' } 
          }, 
          { 
            path: 'security', 
            name: 'security-settings', 
            // Assumindo que SecuritySettingsPage.vue é a página de 2FA (que você precisará criar)
            component: () => import('pages/SecuritySettingsPage.vue') 
          },
        ]
      },
      // --- FIM NOVAS ROTAS ---

    ],
  },
  // --- FIM ROTAS DO HUB ---

  // Rota de Erro 404
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;