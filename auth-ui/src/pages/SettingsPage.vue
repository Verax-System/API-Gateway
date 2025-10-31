<template>
  <q-page>
    <div class="q-pa-md">
      <div class="text-h4 q-mb-lg">Configurações do Hub</div>

      <q-card flat bordered class="rounded-borders">
        <q-tabs
          v-model="tab"
          align="left"
          dense
          class="text-grey-7"
          active-color="primary"
          indicator-color="primary"
          no-caps
        >
          <q-route-tab
            name="profile"
            icon="mdi-account-circle-outline"
            label="Perfil & Conta"
            :to="{ name: 'profile-settings' }"
            exact
          />
          
          <q-route-tab
            name="security"
            icon="mdi-shield-lock-outline"
            label="Segurança (2FA & Sessões)"
            :to="{ name: 'security-settings' }"
            exact
          />
        </q-tabs>

        <q-separator />

        <q-card-section>
          <router-view />
        </q-card-section>
      </q-card>
    </div>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

export default defineComponent({
  name: 'SettingsPage',
  setup() {
    const route = useRoute();
    // Usa o nome da rota atual para inicializar a aba correta
    const tab = ref('profile'); 

    // Atualiza a aba ativa se a rota mudar diretamente
    onMounted(() => {
        // Verifica se a rota atual é 'security-settings' ou 'profile-settings'
        if (route.name === 'security-settings') {
            tab.value = 'security';
        } else if (route.name === 'profile-settings') {
            tab.value = 'profile';
        }
    });

    return {
      tab,
    };
  },
});
</script>