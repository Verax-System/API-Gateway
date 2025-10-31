<template>
  <q-page padding>
    <div class="text-h5 q-mb-md">Configurações de Segurança</div>

    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6">Autenticação de Dois Fatores (2FA)</div>
        <q-item>
          <q-item-section avatar>
            <q-icon :name="authStore.user?.is_mfa_enabled ? 'mdi-shield-check' : 'mdi-shield-off'" 
                    :color="authStore.user?.is_mfa_enabled ? 'positive' : 'negative'" 
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>Status</q-item-label>
            <q-item-label caption>
              {{ authStore.user?.is_mfa_enabled ? 'Ativo' : 'Inativo' }}
            </q-item-label>
          </q-item-section>
          <q-item-section side>
            <q-btn 
              :label="authStore.user?.is_mfa_enabled ? 'Desativar 2FA' : 'Ativar 2FA'" 
              :color="authStore.user?.is_mfa_enabled ? 'negative' : 'positive'" 
              @click="authStore.user?.is_mfa_enabled ? openDisableDialog() : startMFAEnrollment()"
              :loading="mfaLoading"
              no-caps
            />
          </q-item-section>
        </q-item>
      </q-card-section>
    </q-card>
    
    <q-card class="q-mb-lg">
      <q-card-section>
        <div class="text-h6">Sessões Ativas</div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <q-list separator>
          <q-item v-if="sessions.length === 0">
            <q-item-section>
              <q-item-label>Nenhuma sessão ativa encontrada.</q-item-label>
            </q-item-section>
          </q-item>

          <q-item v-for="session in sessions" :key="session.id">
            <q-item-section>
              <q-item-label>
                {{ session.user_agent ? session.user_agent.split('(')[0].trim() : 'Dispositivo Desconhecido' }}
                <q-badge v-if="session.is_current" color="primary">Atual</q-badge>
              </q-item-label>
              <q-item-label caption>
                IP: {{ session.ip_address || 'N/A' }} | Criado em: {{ formatDate(session.created_at) }}
              </q-item-label>
            </q-item-section>
            <q-item-section side>
              <q-btn 
                icon="mdi-logout" 
                color="negative" 
                round 
                flat 
                dense
                size="sm"
                @click="logoutSession(session.id, session.is_current)"
                :disable="session.is_current"
              >
                 <q-tooltip v-if="session.is_current">Não é possível deslogar a sessão atual por aqui.</q-tooltip>
                 <q-tooltip v-else>Encerrar sessão</q-tooltip>
              </q-btn>
            </q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-actions align="right">
         <q-btn 
             label="Encerrar Outras Sessões" 
             color="negative" 
             flat
             :loading="loadingSessions"
             @click="logoutAllOtherSessions"
             :disable="sessions.length <= 1"
             no-caps
         />
         <q-btn 
             label="Recarregar" 
             color="primary" 
             flat
             :loading="loadingSessions"
             @click="fetchSessionsAndDevices"
             icon="mdi-refresh"
             no-caps
         />
      </q-card-actions>
    </q-card>
    
    <q-card>
      <q-card-section>
        <div class="text-h6">Dispositivos Confiáveis</div>
      </q-card-section>
      <q-card-section class="text-body2 text-grey-7 q-pt-none">
          <p>
             Dispositivos confiáveis não exigem 2FA no login por 
             {{ settings.trustedDeviceMaxAgeDays || '30' }} dias. 
             Você deve usar um endpoint da API para listar e remover estes dispositivos. 
          </p>
          </q-card-section>
      </q-card>

    <q-dialog v-model="mfaEnableDialog" persistent>
      <q-card>
        <q-card-section>
          <div class="text-h6">Ativar Autenticação de Dois Fatores</div>
        </q-card-section>

        <q-card-section class="q-pt-none" v-if="mfaStep === 1 && mfaEnrollment.qr_code_base64">
          <div class="text-body2 q-mb-md">
            1. Use um aplicativo autenticador (ex: Google Authenticator) para escanear o QR Code abaixo:
          </div>
          <div class="flex flex-center q-mb-md">
            <q-img :src="'data:image/png;base64,' + mfaEnrollment.qr_code_base64" style="width: 200px; height: 200px;" />
          </div>
          <div class="text-body2 text-center text-grey-8">
            Se não puder escanear, use a chave: <strong>{{ mfaEnrollment.secret }}</strong>
          </div>
        </q-card-section>
        
        <q-card-section class="q-pt-none" v-if="mfaStep === 2">
          <div class="text-body2 q-mb-md">
            2. Digite o código de 6 dígitos gerado pelo seu aplicativo autenticador para confirmar.
          </div>
          <q-input
            v-model="otpCode"
            label="Código 2FA"
            outlined
            mask="######"
            maxlength="6"
            :rules="[val => val.length === 6 || 'O código deve ter 6 dígitos']"
          />
        </q-card-section>
        
        <q-card-section class="q-pt-none" v-if="mfaStep === 3">
          <div class="text-h6 text-positive">2FA Ativado com Sucesso!</div>
          <div class="text-body2 q-mt-sm">
            Estes são seus **Códigos de Recuperação**. Salve-os em um local seguro. Eles são usados para acessar sua conta se você perder o acesso ao seu aplicativo 2FA.
          </div>
          <q-list bordered separator class="q-mt-md">
            <q-item v-for="(code, index) in recoveryCodes" :key="index">
              <q-item-section class="text-center text-bold">{{ code }}</q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn 
            flat 
            label="Cancelar" 
            color="negative" 
            v-if="mfaStep < 3"
            v-close-popup
            @click="resetMFAFlow" 
            no-caps 
          />
          <q-btn 
            label="Próximo" 
            color="primary" 
            v-if="mfaStep === 1"
            @click="mfaStep = 2" 
            no-caps 
          />
          <q-btn 
            label="Confirmar e Ativar" 
            color="positive" 
            v-if="mfaStep === 2"
            :loading="mfaLoading"
            :disable="otpCode.length !== 6"
            @click="confirmMFA"
            no-caps
          />
          <q-btn 
            label="Entendi" 
            color="primary" 
            v-if="mfaStep === 3"
            v-close-popup
            @click="resetMFAFlow"
            no-caps 
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <q-dialog v-model="mfaDisableDialog">
      <q-card>
        <q-card-section>
          <div class="text-h6">Desativar 2FA</div>
        </q-card-section>
        <q-card-section class="q-pt-none">
          <div class="text-body2 q-mb-md">
            Para desativar a autenticação de dois fatores, digite seu código 2FA atual.
          </div>
          <q-input
            v-model="otpCode"
            label="Código 2FA"
            outlined
            mask="######"
            maxlength="6"
            :rules="[val => val.length === 6 || 'O código deve ter 6 dígitos']"
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Cancelar" v-close-popup no-caps />
          <q-btn 
            label="Desativar" 
            color="negative"
            :loading="mfaLoading"
            :disable="otpCode.length !== 6"
            @click="disableMFA"
            no-caps
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { Notify, useQuasar } from 'quasar';
import { format } from 'date-fns';

// Interface básica para Sessão (baseada na SessionInfo da sua API)
interface SessionInfo {
    id: number;
    ip_address: string;
    user_agent: string;
    created_at: string;
    expires_at: string;
    is_current: boolean;
}

export default defineComponent({
  name: 'SecuritySettingsPage',
  setup() {
    const $q = useQuasar();
    const authStore = useAuthStore();
    
    // --- Lógica de MFA ---
    const mfaEnableDialog = ref(false);
    const mfaDisableDialog = ref(false);
    const mfaStep = ref(1); // 1: Scan, 2: Confirm, 3: Recovery Codes
    const mfaLoading = ref(false);
    const otpCode = ref('');
    const recoveryCodes = ref<string[]>([]);
    const mfaEnrollment = ref({
      secret: '',
      qr_code_base64: '',
    });

    const resetMFAFlow = () => {
      mfaStep.value = 1;
      otpCode.value = '';
      mfaEnrollment.value = { secret: '', qr_code_base64: '' };
      recoveryCodes.value = [];
      mfaEnableDialog.value = false;
      mfaDisableDialog.value = false;
    };
    
    const startMFAEnrollment = async () => {
      mfaLoading.value = true;
      try {
        const response = await authStore.startMFAEnrollment();
        mfaEnrollment.value = response;
        mfaEnableDialog.value = true;
        mfaStep.value = 1;
      } catch (error: any) {
        Notify.create({
          type: 'negative',
          message: error.response?.data?.detail || 'Erro ao iniciar 2FA.',
        });
      } finally {
        mfaLoading.value = false;
      }
    };
    
    const confirmMFA = async () => {
      mfaLoading.value = true;
      try {
        const response = await authStore.confirmMFA(otpCode.value);
        recoveryCodes.value = response.recovery_codes;
        mfaStep.value = 3;
      } catch (error: any) {
        Notify.create({
          type: 'negative',
          message: error.response?.data?.detail || 'Código 2FA inválido ou expirado.',
        });
      } finally {
        mfaLoading.value = false;
      }
    };
    
    const openDisableDialog = () => {
      mfaDisableDialog.value = true;
      otpCode.value = '';
    };

    const disableMFA = async () => {
      mfaLoading.value = true;
      try {
        await authStore.disableMFA(otpCode.value);
        resetMFAFlow();
      } catch (error: any) {
        Notify.create({
          type: 'negative',
          message: error.response?.data?.detail || 'Código 2FA inválido.',
        });
      } finally {
        mfaLoading.value = false;
      }
    };
    
    // --- Lógica de Sessões Ativas ---
    const sessions = ref<SessionInfo[]>([]);
    const loadingSessions = ref(false);
    
    const fetchSessionsAndDevices = async () => {
        loadingSessions.value = true;
        try {
            sessions.value = await authStore.fetchActiveSessions();
            // Associa o token atual ao is_current (feito pela API, mas garante que a lista atual é precisa)
            // Se a API não fizer isso, você pode adicionar a lógica aqui.
            // Ex: sessions.value.forEach(s => s.is_current = (s.token_hash === hash_do_token_local))
        } catch (error: any) {
             Notify.create({
                 type: 'negative',
                 message: error.response?.data?.detail || 'Erro ao buscar sessões ativas.'
             });
        } finally {
            loadingSessions.value = false;
        }
    };

    const logoutSession = (sessionId: number, isCurrent: boolean) => {
        if (isCurrent) return; // Proteção adicional
        
        $q.dialog({
            title: 'Confirmar Encerramento',
            message: 'Tem certeza que deseja encerrar esta sessão? O usuário será desconectado.',
            cancel: true,
            persistent: true
        }).onOk(async () => {
            try {
                await authStore.logoutSpecificSession(sessionId);
                await fetchSessionsAndDevices();
            } catch (error: any) {
                Notify.create({ type: 'negative', message: 'Falha ao encerrar sessão.' });
            }
        });
    };
    
    const logoutAllOtherSessions = () => {
        $q.dialog({
            title: 'Confirmar Encerramento',
            message: 'Tem certeza que deseja encerrar todas as outras sessões (exceto a atual)?',
            cancel: true,
            persistent: true
        }).onOk(async () => {
            try {
                await authStore.logoutAllOtherSessions();
                await fetchSessionsAndDevices();
            } catch (error: any) {
                Notify.create({ type: 'negative', message: 'Falha ao encerrar outras sessões.' });
            }
        });
    };
    
    // Função utilitária de formatação de data
    const formatDate = (dateString: string) => {
        try {
            return format(new Date(dateString), 'dd/MM/yyyy HH:mm:ss');
        } catch {
            return dateString;
        }
    };

    onMounted(() => {
        fetchSessionsAndDevices();
        // Nota: A lógica de fetchTrustedDevices deve ser adicionada aqui.
    });

    return {
      authStore,
      mfaEnableDialog,
      mfaDisableDialog,
      mfaStep,
      mfaLoading,
      otpCode,
      recoveryCodes,
      mfaEnrollment,
      sessions,
      loadingSessions,
      
      resetMFAFlow,
      startMFAEnrollment,
      confirmMFA,
      openDisableDialog,
      disableMFA,
      fetchSessionsAndDevices,
      logoutSession,
      logoutAllOtherSessions,
      formatDate,
      
      // Simulação de configurações para o template (você deve buscar isso da sua API ou config)
      settings: {
          trustedDeviceMaxAgeDays: 30 
      }
    };
  },
});
</script>