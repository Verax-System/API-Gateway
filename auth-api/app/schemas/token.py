# auth_api/app/schemas/token.py
from pydantic import BaseModel
from typing import Literal, List, Optional
from datetime import datetime 

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
    token_type: str | None = None
    amr: Optional[List[str]] = None # Authentication Methods Reference

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# --- NOVOS SCHEMAS PARA O CRUD (ADICIONADO) ---
# Necessário para a definição genérica de CRUDBase[Model, CreateSchema, UpdateSchema]

class RefreshTokenCreate(BaseModel):
    """Schema para criar um Refresh Token. Mínimo, pois a lógica está no CRUD."""
    # O Refresh Token é sempre criado com dados internos (user_id, token, expires_at),
    # mas o Base precisa de um schema válido.
    pass # Pode ser vazio, pois o CRUD lida com a geração do token.

class RefreshTokenUpdate(BaseModel):
    """Schema para atualizar um Refresh Token."""
    is_revoked: bool = False
    
# --- FIM DOS SCHEMAS CRUD ---

# --- Schema: Resposta MFA Obrigatório ---
class MFARequiredResponse(BaseModel):
    """Resposta indicando que a verificação MFA é necessária."""
    detail: Literal["MFA verification required"] = "MFA verification required"
    mfa_challenge_token: str # Um token temporário para a próxima etapa

# --- NOVOS SCHEMAS PARA GOOGLE OAUTH ---

class GoogleLoginUrlResponse(BaseModel):
    """Resposta que contém o URL de autorização da Google."""
    url: str

# --- ADICIONADO DE VOLTA ---
class GoogleLoginRequest(BaseModel):
    """Requisição que o frontend envia para a API com o código da Google."""
    code: str
# --- FIM ADIÇÃO ---

# --- FIM NOVOS SCHEMAS ---

class SessionInfo(BaseModel):
    """Informações sobre uma sessão de login ativa (um refresh token)."""
    id: int
    user_agent: Optional[str]
    ip_address: Optional[str]
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True # Permite mapear diretamente do modelo SQLAlchemy