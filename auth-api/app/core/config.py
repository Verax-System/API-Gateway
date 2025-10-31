# auth-api/app/core/config.py
import os
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, EmailStr, validator
from typing import List, Optional, Union
from loguru import logger
import base64

class Settings(BaseSettings):
    # --- CORE ---
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Verax Auth API"
    
    # --- DATABASE ---
    DATABASE_URL: str
    
    # --- SECURITY & JWT ---
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    
    # --- ADMIN USER ---
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    # --- CORS ---
    BACKEND_CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

    # --- Chaves Secretas (do .env) ---
    REFRESH_SECRET_KEY: str
    RESET_PASSWORD_SECRET_KEY: str
    MFA_CHALLENGE_SECRET_KEY: str
    INTERNAL_API_KEY: str
    
    # --- Duração dos Tokens (do .env) ---
    REFRESH_TOKEN_EXPIRE_DAYS: int
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int
    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int
    MFA_CHALLENGE_EXPIRE_MINUTES: int

    # --- EMAIL SETTINGS (Brevo - do .env) ---
    BREVO_API_KEY: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "noreply@verax.com"
    EMAILS_FROM_NAME: Optional[str] = "Verax Auth"
    VERIFICATION_URL_BASE: Optional[AnyHttpUrl] = None
    RESET_PASSWORD_URL_BASE: Optional[AnyHttpUrl] = None

    # --- ACCOUNT LOCKOUT (do .env) ---
    LOGIN_MAX_FAILED_ATTEMPTS: int
    LOGIN_LOCKOUT_MINUTES: int

    # --- OIDC JWT Claims (do .env) ---
    JWT_ISSUER: str
    JWT_AUDIENCE: str

    # --- MFA / TRUSTED DEVICE (do .env) ---
    TRUSTED_DEVICE_COOKIE_NAME: str
    TRUSTED_DEVICE_COOKIE_MAX_AGE_DAYS: int

    # --- GOOGLE OAUTH (do .env) ---
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI_FRONTEND: Optional[AnyHttpUrl] = None

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = 'utf-8'

try:
    settings = Settings()
except Exception as e:
    logger.error(f"Erro ao carregar configurações: {e}")
    # Lança a excepção original para que o log seja claro
    raise e