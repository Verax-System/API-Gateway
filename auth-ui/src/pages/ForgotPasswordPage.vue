<template>
  <q-page class="flex flex-center">
    <q-card style="width: 400px">
      <q-card-section>
        <div class="text-h6">Redefinir Senha</div>
        <div class="text-subtitle2 text-grey-7">
          Insira seu e-mail para receber um link de redefinição.
        </div>
      </q-card-section>

      <q-card-section>
        <q-form @submit="onSubmit">
          <q-input
            v-model="email"
            type="email"
            label="E-mail"
            :rules="[val => !!val || 'O e-mail é obrigatório', val => /.+@.+\..+/.test(val) || 'E-mail inválido']"
            lazy-rules
            outlined
          />

          <q-card-actions align="right" class="q-pt-lg">
            <q-btn 
              flat 
              label="Voltar para Login" 
              color="primary" 
              :to="{ name: 'login' }" 
              no-caps 
            />
            <q-btn 
              type="submit" 
              label="Enviar Link" 
              color="primary" 
              :loading="loading" 
              no-caps 
            />
          </q-card-actions>
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';

export default defineComponent({
  name: 'ForgotPasswordPage',
  setup() {
    const authStore = useAuthStore();
    const email = ref('');
    const loading = ref(false);

    const onSubmit = async () => {
      loading.value = true;
      try {
        await authStore.forgotPassword(email.value);
        // O store já trata o Notify, não precisa de mais aqui.
      } catch (error) {
        // Erro é tratado pelo axios interceptor ou pelo store
        console.error(error);
      } finally {
        loading.value = false;
      }
    };

    return {
      email,
      loading,
      onSubmit,
    };
  },
});
</script>