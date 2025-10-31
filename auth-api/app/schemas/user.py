from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any, List 
from datetime import datetime
import re

# Função de validação de senha (mantida)
def password_strength_validator(password: str) -> str:
    if len(password) < 8:
        raise ValueError('A senha deve ter pelo menos 8 caracteres')
    if not re.search(r"[a-z]", password):
        raise ValueError('A senha deve conter pelo menos uma letra minúscula')
    if not re.search(r"[A-Z]", password):
        raise ValueError('A senha deve conter pelo menos uma letra maiúscula')
    if not re.search(r"[0-9]", password):
        raise ValueError('A senha deve conter pelo menos um número')
    if not re.search(r"[\W_]", password):
        raise ValueError('A senha deve conter pelo menos um caractere especial')
    return password

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    
    # Adicionando campos aqui para serem herdados e usados nos CRUDs e APIs (Optional)
    is_superuser: Optional[bool] = False 
    is_mfa_enabled: Optional[bool] = False

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return password_strength_validator(v)


class UserUpdate(UserBase):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    
    # Permite atualização de claims (ex: roles)
    custom_claims: Optional[Dict[str, Any]] = None 
    
    @field_validator('password')
    @classmethod
    def validate_update_password_strength(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            return password_strength_validator(v)
        return v

class User(UserBase):
    """Schema de Leitura (UserSchema) - usado em /me"""
    id: int
    
    # Sobrescrever para garantir que são bool e requeridos na saída
    is_active: bool
    is_superuser: bool 
    is_mfa_enabled: bool
    is_verified: bool
    
    created_at: datetime
    updated_at: datetime
    custom_claims: Optional[Dict[str, Any]] = {}

    class Config:
        from_attributes = True

# --- (Restante dos Schemas MFA) ---
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        return password_strength_validator(v)

class MFAEnableResponse(BaseModel):
    """Resposta ao iniciar a habilitação do MFA."""
    otp_uri: str 
    qr_code_base64: str 

class MFAConfirmRequest(BaseModel):
    """Requisição para confirmar a habilitação do MFA."""
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

class MFAConfirmResponse(BaseModel):
    """Resposta ao confirmar MFA com sucesso. Inclui os códigos de recuperação."""
    user: User
    recovery_codes: List[str] = Field(..., description="Guarde estes códigos!")

class MFADisableRequest(BaseModel):
    """Requisição para desabilitar o MFA."""
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

class MFAVerifyRequest(BaseModel):
    """Requisição para verificar o código MFA durante o login."""
    mfa_challenge_token: str 
    otp_code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")

class MFARecoveryRequest(BaseModel):
    """Requisição para usar um código de recuperação durante o login."""
    mfa_challenge_token: str
    recovery_code: str = Field(..., description="Um dos códigos de recuperação de uso único (ex: abc-123)")