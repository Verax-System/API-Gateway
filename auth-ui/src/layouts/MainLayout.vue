<template>
  <q-layout view="lHh Lpr lFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          Verax Hub
        </q-toolbar-title>

        <q-space />

        <!-- Opções de Notificação (Exemplo) -->
        <q-btn flat round dense icon="notifications">
          <q-badge color="red" floating transparent>2</q-badge>
          <q-menu>
            <q-list style="min-width: 300px">
              <q-item-label header>Notificações</q-item-label>
              <q-item clickable v-ripple>
                <q-item-section avatar><q-icon name="warning" color="orange" /></q-item-section>
                <q-item-section>Verificação de e-mail pendente</q-item-section>
              </q-item>
              <q-item clickable v-ripple>
                <q-item-section avatar><q-icon name="new_releases" color="blue" /></q-item-section>
                <q-item-section>Nova atualização de software!</q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable class="text-center">
                <q-item-section>Ver todas</q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
        
        <!-- Perfil do Usuário -->
        <q-btn flat round dense icon="account_circle" class="q-ml-sm">
          <q-menu>
            <div class="row no-wrap q-pa-md">
              <div class="column items-center">
                <q-avatar size="72px">
                  <img :src="authStore.user?.avatar_url || 'https://placehold.co/72x72/26A69A/FFFFFF?text=V'" alt="User Avatar">
                </q-avatar>
                <div class="text-subtitle1 q-mt-md q-mb-xs">{{ authStore.user?.full_name || 'Usuário' }}</div>
                <div class="text-caption text-grey">{{ authStore.user?.email || 'N/A' }}</div>
                <q-btn color="primary" label="Ver Perfil" unelevated size="sm" v-close-popup class="q-mt-md" @click="goToProfile" />
                <q-btn flat color="primary" label="Sair" size="sm" v-close-popup @click="handleLogout" />
              </div>
            </div>
          </q-menu>
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer v-model="leftDrawerOpen" show-if-above bordered>
      <q-scroll-area style="height: calc(100% - 150px); margin-top: 0; border-right: 1px solid #ddd">
        <q-list padding>
          <q-item-label header>
            Navegação Principal
          </q-item-label>

          <EssentialLink v-for="link in essentialLinks" :key="link.title" v-bind="link" />

          <q-separator class="q-my-md" />

          <q-item-label header>
            Aplicações (Setores)
          </q-item-label>
          
          <q-item
            v-for="app in hubStore.availableApps"
            :key="app.route"
            clickable
            v-ripple
            :href="`http://localhost/${app.route}`"
            target="_self"
          >
            <q-item-section avatar>
              <q-icon :name="app.icon" />
            </q-item-section>
            <q-item-section>
              <q-item-label>{{ app.title }}</q-item-label>
              <q-item-label caption>{{ app.caption }}</q-item-label>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>

      <div class="absolute-bottom bg-grey-2 q-pa-md">
        <div class="text-caption text-grey-7">Versão 1.0.0</div>
      </div>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import EssentialLink from 'components/EssentialLink.vue';
import { useAuthStore } from 'stores/auth-store';
import { useHubStore } from 'stores/hub-store';
import { useQuasar } from 'quasar';

// Interfaces
interface EssentialLinkProps {
  title: string;
  caption: string;
  icon: string;
  link: string;
}

// Lojas
const authStore = useAuthStore();
const hubStore = useHubStore();
const router = useRouter();
const $q = useQuasar();

// Estado
const leftDrawerOpen = ref(false);

// Links de navegação estáticos do Hub
const essentialLinks: EssentialLinkProps[] = [
  {
    title: 'Dashboard',
    caption: 'Visão Geral do Sistema',
    icon: 'dashboard',
    link: '/dashboard',
  },
  {
    title: 'Gerenciar Usuários',
    caption: 'Configurações e Permissões',
    icon: 'group',
    link: '/users',
  },
  {
    title: 'Minha Conta',
    caption: 'Configurações de Perfil',
    icon: 'settings',
    link: '/settings',
  },
];

function toggleLeftDrawer() {
  leftDrawerOpen.value = !leftDrawerOpen.value;
}

function handleLogout() {
  // Chamada de logout do auth-store
  authStore.logoutAndRedirect();
}

function goToProfile() {
  if (authStore.user?.id) {
    // CORREÇÃO: Usando 'void' para evitar 'floating promise'
    void router.push(`/users/${authStore.user.id}`);
  } else {
    $q.notify({ type: 'negative', message: 'Dados do usuário indisponíveis.' });
  }
}
</script>
