// src/router/router-plugin.ts
import 'pinia';
import type { Router } from 'vue-router';

// Estendemos a interface do Pinia para que o TypeScript saiba que `this.router` existe
declare module 'pinia' {
  export interface PiniaCustomProperties {
    routes: Router;
  }
}

// O plugin em si, que será "usado" pela nossa aplicação
export const routerPlugin = (router: Router) => () => ({
  router,
});