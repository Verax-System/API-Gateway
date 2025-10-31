<template>
  </template>

<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from 'stores/auth-store';
import { useRouter } from 'vue-router';

const email = ref('');
const isLoading = ref(false);
const authStore = useAuthStore();
const router = useRouter();

async function handleRecoveryRequest() {
  if (isLoading.value) return;
  isLoading.value = true;
  
  try {
    // A tipagem já foi corrigida no auth-store.ts para esperar PasswordRecoveryRequest
    await authStore.requestPasswordReset({ email: email.value });
    // A notificação de sucesso já é exibida pela store
    setTimeout(() => {
      // Redireciona para o login após um tempo para o usuário ver a notificação
      void router.push({ name: 'login' }); // CORREÇÃO: Usando 'void' para o floating promise
    }, 4000);
  } finally {
    isLoading.value = false;
  }
}
</script>

<style lang="scss" scoped>
/* ESTILOS INALTERADOS */
.main-container {
  background-image: url('~assets/login-background.jpg');
  background-size: cover;
  background-position: center;
  overflow: hidden;
  position: relative;
}

.background-video {
  position: absolute;
  top: 50%;
  left: 50%;
  min-width: 105%;
  min-height: 105%;
  width: auto;
  height: auto;
  z-index: 1;
  transform: translateX(-50%) translateY(-50%) scale(1.1);
  transition: transform 0.3s ease-out;
}

.video-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(ellipse at center, rgba(5, 10, 20, 0.4) 0%, rgba(5, 10, 20, 0.9) 100%);
  z-index: 2;
}

.login-card-container {
  perspective: 1500px;
  z-index: 3;
}

.login-card {
  width: 420px;
  max-width: 90vw;
  background: rgba(18, 23, 38, 0.5);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: transform 0.3s ease-out;
  position: relative;
  overflow: hidden;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
.animated-form-element {
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

:deep(.q-field--standout.q-field--focused .q-field__control) {
  box-shadow: 0 0 10px rgba(var(--q-color-primary-rgb), 0.5);
}
:deep(.q-field--standout .q-field__control) {
  transition: box-shadow 0.3s ease;
}
</style>