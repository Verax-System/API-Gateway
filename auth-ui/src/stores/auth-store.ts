// auth-ui/src/stores/auth-store.ts

import { defineStore } from 'pinia';
import { LocalStorage, Notify } from 'quasar';
import { api } from 'src/boot/axios';
import type { Router } from 'vue-router';

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

// Resposta de MFA Start
export interface MFAEnrollmentResponse {
    secret: string;
    qr_code_base64: string; // O backend retornou base64
}

// Resposta de MFA Confirm
export interface MFAConfirmResponse {
    user: UserProfile;
    recovery_codes: string[];
}


// --- FIM MODELOS ESSENCIAIS ---


export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: LocalStorage.getItem('token') as string | null,
    // NOVO: Adiciona refresh_token ao estado e LocalStorage
    refreshToken: LocalStorage.getItem('refresh_token') as string | null,
    isAuthenticated: !!LocalStorage.getItem('token'),
    user: null as UserProfile | null,
    router: null as Router | null,
  }),

  getters: {
    isSuperuser(state): boolean {
      return state.user?.is_superuser ?? false;
    },
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

        // CORREÇÃO: Captura ambos os tokens
        const { access_token, refresh_token } = response.data;
        
        this.token = access_token;
        this.refreshToken = refresh_token;
        this.isAuthenticated = true;
        
        LocalStorage.set('token', access_token);
        // SALVA O REFRESH TOKEN
        LocalStorage.set('refresh_token', refresh_token);
        
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

        await this.fetchUser();

        const urlParams = new URLSearchParams(window.location.search);
        const redirectUrl = urlParams.get('redirect');

        if (redirectUrl) {
          window.location.href = redirectUrl;
        } else {
          if (this.router) {
            void this.router.push({ path: '/hub/dashboard' }); 
          } else {
            window.location.href = '/hub/dashboard';
          }
        }
        return true; 
      } catch (error) {
        this.isAuthenticated = false;
        this.token = null;
        this.refreshToken = null; // Limpa o refresh token em caso de falha
        this.user = null;
        LocalStorage.remove('token');
        LocalStorage.remove('refresh_token'); // Limpa o refresh token
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

    async logout() {
      const refreshToken = this.refreshToken || LocalStorage.getItem('refresh_token');
      
      // CHAMA O ENDPOINT DE LOGOUT NA API PARA REVOGAR O REFRESH TOKEN
      if (refreshToken) {
        try {
          await api.post('/api/v1/auth/logout', { refresh_token: refreshToken });
        } catch (error) {
          console.warn('Falha ao encerrar sessão no servidor, prosseguindo com logout local.', error);
          // Continua o logoff local mesmo se o servidor falhar
        }
      }

      // Limpeza local COMPLETA
      this.token = null;
      this.refreshToken = null;
      this.user = null;
      this.isAuthenticated = false;
      LocalStorage.remove('token');
      LocalStorage.remove('refresh_token');
      delete api.defaults.headers.common['Authorization'];
      
      if (this.router) {
        void this.router.push('/login');
      } else {
        window.location.href = '/login';
      }
    },

    async forgotPassword(email: string): Promise<void> {
      await api.post('/api/v1/auth/forgot-password', { email });
      Notify.create({
        type: 'positive',
        message: 'Se o email estiver registrado, um link para redefinição de senha foi enviado.',
      });
    },

    async resetPassword(token: string, new_password: string): Promise<void> {
      await api.post('/api/v1/auth/reset-password', { token, new_password });
      Notify.create({
        type: 'positive',
        message: 'Senha redefinida com sucesso. Você pode fazer login agora.',
      });
    },

    async verifyEmail(token: string): Promise<UserProfile> {
        const response = await api.get(`/api/v1/auth/verify-email/${token}`);
        Notify.create({
            type: 'positive',
            message: 'Email verificado com sucesso!',
        });
        return response.data;
    },

    // --- FUNÇÕES DE PERFIL E SEGURANÇA (MFA) ---

    async updateUserProfile(data: ProfileUpdateData): Promise<void> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        
        const dataToSend = Object.fromEntries(
            Object.entries(data).filter(([_, v]) => v !== null && v !== undefined && v !== '')
        );

        await api.put('/api/v1/users/me', dataToSend);
        
        await this.fetchUser();
        Notify.create({ type: 'positive', message: 'Perfil atualizado com sucesso!' });
    },


    async startMFAEnrollment(): Promise<MFAEnrollmentResponse> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");

        const response = await api.post('/api/v1/auth/mfa/enable');
        // O QR code vem em base64 (string)
        return response.data;
    },

    async confirmMFA(otp_code: string): Promise<MFAConfirmResponse> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        
        const response = await api.post('/api/v1/auth/mfa/confirm', { otp_code });

        // Se bem-sucedido, atualiza o status local
        await this.fetchUser(); 
        Notify.create({ type: 'positive', message: 'Autenticação de dois fatores ativada.' });
        return response.data; // Retorna user e recovery_codes
    },

    async disableMFA(otp_code: string): Promise<boolean> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        
        await api.post('/api/v1/auth/mfa/disable', { otp_code });

        // Atualiza o status local
        await this.fetchUser();
        Notify.create({ type: 'positive', message: 'Autenticação de dois fatores desativada.' });
        return true;
    },

    // --- FUNÇÕES DE GESTÃO DE SESSÃO/DISPOSITIVOS ---

    // Modelo de TrustedDeviceInfo é necessário aqui, mas para simplicidade, usamos 'any' ou criamos uma interface local.
    async fetchActiveSessions(): Promise<any[]> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        const response = await api.get('/api/v1/auth/sessions');
        return response.data;
    },

    async logoutSpecificSession(sessionId: number): Promise<void> {
        if (!this.isLoggedIn) throw new Error("Usuário não autenticado.");
        await api.delete(`/api/v1/auth/sessions/${sessionId}`);
        Notify.create({ type: 'positive', message: 'Sessão encerrada com sucesso.' });
    },

    async logoutAllOtherSessions(): Promise<void> {
        if (!this.isLoggedIn || !this.refreshToken) throw new Error("Usuário não autenticado.");
        // Usa o endpoint que exclui todas exceto o token enviado
        await api.post('/api/v1/auth/sessions/all-except-current', { 
            refresh_token: this.refreshToken 
        });
        Notify.create({ type: 'positive', message: 'Todas as outras sessões foram encerradas.' });
    },
  },
});