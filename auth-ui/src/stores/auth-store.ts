import { defineStore } from 'pinia';
import { LocalStorage, Notify } from 'quasar';
import { api } from 'src/boot/axios';
import { User, LoginCredentials } from './hub-store'; //
import { Router } from 'vue-router'; // Importar Router

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: LocalStorage.getItem('token') as string | null,
    isAuthenticated: !!LocalStorage.getItem('token'),
    user: null as User | null,
    router: null as Router | null, // Para guardar a instância do router
  }),

  getters: {
    isSuperuser(state): boolean {
      return state.user?.is_superuser ?? false;
    },
  },

  actions: {
    // --- FUNÇÃO CORRIGIDA ---
    async login(loginData: LoginCredentials): Promise<boolean> {
      try {
        // 1. O backend (OAuth2PasswordRequestForm) espera 'username' e 'password'.
        // 2. Precisamos formatar os dados como x-www-form-urlencoded usando URLSearchParams.
        const params = new URLSearchParams();
        // Assumindo que LoginCredentials tem 'email' e 'password'.
        // Mapeamos 'email' (do UI) para 'username' (que a API espera).
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

        // --- INÍCIO DA CORREÇÃO DE REDIRECIONAMENTO (FASE 2) ---
        const urlParams = new URLSearchParams(window.location.search);
        const redirectUrl = urlParams.get('redirect');

        if (redirectUrl) {
          // Se houver um 'redirect' (ex: ?redirect=/fleet/)
          // Redireciona para a URL completa
          window.location.href = redirectUrl;
        } else {
          // Se não houver redirect, vai para o dashboard do Hub
          if (this.router) {
            this.router.push('/dashboard');
          } else {
            window.location.href = '/dashboard';
          }
        }
        // --- FIM DA CORREÇÃO ---

        return true; // Retorna sucesso

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
        return false; // Retorna falha
      }
    },

    async fetchUser(): Promise<void> {
      if (!this.token) return;
      try {
        const response = await api.get('/api/v1/users/me'); //
        this.user = response.data;
        this.isAuthenticated = true;
      } catch (error) {
        // Token pode ser inválido/expirado
        this.logout();
      }
    },

    logout() {
      this.token = null;
      this.user = null;
      this.isAuthenticated = false;
      LocalStorage.remove('token');
      delete api.defaults.headers.common['Authorization'];
      if (this.router) {
        this.router.push('/login');
      } else {
        window.location.href = '/login';
      }
    },
  },
});