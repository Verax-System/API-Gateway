<template>
  <q-page padding>
    <div class="text-h5 q-mb-md text-primary text-weight-bold">Configurações da Conta</div>
    <q-separator class="q-mb-lg" />
    
    <div class="row q-col-gutter-lg">
      <div class="col-12 col-md-3">
        <q-card flat bordered>
          <q-list separator>
            <q-item-label header>Opções</q-item-label>
            
            <q-item clickable v-ripple 
                    :active="$route.name === 'profile-settings'" 
                    :to="{ name: 'profile-settings' }" 
                    active-class="bg-blue-1 text-primary text-weight-bold">
              <q-item-section avatar><q-icon name="person" /></q-item-section>
              <q-item-section>Meu Perfil</q-item-section>
            </q-item>
            
            <q-item clickable v-ripple 
                    :active="$route.name === 'security-settings'" 
                    :to="{ name: 'security-settings' }"
                    active-class="bg-blue-1 text-primary text-weight-bold">
              <q-item-section avatar><q-icon name="security" /></q-item-section>
              <q-item-section>Segurança (2FA)</q-item-section>
            </q-item>
            
            <q-separator />

            <q-item-label header>Organização</q-item-label>
            <q-item clickable v-ripple>
              <q-item-section avatar><q-icon name="apartment" /></q-item-section>
              <q-item-section>Detalhes da Empresa</q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
      
      <div class="col-12 col-md-9">
        <router-view />
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Nenhuma lógica necessária aqui, é um componente de layout/navegação.
</script>