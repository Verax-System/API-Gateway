#
import os
from pydantic import AnyHttpUrl, EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from loguru import logger

class Settings(BaseSettings):
    # Configuração do Pydantic para ler do .env
    # CORRIGIDO: Adicionado extra='ignore' para Pydantic não falhar
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # Chaves de Segurança e JWT
    SECRET_KEY: str = "UMA_CHAVE_SECRETA_FORTE_PARA_JWT"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Configuração do Banco de Dados
    DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost:5432/auth_db"

    # Configuração do Super Usuário Inicial
    FIRST_SUPERUSER_EMAIL: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "your_strong_password"

    # Configuração de CORS (Cross-Origin Resource Sharing)
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: str | List[str]) -> List[AnyHttpUrl] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Configuração de E-mail (Opcional, para recuperação de senha, etc.)
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str]) -> str:
        if not v:
            return "VeraxAuth API"
        return v

    # Configuração do MFA (Autenticação de Múltiplos Fatores)
    MFA_CHALLENGE_SECRET_KEY: str = "UMA_QUARTA_CHAVE_SECRETA_FORTE"
    MFA_CHALLENGE_EXPIRE_MINUTES: int = 5
    APP_NAME: str = "VeraxAuth"

# --- Carregamento das Configurações ---
try:
    settings = Settings()
except Exception as e:
    # Este é o log de erro que você viu
    logger.error(f"FATAL: Erro ao carregar 'settings' a partir do .env em {os.path.abspath('.env')}: {e}")
    raise e