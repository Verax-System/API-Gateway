import { defineStore } from 'pinia';
import type { UserSector } from 'src/models/auth-models';
import { AgroStrategy, ServicesStrategy, ConstructionStrategy, FreightStrategy } from 'src/sector-strategies';
import type { ISectorStrategy } from 'src/sector-strategies/strategy.interface';

// Definimos o tipo do estado para ajudar o TypeScript
interface TerminologyState {
  currentSector: UserSector;
}

export const useTerminologyStore = defineStore('terminology', {
  state: (): TerminologyState => ({
    currentSector: null,
  }),

  getters: {
    // Getter principal que define a estratégia
    activeStrategy(state): ISectorStrategy {
      switch (state.currentSector) {
        case 'agronegocio':
          return AgroStrategy;
        case 'construcao_civil':
          return ConstructionStrategy;
        case 'servicos':
          return ServicesStrategy;
        case 'frete':
          return FreightStrategy;
        default:
          return ServicesStrategy;
      }
    },
    
    // --- CORREÇÃO: Adicionando os getters que estavam faltando ---
    fleetNoun(): string { return this.activeStrategy.fleetNoun; }, // NOVO
    implementNounPlural(): string { return this.activeStrategy.implementNounPlural; }, // NOVO
    // --- FIM CORREÇÃO ---
    
    // Todos os outros getters agora usam 'this' para aceder ao getter 'activeStrategy'
    vehicleNoun(): string { return this.activeStrategy.vehicleNoun; },
    vehicleNounPlural(): string { return this.activeStrategy.vehicleNounPlural; },
    journeyNoun(): string { return this.activeStrategy.journeyNoun; },
    journeyNounPlural(): string { return this.activeStrategy.journeyNounPlural; },
    distanceUnit(): string { return this.activeStrategy.distanceUnit; },
    plateOrIdentifierLabel(): string { return this.activeStrategy.plateOrIdentifierLabel; },
    startJourneyButtonLabel(): string { return this.activeStrategy.startJourneyButtonLabel; },
    vehiclePageTitle(): string { return this.activeStrategy.vehiclePageTitle; },
    addVehicleButtonLabel(): string { return this.activeStrategy.addVehicleButtonLabel; },
    editButtonLabel(): string { return this.activeStrategy.editButtonLabel; },
    newButtonLabel(): string { return this.activeStrategy.newButtonLabel; },
    journeyPageTitle(): string { return this.activeStrategy.journeyPageTitle; },
    journeyHistoryTitle(): string { return this.activeStrategy.journeyHistoryTitle; },
    journeyStartSuccessMessage(): string { return this.activeStrategy.journeyStartSuccessMessage; },
    journeyEndSuccessMessage(): string { return this.activeStrategy.journeyEndSuccessMessage; },
  },

  actions: {
    setSector(sector: UserSector) {
      this.currentSector = sector;
    },
  },
});