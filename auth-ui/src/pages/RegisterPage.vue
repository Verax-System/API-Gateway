<template>
  <q-page 
    class="flex flex-center" 
    style="
      background-color: #f0f4f8; 
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
      background-size: 20px 20px;
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
        
        <div class="text-h4 text-positive text-weight-bold">
          Crie Sua Conta
        </div>
        <div class="text-subtitle1 text-grey-7 q-mt-sm q-mb-lg">
          Junte-se à plataforma Verax Hub hoje!
        </div>
      </q-card-section>
      
      <q-card-section>
        <q-form @submit="handleRegister" class="q-gutter-md">
          
          <q-input
            v-model="fullName"
            label="Nome Completo"
            filled
            clearable
            :rules="[val => !!val || 'O nome é obrigatório']"
          >
            <template v-slot:prepend>
              <q-icon name="person_outline" />
            </template>
          </q-input>

          <q-input
            v-model="email"
            label="E-mail"
            type="email"
            filled
            clearable
            :rules="[
              val => !!val || 'O e-mail é obrigatório',
              val => /.+@.+\..+/.test(val) || 'E-mail inválido'
            ]"
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
            :rules="[
              val => !!val || 'A senha é obrigatória',
              val => val.length >= 8 || 'Mínimo de 8 caracteres'
            ]"
          >
            <template v-slot:prepend>
              <q-icon name="lock_outline" />
            </template>
          </q-input>
          
          <q-input
            v-model="confirmPassword"
            label="Confirmar Senha"
            type="password"
            filled
            :rules="[
              val => !!val || 'A confirmação é obrigatória',
              val => val === password || 'As senhas não coincidem'
            ]"
          >
            <template v-slot:prepend>
              <q-icon name="lock_reset" />
            </template>
          </q-input>
          
          <q-btn
            type="submit"
            label="Criar Conta"
            color="positive"
            class="full-width q-py-sm q-mt-lg text-weight-bold"
            rounded
            :loading="loading"
            no-caps
          />
          
        </q-form>
      </q-card-section>
      
      <q-card-section class="text-center q-pt-none">
        <div class="text-body2 text-grey-7">
          Já tem uma conta? 
          <q-btn
            flat
            dense
            label="Entrar"
            color="primary"
            :to="{ name: 'login' }"
            no-caps
            padding="none"
          />
        </div>
      </q-card-section>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import { useRouter } from 'vue-router';
import { api } from 'src/boot/axios';
import { Notify } from 'quasar';

export default defineComponent({
  name: 'RegisterPage',
  setup() {
    const router = useRouter();
    const fullName = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const loading = ref(false);

    const handleRegister = async () => {
      loading.value = true;
      try {
        // Envia a requisição POST para o endpoint de criação de usuário
        await api.post('/api/v1/users/', {
          email: email.value,
          password: password.value,
          full_name: fullName.value,
          // A API deve lidar com a criação de um usuário padrão (não superuser)
        });

        Notify.create({
          type: 'positive',
          message: 'Conta criada com sucesso! Verifique seu e-mail para ativar a conta.',
        });

        // Redireciona para a página de login
        await router.push({ name: 'login' });

      } catch (error: any) {
        let errorMessage = 'Falha ao criar a conta. Tente novamente.';
        
        if (error.response && error.response.status === 400) {
            // Se o erro for 400 (Bad Request), a API geralmente retorna o motivo (ex: email já existe)
            errorMessage = error.response.data?.detail || 'E-mail já registrado ou dados inválidos.';
        }
        
        Notify.create({
          type: 'negative',
          message: errorMessage,
        });

      } finally {
        loading.value = false;
      }
    };

    return {
      fullName,
      email,
      password,
      confirmPassword,
      loading,
      handleRegister,
    };
  },
});
</script>