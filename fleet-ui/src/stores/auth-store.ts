import { defineStore } from 'pinia';
import { LocalStorage, Notify } from 'quasar';
import api from 'src/services/api';
// CORREÇÃO: Usa import type e importa o UserProfile re-exportado
import type { UserProfile } from 'src/models/user-models'; 
// CORREÇÃO: Usa import type e importa os tipos corrigidos
import type { LoginCredentials, PasswordRecoveryRequest, PasswordResetData } from 'src/models/auth-models'; 

export interface AuthState {
  // CORRIGIDO: Propriedade renomeada para 'accessToken' para corresponder ao código original
  accessToken: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  // RESTAURADO: Propriedades que a aplicação esperava
  isImpersonating: boolean;
  originalAdminToken: string | null;
  router: any; // Para guardar a instância do router (manter 'any' ou usar 'Router')
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    // CORREÇÃO: Mantido 'as string | null' e corrigido nome para 'accessToken'
    accessToken: LocalStorage.getItem('token') as string | null,
    user: null,
    isAuthenticated: !!LocalStorage.getItem('token'),
    isImpersonating: LocalStorage.getItem('isImpersonating') === 'true',
    // CORREÇÃO: Mantido 'as string | null'
    originalAdminToken: LocalStorage.getItem('originalAdminToken') as string | null,
    router: null,
  }),

  getters: {
    // RESTAURADO: Getters que a aplicação esperava
    isManager: (state) => state.user?.is_manager || state.user?.is_superuser,
    isSuperuser: (state) => state.user?.is_superuser,
    isDriver: (state) => state.user?.role === 'motorista',
    isDemo: (state) => state.user?.organization?.is_demo ?? false,
    userSector: (state) => state.user?.organization?.sector ?? 'frete',
  },

  actions: {
    // CORREÇÃO: Adicionando de volta a ação 'login' (stub ou re-implementação)
    async login(credentials: LoginCredentials) {
      // NOTE: A lógica de login local foi removida.
      // Implementação stub para evitar erro de método não encontrado em LoginPage.vue
      console.warn(`Ação de login para ${credentials.email} desabilitada. O login deve ser tratado pelo Hub.`);
      throw new Error("Login local desabilitado. Por favor, use o Hub Central.");
      // Se fosse implementado o login local:
      // const response = await api.post<TokenData>('/auth/token', credentials);
      // this.setToken(response.data.access_token);
    },

    setToken(token: string) {
      this.accessToken = token;
      this.isAuthenticated = true;
      LocalStorage.set('token', token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },

    async fetchUser() {
      if (!this.accessToken) {
        this.isAuthenticated = false;
        return;
      }
      // Garante que o token está no cabeçalho da API
      api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
      try {
        const response = await api.get<UserProfile>('/users/me');
        this.user = response.data;
        this.isAuthenticated = true;
      } catch (e) { // CORREÇÃO: Renomeia 'error' para 'e' para evitar erro de 'unused'
        console.error('Failed to fetch user:', e);
        this.logoutAndRedirect(); // Token pode estar inválido
      }
    },

    // CORRIGIDO: Ação de logout agora redireciona para o Hub
    logoutAndRedirect() {
      this.accessToken = null;
      this.user = null;
      this.isAuthenticated = false;
      this.isImpersonating = false;
      this.originalAdminToken = null;
      LocalStorage.remove('token');
      LocalStorage.remove('isImpersonating');
      LocalStorage.remove('originalAdminToken');
      delete api.defaults.headers.common['Authorization'];
      
      // Redireciona para o login do Hub Central
      window.location.href = 'http://localhost/login';
    },

    // --- AÇÕES RESTAURADAS QUE A APLICAÇÃO ESPERA ---

    // CORRIGIDO: Tipagem da requisição corrigida (PasswordRecoveryRequest) e 'error' unused
    async requestPasswordReset(data: PasswordRecoveryRequest) {
      try {
        // CORRIGIDO: Tipagem resolvida pela importação de PasswordRecoveryRequest
        await api.post('http://localhost/api/v1/auth/password-recovery', data);
        Notify.create({
          type: 'positive',
          message: 'Se o e-mail estiver correto, você receberá um link para redefinir sua senha.',
        });
      } catch (e) { // CORREÇÃO: Renomeia 'error' para 'e' para evitar erro de 'unused'
        Notify.create({
          type: 'negative',
          message: 'Erro ao solicitar redefinição de senha.',
        });
      }
    },

    // CORRIGIDO: 'error' unused
    async resetPassword(data: PasswordResetData): Promise<boolean> {
      try {
        await api.post('http://localhost/api/v1/auth/reset-password', data);
        Notify.create({
          type: 'positive',
          message: 'Senha redefinida com sucesso! Você pode fazer o login.',
        });
        return true;
      } catch (e) { // CORREÇÃO: Renomeia 'error' para 'e' para evitar erro de 'unused'
        Notify.create({
          type: 'negative',
          message: 'Token inválido ou expirado. Tente novamente.',
        });
        return false;
      }
    },

    // CORRIGIDO: 'error' unused
    async updateMyPreferences(preferences: unknown) {
      if (!this.user) return;
      try {
        // Esta chamada ainda é local, para o /users/me do fleet-api
        const response = await api.put<UserProfile>('/users/me', { preferences });
        this.user = response.data;
        Notify.create({ type: 'positive', message: 'Preferências salvas' });
      } catch (e) { // CORREÇÃO: Renomeia 'error' para 'e' para evitar erro de 'unused'
        Notify.create({ type: 'negative', message: 'Erro ao salvar preferências' });
      }
    },

    // Lógica de personificação (Administrador entrando como outro usuário)
    startImpersonation(token: string, user: UserProfile) {
      this.originalAdminToken = this.accessToken;
      this.accessToken = token;
      this.user = user;
      this.isImpersonating = true;
      LocalStorage.set('token', this.accessToken);
      LocalStorage.set('originalAdminToken', this.originalAdminToken);
      LocalStorage.set('isImpersonating', 'true');
      api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
      window.location.href = '/fleet/'; // Recarrega a aplicação como o novo usuário
    },

    stopImpersonation() {
      if (!this.originalAdminToken) return;
      this.accessToken = this.originalAdminToken;
      this.isImpersonating = false;
      this.originalAdminToken = null;
      LocalStorage.set('token', this.accessToken);
      LocalStorage.remove('originalAdminToken');
      LocalStorage.remove('isImpersonating');
      api.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;
      // CORREÇÃO: Usando 'void' para evitar o erro de 'floating promise'
      void this.fetchUser(); 
      if (this.router) {
        // CORREÇÃO: Usando 'void' para evitar o erro de 'floating promise'
        void this.router.push('/admin');
      } else {
        window.location.href = '/fleet/admin'; // Volta para a página de admin
      }
    },
  },
});