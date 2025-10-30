<template>
  <q-layout view="lHh LpR fFf" class="bg-dark-theme text-white">
    <q-drawer
      v-model="leftDrawerOpen"
      show-if-above
      :width="260"
      class="bg-dark-drawer"
    >
      <q-scroll-area class="fit">
        <div class="sidebar-header q-pa-md text-center">
          <div class="logo">Verax</div>
        </div>

        <q-list padding>
          <q-item clickable v-ripple :active="true" class="nav-item active-item">
            <q-item-section avatar>
              <!-- ÍCONE CORRIGIDO -->
              <q-icon name="dashboard" />
            </q-item-section>
            <q-item-section> Hub </q-item-section>
          </q-item>

          <q-item clickable v-ripple class="nav-item">
            <q-item-section avatar>
              <!-- ÍCONE CORRIGIDO -->
              <q-icon name="directions_car" />
            </q-item-section>
            <q-item-section> TruCar </q-item-section>
          </q-item>

          <q-item clickable v-ripple class="nav-item">
            <q-item-section avatar>
              <!-- ÍCONE CORRIGIDO -->
              <q-icon name="contacts" />
            </q-item-section>
            <q-item-section class="flex items-center no-wrap">
              CRM <q-badge color="orange" class="q-ml-sm">Breve</q-badge>
            </q-item-section>
          </q-item>

          <q-item clickable v-ripple class="nav-item">
            <q-item-section avatar>
              <!-- ÍCONE CORRIGIDO -->
              <q-icon name="groups" />
            </q-item-section>
            <q-item-section class="flex items-center no-wrap">
              RH <q-badge color="orange" class="q-ml-sm">Breve</q-badge>
            </q-item-section>
          </q-item>
        </q-list>
      </q-scroll-area>

      <!-- SEÇÃO DO USUÁRIO MELHORADA -->
      <div class="absolute-bottom user-profile-section">
        <q-item>
          <q-item-section avatar>
            <q-avatar size="40px">
              <img src="https://i.pravatar.cc/150?u=a042581f4e29026704d" />
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-weight-medium">{{ authStore.user?.full_name }}</q-item-label>
            <q-item-label caption class="text-grey-6">{{
              authStore.user?.organization.name
            }}</q-item-label>
          </q-item-section>
          <q-item-section side>
             <q-btn flat round dense icon="more_vert">
                <!-- MENU DO USUÁRIO -->
                <q-menu anchor="top right" self="top left" dark>
                  <q-list dense style="min-width: 100px">
                    <q-item clickable v-close-popup>
                      <q-item-section>Perfil</q-item-section>
                    </q-item>
                    <q-item clickable v-close-popup>
                      <q-item-section>Configurações</q-item-section>
                    </q-item>
                    <q-separator />
                    <q-item clickable v-close-popup @click="authStore.logout()">
                      <q-item-section class="text-red-4">Sair</q-item-section>
                    </q-item>
                  </q-list>
                </q-menu>
              </q-btn>
          </q-item-section>
        </q-item>
      </div>
    </q-drawer>

    <q-header class="bg-dark-header q-py-sm">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Menu" @click="toggleLeftDrawer" />

        <q-toolbar-title> Dashboard Geral </q-toolbar-title>

        <q-space />

        <div class="q-gutter-sm row items-center no-wrap">
          <!-- ÍCONE CORRIGIDO -->
          <q-btn round dense flat icon="notifications">
            <q-badge color="orange" floating transparent> 4 </q-badge>
             <q-tooltip>Notificações</q-tooltip>
          </q-btn>
          <!-- Botão de logout movido para o menu do perfil -->
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <!-- TRANSIÇÃO DE PÁGINA -->
      <router-view v-slot="{ Component }">
        <transition appear enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
          <component :is="Component" />
        </transition>
      </router-view>
    </q-page-container>
  </q-layout>
</template>

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

