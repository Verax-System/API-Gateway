<template>
  <q-page class="flex flex-center">
    <q-card style="width: 400px" class="q-pa-lg text-center">
      <q-card-section>
        <q-spinner
          v-if="loading"
          color="primary"
          size="3em"
        />
        <q-icon
          v-else-if="success"
          name="check_circle"
          color="positive"
          size="4em"
        />
        <q-icon
          v-else
          name="error"
          color="negative"
          size="4em"
        />
      </q-card-section>

      <q-card-section>
        <div class="text-h6">{{ message }}</div>
        <div class="text-body2 text-grey-7" v-if="success">
          Seu e-mail foi verificado com sucesso. Você será redirecionado para o login.
        </div>
      </q-card-section>

      <q-card-actions align="center" v-if="!loading">
        <q-btn 
          label="Ir para Login" 
          color="primary" 
          :to="{ name: 'login' }" 
          no-caps 
        />
      </q-card-actions>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from 'src/stores/auth-store';

export default defineComponent({
  name: 'VerifyEmailPage',
  setup() {
    const authStore = useAuthStore();
    const route = useRoute();
    const router = useRouter();

    const loading = ref(true);
    const success = ref(false);
    const message = ref('Verificando seu e-mail...');

    onMounted(async () => {
      const token = route.params.token as string;

      if (!token) {
        message.value = 'Token de verificação não encontrado.';
        loading.value = false;
        return;
      }

      try {
        await authStore.verifyEmail(token);
        success.value = true;
        message.value = 'Verificação Concluída!';
        
        // Redireciona para login após alguns segundos
        setTimeout(() => {
          void router.push({ name: 'login' });
        }, 3000);

      } catch (error: any) {
        success.value = false;
        message.value = error.response?.data?.detail || 'Falha na verificação. O link pode ser inválido ou expirado.';
      } finally {
        loading.value = false;
      }
    });

    return {
      loading,
      success,
      message,
    };
  },
});
</script>