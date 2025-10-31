import { defineStore } from 'pinia';
import { LocalStorage, Notify } from 'quasar';
import { api } from 'src/boot/axios';
import type { Router } from 'vue-router'; // Importar Router

// --- MODELOS ESSENCIAIS DEFINIDOS LOCALMENTE PARA EVITAR DEPENDÊNCIAS CIRCULARES ---

// Tipagem básica para o usuário do Hub (mestre)
export interface UserProfile {
  id: number;
  full_name: string;
  email: string;
  role: string; // Ex: 'admin', 'user', etc.
  is_active: boolean;
  is_superuser: boolean;
  avatar_url?: string | null;
  // Campos de segurança da API de Auth
  is_mfa_enabled: boolean;
  // Adicione outros campos necessários
}

// Credenciais de Login
export interface LoginCredentials {
  email: string;
  password: string;
}

// Dados para atualização de perfil
export interface ProfileUpdateData {
  full_name?: string;
  email?: string;
  current_password?: string;
  new_password?: string;
}

// --- FIM MODELOS ESSENCIAIS ---


export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: LocalStorage.getItem('token') as string | null,
    isAuthenticated: !!LocalStorage.getItem('token'),
    user: null as UserProfile | null, // Usando a nova interface UserProfile
    router: null as Router | null, // Para guardar a instância do router
  }),

  getters: {
    isSuperuser(state): boolean {
      return state.user?.is_superuser ?? false;
    },
    // Getter para verificar se a API de segurança está sendo chamada de forma correta
    isLoggedIn(state): boolean {
      return state.isAuthenticated && !!state.token;
    }
  },

  actions: {
    // --- FUNÇÕES DE AUTENTICAÇÃO ---
    async login(loginData: LoginCredentials): Promise<boolean> {
      try {
        const params = new URLSearchParams();
        params.append('username', loginData.email); 
        params.append('password', loginData.password);

        const response = await api.post('/api/v1/auth/token', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        const { access_token } = response.data;
        this.token = access_token;
        this.isAuthenticated = true;
        LocalStorage.set('token', access_token);
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        await this.fetchUser();

        // --- CORREÇÃO DE REDIRECIONAMENTO (Usando o prefixo /hub/) ---
        const urlParams = new URLSearchParams(window.location.search);
        const redirectUrl = urlParams.get('redirect');

        if (redirectUrl) {
          // Se houver um 'redirect' (ex: ?redirect=/fleet/), redireciona para a URL completa
          window.location.href = redirectUrl;
        } else {
          // Se não houver redirect, vai para o dashboard do Hub
          if (this.router) {
            // CORRIGIDO: Redireciona para a rota correta do Pinia/Vue Router
            void this.router.push({ path: '/hub/dashboard' }); 
          } else {
            // Fallback para hard redirect
            window.location.href = '/hub/dashboard';
          }
        }
        // --- FIM DA CORREÇÃO ---

        return true; 
      } catch (error) {
        this.isAuthenticated = false;
        this.token = null;
        this.user = null;
        LocalStorage.remove('token');
        delete api.defaults.headers.common['Authorization'];
        Notify.create({
          type: 'negative',
          message: 'Login ou senha inválidos.',
        });
        return false; 
      }
    },

    async fetchUser(): Promise<void> {
      if (!this.token) return;
      try {
        const response = await api.get('/api/v1/users/me'); 
        this.user = response.data;
        this.isAuthenticated = true;
      } catch (error) {
        this.logout();
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      this.isAuthenticated = false;
      LocalStorage.remove('token');
      delete api.defaults.headers.common['Authorization'];
      // CORRIGIDO: Garante que o redirecionamento é para a página de login raiz
      if (this.router) {
        void this.router.push('/login');
      } else {
        window.location.href = '/login';
      }
    },

    // --- FUNÇÕES DE PERFIL E SEGURANÇA (MFA) ---

    async updateUserProfile(data: ProfileUpdateData): Promise<void> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        
        // Remove campos vazios para evitar erros na API
        const dataToSend = Object.fromEntries(
            Object.entries(data).filter(([_, v]) => v !== null && v !== undefined && v !== '')
        );

        // Chamada da rota PUT /users/me do Auth API
        await api.put('/api/v1/users/me', dataToSend);
        
        // Atualiza os dados locais do usuário
        await this.fetchUser();
        Notify.create({ type: 'positive', message: 'Perfil atualizado com sucesso!' });
    },


    async startMFAEnrollment(): Promise<{ secret: string; qr_code_url: string }> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");

        // Rota para iniciar o MFA
        const response = await api.post('/api/v1/auth/mfa/enroll');
        return response.data; // Deve retornar { secret, qr_code_url }
    },

    async verifyAndEnableMFA(secret: string, code: string): Promise<boolean> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        
        // Rota para finalizar a ativação do MFA
        await api.post('/api/v1/auth/mfa/verify', { secret, code });

        // Se bem-sucedido, atualiza o status local
        await this.fetchUser(); 
        Notify.create({ type: 'positive', message: 'Autenticação de dois fatores ativada.' });
        return true;
    },

    async disableMFA(): Promise<boolean> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        
        // Rota para desativar o MFA
        await api.post('/api/v1/auth/mfa/disable');

        // Atualiza o status local
        await this.fetchUser();
        Notify.create({ type: 'positive', message: 'Autenticação de dois fatores desativada.' });
        return true;
    },
  },
});