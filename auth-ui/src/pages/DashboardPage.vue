<template>
  <q-page padding class="dashboard-page">
    <!-- Mensagem de Boas-vindas -->
    <div class="welcome-message q-mb-lg">
      <h4 class="text-weight-bold no-margin">
        Olá, {{ authStore.user?.full_name?.split(' ')[0] }}! 👋
      </h4>
      <p class="text-grey-6">Aqui está o resumo da sua operação hoje.</p>
    </div>

    <!-- Banner de Erro -->
    <q-banner v-if="hubStore.error" inline-actions rounded class="bg-red-4 text-white q-mb-lg">
      <template v-slot:avatar>
        <q-icon name="warning" />
      </template>
      {{ hubStore.error }}
      <template v-slot:action>
        <q-btn flat label="Tentar Novamente" @click="hubStore.fetchKpis" :loading="hubStore.loading" />
      </template>
    </q-banner>

    <!-- Seção de KPIs -->
    <div class="row q-col-gutter-md q-mb-lg">
      <template v-if="hubStore.loading">
        <!-- Esqueletos de Carregamento -->
        <div v-for="i in 4" :key="i" class="col-12 col-sm-6 col-md-3">
          <q-card class="kpi-card text-center" flat>
            <q-card-section>
              <q-skeleton type="QAvatar" size="40px" />
              <q-skeleton type="text" class="text-h6 q-mt-md" width="60%" />
              <q-skeleton type="text" class="text-caption q-mt-sm" width="40%" />
            </q-card-section>
          </q-card>
        </div>
      </template>
      <template v-else-if="hubStore.kpis">
        <!-- Cards de KPI Reais -->
        <!-- Veículos Ativos -->
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="kpi-card text-center kpi-card--blue" flat>
            <q-card-section>
              <q-icon name="directions_car" size="lg" color="blue-4" />
              <div class="text-h5 text-weight-bolder q-mt-sm">
                {{ hubStore.getKpis.activeVehicles }}
                <span class="text-h6 text-weight-light">/ {{ hubStore.getKpis.totalVehicles }}</span>
              </div>
              <div class="text-caption text-grey-5">Veículos Ativos</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Custo Total -->
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="kpi-card text-center kpi-card--green" flat>
            <q-card-section>
              <q-icon name="attach_money" size="lg" color="green-4" />
              <div class="text-h5 text-weight-bolder q-mt-sm">
                {{ formatCurrency(hubStore.getKpis.monthlyCost) }}
              </div>
              <div class="text-caption text-grey-5">Custo Total (Mês)</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Manutenções -->
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="kpi-card text-center kpi-card--orange" flat>
            <q-card-section>
              <q-icon name="build" size="lg" color="orange-4" />
              <div class="text-h5 text-weight-bolder q-mt-sm">
                {{ hubStore.getKpis.pendingMaintenances }}
                <span class="text-caption text-weight-light">Pendentes</span>
              </div>
              <div class="text-caption text-grey-5">Manutenções</div>
            </q-card-section>
          </q-card>
        </div>

        <!-- Novos Leads (CRM) -->
        <div class="col-12 col-sm-6 col-md-3">
          <q-card class="kpi-card text-center disabled-card" flat>
            <q-card-section>
              <q-icon name="contacts" size="lg" color="grey-7" />
              <div class="text-h5 text-weight-bolder q-mt-sm">Em Breve</div>
              <div class="text-caption text-grey-6">Novos Leads (CRM)</div>
            </q-card-section>
          </q-card>
        </div>
      </template>
    </div>

    <!-- Gráfico Placeholder Melhorado -->
    <div class="row">
      <div class="col-12">
        <q-card flat class="kpi-card chart-placeholder">
          <q-card-section class="text-center">
            <div class="text-h6 text-white">Análise de Custos</div>
            <q-icon name="show_chart" size="xl" color="grey-7" class="q-mt-md" />
            <div class="text-grey-6 q-mt-md">O gráfico interativo de custos aparecerá aqui.</div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useHubStore } from 'src/stores/hub-store';

const authStore = useAuthStore();
const hubStore = useHubStore();

// Função para formatar o valor como moeda brasileira
const formatCurrency = (value: number) => {
  if (typeof value !== 'number') return 'R$ 0,00';
  return value.toLocaleString('pt-BR', {
    style: 'currency',
    currency: 'BRL',
  });
};

// Ao montar o componente, chama a ação para buscar os dados
onMounted(() => {
  hubStore.fetchKpis();
});
</script>

<style lang="scss" scoped>
.dashboard-page {
  // Efeito de fade-in para a página inteira
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.kpi-card {
  background-color: #1e1e2f;
  border: 1px solid #2d2d4a;
  border-radius: 12px;
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: all 0.3s ease-in-out;
  border-top: 3px solid transparent; // Borda superior para efeito de cor

  &:hover {
    transform: translateY(-5px);
    border-color: #5a5a8d;
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  }

  &--blue { border-top-color: $blue-4; }
  &--green { border-top-color: $green-4; }
  &--orange { border-top-color: $orange-4; }
}

.disabled-card {
  opacity: 0.5;
  &:hover {
    transform: none;
    border-color: #2d2d4a;
    box-shadow: none;
  }
}

.q-skeleton {
  background-color: rgba(255, 255, 255, 0.08);
  margin-left: auto;
  margin-right: auto;
}

.chart-placeholder {
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
   // Fundo com padrão de grade para simular um gráfico
  background-image:
    linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
  background-size: 20px 20px;
}
</style>
