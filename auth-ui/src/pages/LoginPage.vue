<template>
  <q-layout>
    <q-page-container>
      <q-page class="flex flex-center login-body">
        <q-card class="login-box">
          <q-card-section class="login-header text-center">
            <div class="logo">Verax</div>
            <div class="text-h5 q-mt-sm">Acesse seu Ecossistema</div>
            <div class="text-subtitle2 text-grey">Uma conta, todas as soluções.</div>
          </q-card-section>

          <q-card-section>
            <q-form @submit.prevent="handleLogin" class="q-gutter-md">
              <q-input
                v-model="email"
                label="E-mail"
                type="email"
                dark
                outlined
                lazy-rules
                :rules="[(val) => !!val || 'E-mail é obrigatório']"
              />
              <q-input
                v-model="password"
                label="Senha"
                type="password"
                dark
                outlined
                lazy-rules
                :rules="[(val) => !!val || 'Senha é obrigatória']"
              />
              <div>
                <q-btn
                  label="Entrar"
                  type="submit"
                  color="primary"
                  class="full-width"
                  :loading="isLoading"
                />
              </div>
            </q-form>
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useQuasar } from 'quasar';
import { useAuthStore } from 'src/stores/auth-store';

const email = ref('');
const password = ref('');
const isLoading = ref(false);

const authStore = useAuthStore();
const router = useRouter();
const $q = useQuasar();

// --- FUNÇÃO CORRIGIDA ---
const handleLogin = async () => {
  isLoading.value = true;
  try {
    // 1. A action 'login' espera UM objeto (LoginCredentials).
    // 2. Passamos o email e a senha dentro desse objeto.
    const loginSuccess = await authStore.login({
      email: email.value,
      password: password.value
    });

    if (loginSuccess) {
      $q.notify({
        color: 'positive',
        message: 'Login realizado com sucesso!',
        icon: 'check',
        position: 'top',
      });
      // O redirecionamento principal é feito na store.
      // Este 'push' serve como um fallback ou destino pós-login.
      await router.push('/hub'); 
    } else {
      // A notificação de erro já é tratada pela store,
      // então não precisamos duplicá-la aqui.
    }
  } catch (error) {
    console.error('Falha crítica no processo de login:', error);
    $q.notify({
      color: 'negative',
      message: 'Ocorreu um erro inesperado. Tente novamente.',
      icon: 'error',
      position: 'top',
    });
  } finally {
    isLoading.value = false;
  }
};
</script>

<style lang="scss">
.login-body {
  background: linear-gradient(45deg, #12121c, #1e1e2f);
}
.login-box {
  width: 100%;
  max-width: 400px;
  background-color: #1e1e2f;
  border: 1px solid #2d2d4a;
  border-radius: 12px;
}
.login-header .logo {
  font-size: 2.5rem;
  background: linear-gradient(45deg, #8e44ad, #2980b9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 700;
}
</style> 