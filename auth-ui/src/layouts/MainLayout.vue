<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="toggleLeftDrawer"
        />

        <q-toolbar-title>
          Virax Hub
        </q-toolbar-title>

        <div>
          <q-btn flat dense round icon="logout" @click="handleLogout" />
        </div>
      </q-toolbar>
    </q-header>

    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      bordered
    >
      <q-list>
        <q-item-label
          header
        >
          Menu Principal
        </q-item-label>

        <EssentialLink
          v-for="link in essentialLinks"
          :key="link.title"
          v-bind="link"
        />

        <q-item-label header>Aplicações</q-item-label>

        <q-item
          clickable
          tag="a"
          href="/fleet/"
          target="_blank" 
        >
          <q-item-section avatar>
            <q-icon name="local_shipping" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Gestão de Frota</q-item-label>
            <q-item-label caption>Acessar o TruCar</q-item-label>
          </q-item-section>
        </q-item>

        <q-item
          clickable
          tag="a"
          href="/sales/"
          target="_blank"
        >
          <q-item-section avatar>
            <q-icon name="point_of_sale" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Ponto de Venda</q-item-label>
            <q-item-label caption>Acessar o VRSales</q-item-label>
          </q-item-section>
        </q-item>

        </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import EssentialLink, { EssentialLinkProps } from 'components/EssentialLink.vue';
import { useAuthStore } from 'src/stores/auth-store';
import { useRouter } from 'vue-router';

const essentialLinks: EssentialLinkProps[] = [
  {
    title: 'Dashboard',
    caption: 'Visão Geral',
    icon: 'dashboard',
    link: '/dashboard',
  },
  {
    title: 'Usuários',
    caption: 'Gerenciamento de Usuários',
    icon: 'people',
    link: '/admin/users', // Assumindo que você tem essa rota
  },
];

const leftDrawerOpen = ref(false);
const authStore = useAuthStore();
const router = useRouter();

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';

const leftDrawerOpen = ref(false);
const authStore = useAuthStore();

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}
</script>

<style lang="scss" scoped>
// Cores e Estilos do nosso Protótipo
.bg-dark-theme {
  background-color: #12121c;
}
.bg-dark-drawer {
  background-color: #1e1e2f;
  border-right: 1px solid #2d2d4a;
}
.bg-dark-header {
  background-color: #1e1e2f;
  border-bottom: 1px solid #2d2d4a;
}
.sidebar-header .logo {
  font-size: 2.5rem;
  background: linear-gradient(45deg, #8e44ad, #2980b9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}
.nav-item {
  color: #bdc3c7;
  border-radius: 8px;
  margin: 4px 10px; // Espaçamento entre os itens
  &.active-item {
    color: white;
    // Gradiente sutil para o item ativo, combinando com o logo
    background: linear-gradient(90deg, #8e44ad, #3498db);
  }
   &:hover {
    background-color: #2d2d4a;
  }
  .q-item__section--avatar {
    min-width: 40px;
  }
}

.user-profile-section {
  border-top: 1px solid #2d2d4a;
  background-color: #1e1e2f; // Mantém a cor de fundo consistente
}
</style>

