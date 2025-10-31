// src/stores/hub-store.ts

import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';
import type { UserProfile } from './auth-store'; // Importa a interface do usuário (assumindo que está em auth-store.ts)

// --- NOVAS INTERFACES E CONFIGURAÇÃO ---
interface HubApp {
  title: string;
  caption: string;
  icon: string; // Quasar/MDI icon name
  route: string; // Ex: 'fleet' ou 'sales' (subcaminho do Nginx)
  allowed_roles: string[]; // Quais roles podem ver este app
}
// --- FIM NOVAS INTERFACES ---

export interface HubKpis {
  activeVehicles: number;
  totalVehicles: number;
  monthlyCost: number;
  pendingMaintenances: number;
}

export interface HubState {
  kpis: HubKpis | null;
  loading: boolean;
  error: string | null;
  availableApps: HubApp[]; // ADICIONADO: Lista de aplicativos setoriais
}


export const useHubStore = defineStore('hub', {
  state: (): HubState => ({
    kpis: null,
    loading: false,
    error: null,
    // ADICIONADO: Configuração MOCK dos aplicativos setoriais
    availableApps: [
      {
        title: 'Gestão de Frota',
        caption: 'TruCar (Caminhões e Frotas)',
        icon: 'local_shipping',
        route: 'fleet', // Rota do Nginx
        allowed_roles: ['admin', 'manager', 'motorista'],
      },
      {
        title: 'Gestão de Vendas',
        caption: 'VrSales (PDV e Estoque)',
        icon: 'point_of_sale',
        route: 'sales', // Rota do Nginx
        allowed_roles: ['admin', 'manager', 'vendedor'],
      },
      // Adicione mais aplicações conforme o projeto cresce
    ],
  }),

  getters: {
    getKpis: (state): HubKpis => {
      return (
        state.kpis ?? {
          activeVehicles: 0,
          totalVehicles: 0,
          monthlyCost: 0,
          pendingMaintenances: 0,
        }
      );
    },
    // NOVO GETTER: Filtra apps com base no papel do usuário
    getFilteredApps: (state) => (user: UserProfile | null): HubApp[] => {
        if (!user) return [];
        
        return state.availableApps.filter(app => {
            // Se o usuário for Superuser, ele vê todos os aplicativos
            if (user.is_superuser) return true;
            // Caso contrário, filtra pelo papel do usuário
            return app.allowed_roles.includes(user.role);
        });
    }
  },

  actions: {
    async fetchKpis() {
      if (this.loading) return;

      this.loading = true;
      this.error = null;
      try {
        await new Promise(resolve => setTimeout(resolve, 1500)); 

        if (Math.random() > 0.9) {
          throw new Error('Falha simulada na rede');
        }

        this.kpis = {
          activeVehicles: 18,
          totalVehicles: 20,
          monthlyCost: 47850.30,
          pendingMaintenances: 3,
        };

      } catch (err) {
        this.error = 'Não foi possível carregar os indicadores da operação.';
        console.error('Erro ao buscar KPIs do Hub:', err);
        this.kpis = null;
      } finally {
        this.loading = false;
      }
    },
  },
});