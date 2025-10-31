<template>
  <q-card flat bordered>
    <q-card-section>
      <div class="text-h6 text-primary">Detalhes do Meu Perfil</div>
      <div class="text-subtitle2 text-grey">Atualize seu nome, e-mail e senha.</div>
    </q-card-section>

    <q-separator />

    <q-card-section class="q-gutter-md">
      <q-form @submit="handleUpdateProfile" class="q-gutter-md">
        
        <q-input
          v-model="fullName"
          label="Nome Completo"
          outlined
        />
        
        <q-input
          v-model="email"
          label="E-mail"
          type="email"
          outlined
          hint="Para alterar o e-mail, você precisará reconfirmar o novo endereço."
        />
        
        <q-separator />
        
        <div class="text-h6 q-mt-lg">Alterar Senha</div>
        <q-input
          v-model="oldPassword"
          label="Senha Atual"
          type="password"
          outlined
        />
        <q-input
          v-model="newPassword"
          label="Nova Senha"
          type="password"
          outlined
        />
        <q-input
          v-model="confirmNewPassword"
          label="Confirmar Nova Senha"
          type="password"
          outlined
        />
        
        <q-btn type="submit" label="Salvar Alterações" color="primary" :loading="loading" unelevated />
      </q-form>
    </q-card-section>
  </q-card>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useQuasar } from 'quasar';

const authStore = useAuthStore();
const $q = useQuasar();

const loading = ref(false);

const fullName = ref(authStore.user?.full_name || '');
const email = ref(authStore.user?.email || '');
const oldPassword = ref('');
const newPassword = ref('');
const confirmNewPassword = ref('');

// Sincronizar dados iniciais do store
watch(() => authStore.user, (user) => {
    if (user) {
        fullName.value = user.full_name;
        email.value = user.email;
    }
}, { immediate: true });


async function handleUpdateProfile() {
  if (loading.value) return;
  loading.value = true;

  // Implementação de validação e chamada de API aqui
  // Exemplo: await authStore.updateUserProfile({ full_name: fullName.value, ... });

  $q.notify({ type: 'positive', message: 'Perfil atualizado com sucesso! (Simulado)' });
  loading.value = false;
}
</script>