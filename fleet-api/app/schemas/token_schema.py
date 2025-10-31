from pydantic import BaseModel
from typing import Optional

from .user_schema import UserPublic

# --- CORREÇÃO: Adicionando a classe TokenPayload faltante ---
class TokenPayload(BaseModel):
    sub: Optional[str] = None # O campo 'sub' é o email ou ID do usuário no JWT
# -----------------------------------------------------------

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    access_token: str
    token_type: str
    user: UserPublic