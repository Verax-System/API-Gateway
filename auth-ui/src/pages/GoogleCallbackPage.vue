<template>
  <q-page class="flex flex-center">
    <q-card style="width: 400px" class="q-pa-lg text-center">
      <q-card-section>
        <q-spinner color="primary" size="3em" />
      </q-card-section>

      <q-card-section>
        <div class="text-h6">Processando login social...</div>
        <div class="text-body2 text-grey-7">
          Aguarde enquanto validamos sua conta Google.
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { api } from 'src/boot/axios';
import { useAuthStore } from 'src/stores/auth-store';
import { Notify } from 'quasar';

export default defineComponent({
  name: 'GoogleCallbackPage',
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();

    onMounted(async () => {
      const code = route.query.code as string;
      const error = route.query.error as string;

      if (error) {
        Notify.create({
          type: 'negative',
          message: 'Login Google cancelado ou falhou: ' + error,
        });
        await router.push({ name: 'login' });
        return;
      }

      if (!code) {
        Notify.create({
          type: 'negative',
          message: 'Código de autorização Google não encontrado.',
        });
        await router.push({ name: 'login' });
        return;
      }

      try {
        const response = await api.post('/api/v1/auth/google/callback', {
          code: code,
        });

        const { access_token, refresh_token } = response.data;

        // Atualiza a Store e LocalStorage com os novos tokens
        authStore.token = access_token;
        authStore.refreshToken = refresh_token;
        authStore.isAuthenticated = true;
        
        localStorage.setItem('token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        
        await authStore.fetchUser();
        
        // Redireciona para o dashboard após o sucesso
        Notify.create({ type: 'positive', message: 'Login com Google bem-sucedido!' });
        await router.push({ name: 'dashboard' });

      } catch (e) {
        Notify.create({
          type: 'negative',
          message: 'Falha ao autenticar com a Google. Credenciais inválidas ou erro interno.',
        });
        await router.push({ name: 'login' });
      }
    });

    return {};
  },
});
</script>