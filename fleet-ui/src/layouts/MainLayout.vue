<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated :class="isDemo ? 'bg-grey-8' : 'bg-primary'">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />
        <q-toolbar-title v-if="!$q.screen.lt.sm">
          <span class="text-weight-bold">TruCar</span>
          <q-badge v-if="isDemo" color="orange" text-color="black" class="q-ml-sm">DEMO</q-badge>
        </q-toolbar-title>
        <q-space />
        <q-btn flat round dense icon="notifications">
          <q-badge color="red" floating transparent>4</q-badge>
          <q-menu>
            <q-list style="min-width: 300px">
              <q-item-label header>Notificações</q-item-label>
              <q-item clickable v-ripple>
                <q-item-section avatar><q-icon name="warning" color="orange" /></q-item-section>
                <q-item-section>Manutenção Preventiva P-001 Vencendo</q-item-section>
              </q-item>
              <q-item clickable v-ripple>
                <q-item-section avatar><q-icon name="local_shipping" color="green" /></q-item-section>
                <q-item-section>Ordem de Frete #1024 Concluída</q-item-section>
              </q-item>
              <q-item clickable v-ripple>
                <q-item-section avatar><q-icon name="error" color="red" /></q-item-section>
                <q-item-section>Falha no Sensor de Temperatura - Caminhão A</q-item-section>
              </q-item>
              <q-item clickable v-ripple>
                <q-item-section avatar><q-icon name="sell" color="blue" /></q-item-section>
                <q-item-section>Nova Peça "Filtro de Ar" Cadastrada</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
        <q-btn flat round dense icon="account_circle">
          <q-menu>
            <div class="row no-wrap q-pa-md">
              <div class="column items-center">
                <q-avatar size="72px">
                  <img :src="authStore.user?.avatar_url || defaultAvatar">
                </q-avatar>
                <div class="text-subtitle1 q-mt-md q-mb-xs">{{ authStore.user?.full_name || 'Usuário' }}</div>
                <div class="text-caption text-grey">{{ authStore.user?.email }}</div>
                <q-btn color="primary" label="Ver Perfil" unelevated size="sm" v-close-popup class="q-mt-md" @click="goToProfile" />
                <q-btn flat color="primary" label="Sair" size="sm" v-close-popup @click="handleLogout" />
              </div>
            </div>
          </q-menu>
        </q-btn>
      </q-toolbar>
      <q-banner v-if="authStore.isImpersonating" inline-actions class="bg-deep-orange text-white text-center shadow-2">
        <template v-slot:avatar>
          <q-icon name="visibility_off" color="white" />
        </template>
        <div class="text-weight-medium">
          Você está visualizando como <strong>{{ authStore.user?.full_name }}</strong>.
        </div>
        <template v-slot:action>
          <q-btn flat dense color="white" label="Voltar à minha conta" @click="authStore.stopImpersonation()" />
        </template>
      </q-banner>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered :width="280">
      <q-scroll-area class="fit">
        <q-list padding>
          <div v-for="category in menuCategories" :key="category.title">
            <q-item-label header class="text-weight-bold text-uppercase">{{ category.title }}</q-item-label>
            <EssentialLink v-for="link in category.links" :key="link.title" v-bind="link" />
            <q-separator class="q-my-md" v-if="category.separator" />
          </div>
          
          <q-separator class="q-my-md" />
          <q-item clickable tag="a" href="http://localhost/">
            <q-item-section avatar><q-icon name="hub" /></q-item-section>
            <q-item-section>
              <q-item-label>Voltar ao Hub</q-item-label>
              <q-item-label caption>Portal Principal</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>
      
      <div v-if="isDemo" class="absolute-bottom q-ma-sm">
        <PremiumWidget @upgrade="showUpgradeDialog" />
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useQuasar } from 'quasar';
import { useRouter } from 'vue-router';
import EssentialLink from 'components/EssentialLink.vue';
import PremiumWidget from 'components/PremiumWidget.vue';
import { useAuthStore } from 'stores/auth-store';
import { useTerminologyStore } from 'stores/terminology-store';
import defaultAvatar from 'src/assets/default-avatar.png';
import {
  mdiViewDashboard, mdiTruck, mdiRoadVariant, mdiWrench, mdiFileDocument,
  mdiClipboardList, mdiGasStation, mdiAccountGroup, mdiWarehouse, mdiCog,
  mdiChartLine, mdiTire, mdiTruckTrailer, mdiReceipt, mdiCarMultiple,
  mdiTrophy, mdiMapMarker, mdiAccountHardHat, mdiTractor, mdiSprout
} from '@quasar/extras/mdi-v7';

// Interfaces
interface MenuLink {
  title: string;
  caption: string;
  icon: string;
  link: string;
}
interface MenuCategory {
  title: string;
  links: MenuLink[];
  separator?: boolean;
}

const $q = useQuasar();
const router = useRouter();
const authStore = useAuthStore();
const terminologyStore = useTerminologyStore();

const leftDrawerOpen = ref(false);

// CORRIGIDO: Esta função agora chama 'logoutAndRedirect'
function handleLogout() {
  if (authStore.isImpersonating) {
    authStore.stopImpersonation();
  } else {
    authStore.logoutAndRedirect();
  }
}

// CORRIGIDO: Estas propriedades agora vêm do getter do authStore
const isDemo = computed(() => authStore.isDemo);

function showUpgradeDialog() {
  $q.dialog({
    title: 'Versão Completa',
    message: 'Esta é uma funcionalidade da versão completa do TruCar. Entre em contato para saber mais!',
    ok: { label: 'Entendido', flat: true },
  }).onOk(() => {
    // Ação
  });
}

function goToProfile() {
  if (authStore.user) {
    router.push(`/users/${authStore.user.id}`);
  }
}

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

// --- LÓGICA DE MENU DINÂMICO (RESTAURADA) ---
function getDriverMenu(): MenuCategory[] {
  // CORRIGIDO: 'userSector' vem do getter
  const sector = authStore.userSector;
  const menu: MenuCategory[] = [];

  const general: MenuCategory = {
    title: 'Geral',
    links: [
      { title: terminologyStore.journeyNounPlural, caption: `Minhas ${terminologyStore.journeyNounPlural}`, icon: mdiRoadVariant, link: '/journeys' },
      { title: 'Minhas Multas', caption: 'Registro de multas', icon: mdiReceipt, link: '/fines' },
    ],
    separator: true,
  };
  menu.push(general);

  if (sector === 'frete') {
    const freight: MenuCategory = {
      title: 'Fretes',
      links: [
        { title: 'Painel de Fretes', caption: 'Visualizar fretes disponíveis', icon: mdiClipboardList, link: '/driver-cockpit' },
      ],
      separator: true,
    };
    menu.push(freight);
  }

  const operational: MenuCategory = {
    title: 'Operacional',
    links: [
      { title: 'Abastecimentos', caption: 'Registrar abastecimentos', icon: mdiGasStation, link: '/fuel-logs' },
      { title: 'Manutenção', caption: 'Solicitar manutenção', icon: mdiWrench, link: '/maintenance' },
    ],
    separator: true,
  };
  menu.push(operational);
  return menu;
}

function getManagerMenu(): MenuCategory[] {
  // CORRIGIDO: 'userSector' vem do getter
  const sector = authStore.userSector;
  const menu: MenuCategory[] = [];

  const general: MenuCategory = {
    title: 'Geral',
    links: [
      { title: 'Dashboard', caption: 'Visão geral da frota', icon: mdiViewDashboard, link: '/dashboard' },
      { title: 'Relatórios', caption: 'Análises e KPIs', icon: mdiChartLine, link: '/reports' },
    ],
    separator: true,
  };
  menu.push(general);

  const fleet: MenuCategory = {
    title: terminologyStore.fleetNoun,
    links: [
      { title: terminologyStore.vehicleNounPlural, caption: `Gerenciar ${terminologyStore.vehicleNounPlural}`, icon: sector === 'agronegocio' ? mdiTractor : mdiTruck, link: '/vehicles' },
      { title: 'Pneus', caption: 'Controle de pneus', icon: mdiTire, link: '/tires' },
      { title: 'Manutenção', caption: 'Ordens de serviço', icon: mdiWrench, link: '/maintenance' },
      { title: 'Abastecimentos', caption: 'Controle de combustível', icon: mdiGasStation, link: '/fuel-logs' },
      { title: 'Documentos', caption: 'Vencimentos e alertas', icon: mdiFileDocument, link: '/documents' },
    ],
    separator: true,
  };
  if (sector === 'agronegocio' || sector === 'construcao_civil') {
    fleet.links.splice(1, 0, { title: terminologyStore.implementNounPlural, caption: `Gerenciar ${terminologyStore.implementNounPlural}`, icon: sector === 'agronegocio' ? mdiSprout : mdiAccountHardHat, link: '/implements' });
  }
  menu.push(fleet);

  if (sector === 'frete') {
    const freight: MenuCategory = {
      title: 'Logística',
      links: [
        { title: 'Ordens de Frete', caption: 'Gerenciar fretes', icon: mdiClipboardList, link: '/freight-orders' },
        { title: 'Jornadas', caption: 'Acompanhar motoristas', icon: mdiRoadVariant, link: '/journeys' },
        { title: 'Clientes', caption: 'Gerenciar clientes', icon: mdiAccountGroup, link: '/clients' },
      ],
      separator: true,
    };
    menu.push(freight);
  } else {
    const operations: MenuCategory = {
      title: 'Operações',
      links: [
        { title: terminologyStore.journeyNounPlural, caption: `Acompanhar ${terminologyStore.journeyNounPlural}`, icon: mdiRoadVariant, link: '/journeys' },
        { title: 'Clientes', caption: 'Gerenciar clientes', icon: mdiAccountGroup, link: '/clients' },
      ],
      separator: true,
    };
    menu.push(operations);
  }

  const management: MenuCategory = {
    title: 'Gestão',
    links: [
      { title: 'Custos', caption: 'Controle financeiro', icon: 'payments', link: '/costs' },
      { title: 'Estoque de Peças', caption: 'Inventário', icon: mdiWarehouse, link: '/parts' },
      { title: 'Usuários', caption: 'Motoristas e gestores', icon: 'manage_accounts', link: '/users' },
      { title: 'Multas', caption: 'Gestão de infrações', icon: mdiReceipt, link: '/fines' },
    ],
    separator: true,
  };
  menu.push(management);

  const advanced: MenuCategory = {
    title: 'Avançado',
    links: [
      { title: 'Performance', caption: 'Análise de Motoristas', icon: mdiTrophy, link: '/performance' },
      { title: 'Telemetria', caption: 'Rastreamento e Mapa', icon: mdiMapMarker, link: '/map' },
      { title: 'Configurações', caption: 'Ajustes do sistema', icon: mdiCog, link: '/settings' },
    ],
    separator: false,
  };
  menu.push(advanced);

  if (authStore.isSuperuser) {
    management.links.push({
      title: 'Admin',
      caption: 'Superusuário',
      icon: 'admin_panel_settings',
      link: '/admin',
    });
  }
  return menu;
}

const menuCategories = computed(() => {
  if (authStore.user?.role === 'motorista' && !authStore.isImpersonating) {
    return getDriverMenu();
  }
  return getManagerMenu();
});
</script>