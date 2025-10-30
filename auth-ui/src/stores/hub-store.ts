// src/stores/hub-store.ts

import { defineStore } from 'pinia';
import { api } from 'src/boot/axios';

// Interface para definir a estrutura dos nossos KPIs
export interface HubKpis {
  activeVehicles: number;
  totalVehicles: number;
  monthlyCost: number;
  pendingMaintenances: number;
}

export const useHubStore = defineStore('hub', {
  state: () => ({
    // O estado inicial é sempre nulo, forçando o carregamento
    kpis: null as HubKpis | null,
    loading: false,
    error: null as string | null,
  }),

  getters: {
    // Getter para facilitar o acesso aos KPIs, com valores padrão seguros
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
  },

  actions: {
    // Ação para buscar os dados da API
    async fetchKpis() {
      // Evita múltiplas chamadas se já estiver carregando
      if (this.loading) return;

      this.loading = true;
      this.error = null;
      try {
        // --- Ponto Chave ---
        // Quando o backend do Hub estiver pronto, a chamada real e única será esta linha:
        // const response = await api.get('/api/v1/hub/kpis/trucar');
        // this.kpis = response.data;
        // -------------------

        // Simulação de chamada de API aprimorada
        await new Promise(resolve => setTimeout(resolve, 1500)); // Simula latência de rede

        // Simula uma falha aleatória para testar o estado de erro
        if (Math.random() > 0.9) {
          throw new Error('Falha simulada na rede');
        }

        // Dados que viriam da API
        this.kpis = {
          activeVehicles: 18,
          totalVehicles: 20,
          monthlyCost: 47850.30,
          pendingMaintenances: 3,
        };

      } catch (err) {
        this.error = 'Não foi possível carregar os indicadores da operação.';
        console.error('Erro ao buscar KPIs do Hub:', err);
        // Garante que os dados antigos sejam limpos em caso de erro
        this.kpis = null;
      } finally {
        this.loading = false;
      }
    },
  },
});
