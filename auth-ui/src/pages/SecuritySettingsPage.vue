<template>
  <q-card flat bordered>
    <q-card-section>
      <div class="text-h6 text-primary">Autenticação e Segurança (2FA)</div>
      <div class="text-subtitle2 text-grey">Proteja sua conta com autenticação de dois fatores.</div>
    </q-card-section>

    <q-separator />

    <q-card-section class="q-pa-lg">
      <div class="row items-center q-gutter-md">
        <q-icon 
          :name="authStore.user?.is_mfa_enabled ? 'verified_user' : 'lock_open'" 
          size="lg" 
          :color="authStore.user?.is_mfa_enabled ? 'positive' : 'negative'" 
        />
        <div>
          <div class="text-h6 q-mb-none">
            {{ authStore.user?.is_mfa_enabled ? '2FA ATIVADO' : '2FA DESATIVADO' }}
          </div>
          <div class="text-caption" :class="authStore.user?.is_mfa_enabled ? 'text-positive' : 'text-negative'">
            {{ authStore.user?.is_mfa_enabled ? 'Sua conta está protegida por TOTP.' : 'Sua conta não possui uma camada extra de segurança.' }}
          </div>
        </div>
        <q-space />
        <q-btn 
          :label="authStore.user?.is_mfa_enabled ? 'Desativar 2FA' : 'Ativar 2FA'" 
          :color="authStore.user?.is_mfa_enabled ? 'negative' : 'primary'" 
          :loading="loadingMFA"
          unelevated 
          @click="authStore.user?.is_mfa_enabled ? handleDisableMFA() : handleEnableMFA()"
        />
      </div>
      
      <q-slide-transition>
        <div v-if="mfaSetupData">
          <q-separator class="q-my-md" />
          <div class="text-subtitle1 text-weight-bold q-mb-sm">Passo 1: Escaneie o QR Code</div>
          <div class="row items-center q-gutter-xl">
            <q-img :src="mfaSetupData.qr_code_url" style="width: 200px; height: 200px; border: 1px solid #ddd;" fit="contain" />
            <div class="column q-gutter-sm">
                <div class="text-subtitle2">Código Secreto:</div>
                <q-chip color="grey-2" text-color="dark" class="text-weight-bold">
                    {{ mfaSetupData.secret }}
                </q-chip>
                <div class="text-caption text-grey">Use um app como Google Authenticator.</div>
            </div>
          </div>

          <div class="text-subtitle1 text-weight-bold q-mt-lg q-mb-sm">Passo 2: Verifique o Código</div>
          <q-input 
            v-model="verificationCode" 
            label="Código de 6 dígitos" 
            mask="######"
            maxlength="6"
            outlined
            dense
            style="max-width: 250px;"
          >
            <template v-slot:append>
                <q-btn label="Confirmar" color="positive" @click="handleVerifyMFA" :loading="loadingVerify" unelevated />
            </template>
          </q-input>
        </div>
      </q-slide-transition>
    </q-card-section>
    
    <q-separator />

    <q-card-section>
      <div class="text-h6 q-mb-sm">Dispositivos Confiáveis</div>
      <q-list bordered separator class="rounded-borders">
        <q-item-label header>Sessões ativas que ignoram o 2FA</q-item-label>
        <q-item v-for="i in 2" :key="i">
          <q-item-section avatar><q-icon name="computer" /></q-item-section>
          <q-item-section>
            <q-item-label>Desktop (Chrome no Windows)</q-item-label>
            <q-item-label caption>Localização: São Paulo, Brasil</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn label="Revogar" color="negative" flat dense size="sm" />
          </q-item-section>
        </q-item>
        <q-item>
          <q-item-section avatar><q-icon name="phone_android" /></q-item-section>
          <q-item-section>
            <q-item-label>Smartphone Android</q-item-label>
            <q-item-label caption>Último acesso: 3 horas atrás</q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn label="Revogar" color="negative" flat dense size="sm" />
          </q-item-section>
        </q-item>
      </q-list>
    </q-card-section>
    
  </q-card>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useQuasar } from 'quasar';
import { onMounted } from 'vue';

const authStore = useAuthStore();
const $q = useQuasar();

const loadingMFA = ref(false);
const loadingVerify = ref(false);
const verificationCode = ref('');

// Estrutura para receber o QR Code URL e o Secret Key
const mfaSetupData = ref<{ secret: string; qr_code_url: string } | null>(null);

// --- HANDLERS DE 2FA ---

async function handleEnableMFA() {
  if (loadingMFA.value) return;
  loadingMFA.value = true;
  mfaSetupData.value = null; // Limpa dados anteriores
  
  try {
    // Ação na Store para obter o QR Code e o Secret
    const data = await authStore.startMFAEnrollment();
    mfaSetupData.value = data;
    $q.notify({ type: 'info', message: 'Escaneie o QR Code para continuar.' });
  } catch (error) {
    $q.notify({ type: 'negative', message: 'Erro ao iniciar 2FA. Tente novamente.' });
  } finally {
    loadingMFA.value = false;
  }
}

async function handleVerifyMFA() {
    if (!verificationCode.value || verificationCode.value.length !== 6 || !mfaSetupData.value) return;
    loadingVerify.value = true;
    
    try {
        const success = await authStore.verifyAndEnableMFA(
            mfaSetupData.value.secret,
            verificationCode.value
        );

        if (success) {
            $q.notify({ type: 'positive', message: '2FA ativado com sucesso!' });
            mfaSetupData.value = null;
        } else {
            $q.notify({ type: 'negative', message: 'Código de verificação inválido.' });
        }
    } catch (error) {
        $q.notify({ type: 'negative', message: 'Erro ao verificar o código.' });
    } finally {
        loadingVerify.value = false;
        verificationCode.value = '';
    }
}

async function handleDisableMFA() {
    if (loadingMFA.value) return;
    loadingMFA.value = true;
    
    $q.dialog({
        title: 'Confirmação',
        message: 'Tem certeza de que deseja desativar a autenticação de dois fatores? Isso tornará sua conta menos segura.',
        cancel: true,
        persistent: true
    }).onOk(async () => {
        try {
            const success = await authStore.disableMFA();
            if (success) {
                $q.notify({ type: 'positive', message: '2FA desativado com sucesso.' });
            } else {
                 $q.notify({ type: 'negative', message: 'Falha ao desativar 2FA.' });
            }
        } catch (error) {
            $q.notify({ type: 'negative', message: 'Erro de API ao desativar 2FA.' });
        } finally {
            loadingMFA.value = false;
        }
    }).onCancel(() => {
        loadingMFA.value = false;
    });
}
</script>