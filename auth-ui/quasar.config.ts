// quasar.config.ts

import { configure } from 'quasar/wrappers';

export default configure(function (/* ctx */) {
  return {
    // Lista de arquivos de boot, 'axios' deve estar aqui.
    boot: ['axios'],

    // CSS da sua aplicação
    css: ['app.scss'],

    // Pacotes de ícones e fontes
    extras: ['roboto-font', 'material-icons'],

    // Configuração de build
    build: {
      target: {
        browser: ['es2022', 'firefox115', 'chrome115', 'safari14'],
        node: 'node20',
      },
      vueRouterMode: 'hash',
    },

    // Configuração do Servidor de Desenvolvimento (com o proxy)
    devServer: {
      open: true,
      proxy: {
        '/api': {
          target: 'http://localhost:7000',
          changeOrigin: true,
        },
      },
    },

    // --- A CORREÇÃO CRÍTICA E DEFINITIVA ESTÁ AQUI ---
    // Configuração do Framework Quasar
    framework: {
      config: {
        dark: true, // Força o modo escuro
      },
      // Nós registramos os plugins do Quasar AQUI e em nenhum outro lugar.
      plugins: [
        'Notify'
      ],
    },
    // -------------------------------------------------

    // O resto das configurações (ssr, pwa, etc.) pode ser mantido como estava
    // se você precisar delas, ou removido se não for o caso.
    ssr: {
      pwa: false,
      middlewares: ['render'],
    },
    pwa: {
      workboxMode: 'GenerateSW',
    },
  };
});