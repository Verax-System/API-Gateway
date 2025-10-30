// src/stores/auth-store.ts

import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import type { Router } from 'vue-router';

// A declaração do router para o Pinia é necessária para o logout
declare module 'pinia' {
  export interface PiniaCustomProperties {
    routes: Router;
  }
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  organization: {
    id: string;
    name: string;
  };
  roles: { id: number; name: string }[];
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: null as User | null,
  }),

  getters: {
    // A autenticação SÓ é verdadeira se tivermos o token E os dados do usuário.
    isAuthenticated: (state) => !!state.token && !!state.user,
  },

  actions: {
    // A função de login AGORA retorna um booleano: sucesso ou falha.
    async login(email: string, password: string): Promise<boolean> {
      try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const response = await api.post('/api/v1/auth/token', formData);
        const { access_token } = response.data;

        this.setToken(access_token);
        await this.fetchUser();

        // Se fetchUser não deu erro e temos um usuário, o login foi um sucesso.
        return this.user !== null;
      } catch (error) {
        console.error('Erro no processo de login na store:', error);
        this.clearAuthData();
        return false;
      }
    },

    async fetchUser() {
      if (!this.token) return;
      try {
        const response = await api.get('/api/v1/users/me');
        this.user = response.data;
      } catch (error) {
        console.error('Erro ao buscar usuário (token pode ser inválido).', error);
        // Se falhar, limpa os dados. O interceptor do axios cuidará do redirecionamento.
        this.clearAuthData();
      }
    },

    setToken(token: string) {
      this.token = token;
      localStorage.setItem('token', token);
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    },

    clearAuthData() {
      this.token = null;
      this.user = null;
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
    },

    logout() {
      this.clearAuthData();
      // O único redirecionamento que a store faz é no logout explícito.
      void this.router.push('/login');
    },
  },
});