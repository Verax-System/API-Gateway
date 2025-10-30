// src/main.ts

import { createApp } from 'vue';
import { Quasar } from 'quasar'; // Importamos apenas o Quasar
import { createPinia } from 'pinia';
import { routerPlugin } from './router/router-plugin';

// Importe os estilos e ícones
import '@quasar/extras/material-icons/material-icons.css';
import 'quasar/src/css/index.sass';

import App from './App.vue';
import createRouter from './router';

async function startApp() {
  const myApp = createApp(App);

  // O Quasar agora é usado de forma simples. Ele lerá a configuração
  // do quasar.config.ts automaticamente, incluindo o plugin Notify.
  myApp.use(Quasar, {});

  const pinia = createPinia();
  myApp.use(pinia);
  
  const router = await createRouter({ store: pinia });
  
  pinia.use(routerPlugin(router));

  myApp.use(router);

  myApp.mount('#q-app');
}

void startApp();