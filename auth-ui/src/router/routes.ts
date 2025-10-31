// auth-ui/src/router/routes.ts

import type { RouteRecordRaw } from 'vue-router';

// NOVO: Grupo para rotas que não usam o MainLayout
const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    // Usa o Layout Simples que o QPage exige
    component: () => import('layouts/BlankLayout.vue'), 
    children: [
      // Mantenha o redirecionamento da raiz para o dashboard (após login)
      {
        path: '', 
        redirect: '/login', 
      },
      // Rotas Públicas (LoginPage, ForgotPasswordPage, etc.)
      {
        path: '/login',
        name: 'login', 
        component: () => import('pages/LoginPage.vue'),
      },

      {
        path: '/register',
        name: 'register',
        component: () => import('pages/RegisterPage.vue'),
      },
      
      {
        path: '/forgot-password',
        name: 'forgot-password',
        component: () => import('pages/ForgotPasswordPage.vue'), 
      },
      {
        path: '/reset-password',
        name: 'reset-password',
        component: () => import('pages/ResetPasswordPage.vue'), 
      },
      {
        path: '/verify-email/:token',
        name: 'verify-email',
        component: () => import('pages/VerifyEmailPage.vue'), 
      },
      {
        path: '/google-callback',
        name: 'google-callback',
        component: () => import('pages/GoogleCallbackPage.vue'),
      },
    ]
  }
];

const hubRoutes: RouteRecordRaw[] = [
  // --- ROTAS DO HUB (REQUER AUTENTICAÇÃO) ---
  {
    path: '/hub',
    // Continua usando o Layout principal
    component: () => import('layouts/MainLayout.vue'),
    meta: { requiresAuth: true }, // Protege rotas do Hub
    children: [
      { 
        path: 'dashboard', 
        name: 'dashboard', 
        component: () => import('pages/DashboardPage.vue') 
      },
      { 
        path: 'profile', 
        name: 'profile-settings', 
        component: () => import('pages/ProfileSettingsPage.vue') 
      },
      
      // --- ROTAS DE CONFIGURAÇÕES ANINHADAS ---
      { 
        path: 'settings', 
        component: () => import('pages/SettingsPage.vue'), 
        children: [
          { 
            path: '', 
            redirect: { name: 'security-settings' } 
          }, 
          { 
            path: 'security', 
            name: 'security-settings', 
            component: () => import('pages/SecuritySettingsPage.vue') 
          },
        ]
      },
    ],
  },
];

const errorRoute: RouteRecordRaw = {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
};

// Junta todas as rotas
const routes: RouteRecordRaw[] = [
  ...publicRoutes,
  ...hubRoutes,
  errorRoute,
];

export default routes;