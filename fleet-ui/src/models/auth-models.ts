// --- Conteúdo Corrigido ---
// Renomeado para LoginCredentials para corrigir o erro de importação na store
export interface LoginCredentials {
  email: string;
  password: string;
}

export type UserRole = 'cliente_ativo' | 'cliente_demo' | 'driver';
export type UserSector = 'agronegocio' | 'frete' | 'servicos' | 'construcao_civil' | null;

export interface Organization {
  id: number;
  name: string;
  sector: UserSector;
}

// Renomeado de 'User' para 'UserProfile' para corrigir o erro de importação na store
export interface UserProfile {
  id: number;
  full_name: string;
  email: string;
  employee_id: string;
  role: UserRole;
  is_active: boolean;
  avatar_url: string | null;
  notify_in_app: boolean;
  notify_by_email: boolean;
  notification_email: string | null;
  organization: Organization;
  is_superuser?: boolean;
}

export interface TokenData {
  access_token: string;
  token_type: string;
  user: UserProfile;
}

// O nome real para a requisição de recuperação de senha (apenas email)
export interface PasswordRecoveryRequest {
  email: string;
}

// O nome que a store estava usando para o reset final (token + nova senha)
export interface PasswordResetData {
  token: string;
  new_password: string;
}

// Interface que a store estava importando
export interface PasswordResetRequest {
  token: string;
  new_password: string;
}

export interface UserRegister {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
  sector: UserSector;
}