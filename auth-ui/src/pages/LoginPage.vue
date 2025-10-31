<template>
  <q-page 
    class="flex flex-center" 
    style="
      background-color: #f0f4f8; /* Cor de base clara */
      background-image: linear-gradient(
        45deg, 
        rgba(200, 200, 200, 0.1) 25%, 
        transparent 25%, 
        transparent 75%, 
        rgba(200, 200, 200, 0.1) 75%, 
        rgba(200, 200, 200, 0.1)
      ), 
      linear-gradient(
        -45deg, 
        rgba(200, 200, 200, 0.1) 25%, 
        transparent 25%, 
        transparent 75%, 
        rgba(200, 200, 200, 0.1) 75%, 
        rgba(200, 200, 200, 0.1)
      );
      background-size: 20px 20px; /* Ajuste o tamanho dos 'risquinhos' */
    "
  >
    <div class="absolute-top-left q-pa-lg text-primary text-h4 text-weight-bolder">
      VERAX HUB
    </div>

    <q-card 
      class="q-pa-md shadow-10" 
      style="width: 450px; border-radius: 15px;"
    >
      <q-card-section class="text-center q-pb-none">
        
        <div class="text-h4 text-primary text-weight-bold">
          Bem-vindo de volta!
        </div>
        <div class="text-subtitle1 text-grey-7 q-mt-sm q-mb-lg">
          Acesse sua conta para continuar.
        </div>
      </q-card-section>
      
      <q-card-section>
        <q-form @submit="handleLogin" class="q-gutter-md">
          <q-input
            v-model="email"
            label="E-mail"
            type="email"
            filled
            clearable
            :rules="[val => !!val || 'E-mail obrigatório']"
          >
            <template v-slot:prepend>
              <q-icon name="mail_outline" />
            </template>
          </q-input>
          
          <q-input
            v-model="password"
            label="Senha"
            type="password"
            filled
            :rules="[val => !!val || 'Senha obrigatória']"
          >
            <template v-slot:prepend>
              <q-icon name="lock_outline" />
            </template>
          </q-input>
          
          <div class="flex justify-between items-center">
            
            <q-btn
              flat
              dense
              label="Não recebeu o email de verificação?"
              color="grey-7"
              @click="openResendDialog = true"
              no-caps
              size="sm"
              padding="none"
            />
            
            <q-btn
              flat
              dense
              label="Esqueceu a senha?"
              color="primary"
              :to="{ name: 'forgot-password' }"
              no-caps
              size="sm"
              padding="none"
            />
          </div>
          
          <q-btn
            type="submit"
            label="Entrar"
            color="primary"
            class="full-width q-py-sm text-weight-bold"
            rounded
            :loading="loading"
            no-caps
          />
          
          <q-separator class="q-my-md">
            <q-chip color="grey-3" text-color="grey-7" size="sm" outline>
              OU
            </q-chip>
          </q-separator>

          <q-btn
            @click="handleGoogleLogin"
            label="Entrar com Google"
            icon="mdi-google" 
            text-color="grey-9"
            class="full-width q-py-sm"
            :loading="loadingGoogle"
            no-caps
            outline
            rounded
          />
          
        </q-form>
      </q-card-section>
      
      <q-card-section class="text-center q-pt-none">
        <div class="text-body2 text-grey-7">
          Não tem uma conta? 
          <q-btn
            flat
            dense
            label="Cadastre-se"
            color="secondary"
            :to="{ name: 'register' }"
            no-caps
            padding="none"
          />
        </div>
      </q-card-section>
    </q-card>
    
    <q-dialog v-model="openResendDialog">
      <q-card style="width: 350px;">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Reenviar Verificação</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>

        <q-card-section>
          <div class="q-mb-md">Digite o e-mail da sua conta para receber um novo link de ativação.</div>
          <q-input
            v-model="resendEmail"
            type="email"
            label="E-mail da Conta"
            outlined
            dense
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancelar" color="negative" v-close-popup no-caps />
          <q-btn 
            label="Reenviar" 
            color="primary" 
            :loading="loadingResend"
            @click="handleResend" 
            no-caps 
            :disable="!resendEmail || !/.+@.+\..+/.test(resendEmail)"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
    
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { api } from 'src/boot/axios';
import { Notify } from 'quasar';

export default defineComponent({
  name: 'LoginPage',
  setup() {
    const authStore = useAuthStore();
    const email = ref('');
    const password = ref('');
    const loading = ref(false);
    const loadingGoogle = ref(false);
    
    // NOVO: Lógica de Reenvio
    const openResendDialog = ref(false);
    const resendEmail = ref('');
    const loadingResend = ref(false);

<<<<<<< HEAD
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
=======
    const handleLogin = async () => {
      loading.value = true;
      await authStore.login({
        email: email.value,
        password: password.value,
      });
      loading.value = false;
    };

    const handleGoogleLogin = async () => {
      loadingGoogle.value = true;
      try {
        const response = await api.get('/api/v1/auth/google/login-url');
        const { url } = response.data;
        window.location.href = url;
      } catch (error) {
        console.error('Erro ao obter URL de login do Google:', error);
        loadingGoogle.value = false;
        Notify.create({
          type: 'negative',
          message: 'Falha ao iniciar login Google. Verifique o console.',
        });
      }
    };

    const handleResend = async () => {
        // Validação simples
        if (!resendEmail.value || !/.+@.+\..+/.test(resendEmail.value)) return;
        
        loadingResend.value = true;
        try {
            // Chama o novo endpoint da API
            await api.post('/api/v1/users/resend-verification', { email: resendEmail.value });
            
            Notify.create({
              type: 'positive',
              message: 'Se o e-mail precisar de verificação, um novo link foi enviado!',
            });
            openResendDialog.value = false;
            resendEmail.value = '';

        } catch (error: any) {
            // Se o endpoint retornar 202 (Accepted) mesmo com falha interna, este catch é só para erros de conexão ou 500.
            Notify.create({
              type: 'negative',
              message: error.response?.data?.detail || 'Erro ao processar sua requisição. Tente mais tarde.',
            });
        } finally {
            loadingResend.value = false;
        }
    };

    return {
      email,
      password,
      loading,
      loadingGoogle,
      
      handleLogin,
      handleGoogleLogin,
      
      // Reenvio
      openResendDialog,
      resendEmail,
      loadingResend,
      handleResend,
    };
  },
});
</script>
>>>>>>> 226d4bb11378fe37d171a0e916945c18d6208a5a
