<template>
  <q-page class="q-pa-md">
    <div class="text-h6 q-mb-md">Informações do Perfil</div>

    <q-card flat bordered class="q-mb-lg">
      <q-card-section>
        <div class="text-subtitle1 text-primary">Atualizar Nome e Email</div>
      </q-card-section>
      
      <q-card-section class="q-pt-none">
        <q-form @submit="updateBasicInfo">
          <q-input
            v-model="fullName"
            label="Nome Completo"
            :hint="`Atual: ${authStore.user?.full_name}`"
            outlined
            dense
            class="q-mb-md"
            :rules="[val => !!val || 'O nome é obrigatório']"
          />
          <q-input
            v-model="email"
            label="E-mail"
            :hint="`Atual: ${authStore.user?.email}`"
            type="email"
            outlined
            dense
            class="q-mb-md"
            :rules="[
              val => !!val || 'O e-mail é obrigatório', 
              val => /.+@.+\..+/.test(val) || 'E-mail inválido'
            ]"
          />
          
          <q-btn
            type="submit"
            label="Salvar Alterações"
            color="primary"
            :loading="loadingInfo"
            no-caps
            class="q-mt-md"
          />
        </q-form>
      </q-card-section>
    </q-card>

    <q-card flat bordered>
      <q-card-section>
        <div class="text-subtitle1 text-primary">Alterar Senha</div>
      </q-card-section>
      
      <q-card-section class="q-pt-none">
        <q-form @submit="updatePassword">
          <q-input
            v-model="currentPassword"
            type="password"
            label="Senha Atual"
            outlined
            dense
            class="q-mb-md"
            :rules="[val => !!val || 'Senha atual é obrigatória']"
          />
          <q-input
            v-model="newPassword"
            type="password"
            label="Nova Senha"
            outlined
            dense
            class="q-mb-md"
            :rules="[
              val => !!val || 'Nova senha é obrigatória', 
              val => val.length >= 8 || 'Mínimo de 8 caracteres'
            ]"
          />
          <q-input
            v-model="confirmPassword"
            type="password"
            label="Confirmar Nova Senha"
            outlined
            dense
            class="q-mb-md"
            :rules="[
              val => !!val || 'Confirmação é obrigatória',
              val => val === newPassword || 'As senhas não coincidem'
            ]"
          />
          
          <q-btn
            type="submit"
            label="Alterar Senha"
            color="primary"
            :loading="loadingPassword"
            no-caps
            class="q-mt-md"
          />
        </q-form>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, watch } from 'vue';
import { useAuthStore } from 'src/stores/auth-store';
import { Notify } from 'quasar';

export default defineComponent({
  name: 'ProfileSettingsPage',
  setup() {
    const authStore = useAuthStore();
    
    // --- Dados de Informações Básicas ---
    const fullName = ref(authStore.user?.full_name || '');
    const email = ref(authStore.user?.email || '');
    const loadingInfo = ref(false);

    // Garante que os campos são populados se o usuário for carregado mais tarde (após reload)
    watch(() => authStore.user, (newUser) => {
      if (newUser) {
        fullName.value = newUser.full_name;
        email.value = newUser.email;
      }
    }, { immediate: true });


    const updateBasicInfo = async () => {
        loadingInfo.value = true;
        try {
            await authStore.updateUserProfile({
                full_name: fullName.value,
                email: email.value,
            });
            // O store já envia o Notify de sucesso
        } catch (error: any) {
            Notify.create({
                type: 'negative',
                message: error.response?.data?.detail || 'Falha ao atualizar informações.',
            });
        } finally {
            loadingInfo.value = false;
        }
    };
    
    // --- Dados de Senha ---
    const currentPassword = ref('');
    const newPassword = ref('');
    const confirmPassword = ref('');
    const loadingPassword = ref(false);

    const updatePassword = async () => {
        if (newPassword.value !== confirmPassword.value) return; // Regra de validação no campo

        loadingPassword.value = true;
        try {
            await authStore.updateUserProfile({
                current_password: currentPassword.value,
                new_password: newPassword.value,
            });
            // Limpa os campos após o sucesso
            currentPassword.value = '';
            newPassword.value = '';
            confirmPassword.value = '';
            // O store já envia o Notify de sucesso
        } catch (error: any) {
             Notify.create({
                type: 'negative',
                message: error.response?.data?.detail || 'Falha ao alterar senha. Verifique a senha atual.',
            });
        } finally {
            loadingPassword.value = false;
        }
    };

    return {
      authStore,
      fullName,
      email,
      loadingInfo,
      updateBasicInfo,
      
      currentPassword,
      newPassword,
      confirmPassword,
      loadingPassword,
      updatePassword,
    };
  },
});
</script>