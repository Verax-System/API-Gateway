<template>
  <q-page class="flex flex-center">
    <q-card style="width: 400px">
      <q-card-section>
        <div class="text-h6">Nova Senha</div>
        <div v-if="!token" class="text-negative">
          Token de redefinição não encontrado na URL.
        </div>
      </q-card-section>

      <q-card-section v-if="token">
        <q-form @submit="onSubmit">
          <q-input
            v-model="newPassword"
            type="password"
            label="Nova Senha"
            :rules="[
              val => !!val || 'A nova senha é obrigatória',
              val => val.length >= 8 || 'Mínimo de 8 caracteres'
            ]"
            lazy-rules
            outlined
          />
          <q-input
            v-model="confirmPassword"
            type="password"
            label="Confirme a Senha"
            :rules="[
              val => !!val || 'A confirmação é obrigatória',
              val => val === newPassword || 'As senhas não coincidem'
            ]"
            lazy-rules
            outlined
            class="q-mt-md"
          />

          <q-card-actions align="right" class="q-pt-lg">
            <q-btn 
              type="submit" 
              label="Redefinir Senha" 
              color="primary" 
              :loading="loading" 
              no-caps 
              :disable="!newPassword || newPassword !== confirmPassword"
            />
          </q-card-actions>
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from 'src/stores/auth-store';

export default defineComponent({
  name: 'ResetPasswordPage',
  setup() {
    const authStore = useAuthStore();
    const route = useRoute();
    const router = useRouter();

    const token = route.query.token as string;
    const newPassword = ref('');
    const confirmPassword = ref('');
    const loading = ref(false);

    const onSubmit = async () => {
      if (!token) return;
      loading.value = true;
      try {
        await authStore.resetPassword(token, newPassword.value);
        // Redireciona para login após o sucesso
        await router.push({ name: 'login' });
      } catch (error) {
        // Erro é tratado pelo axios interceptor
        console.error(error);
      } finally {
        loading.value = false;
      }
    };

    return {
      token,
      newPassword,
      confirmPassword,
      loading,
      onSubmit,
    };
  },
});
</script>