# auth_api/app/api/dependencies.py
from fastapi import Depends, HTTPException, status
# IMPORTAR HTTPBearer e HTTPAuthorizationCredentials
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from app.models.user import User
from jose import jwt, JWTError
from pydantic import ValidationError

from app.crud.crud_user import user as crud_user
from app.schemas.token import TokenPayload
import secrets # Importar secrets para comparação segura

# Remover import do logger
# from loguru import logger 

from app.core import security
# --- CORRECTION HERE: Remove AsyncSessionLocal import ---
from app.db.session import get_db  # <--- CORREÇÃO
# --- END CORRECTION ---
from app.models.user import User as UserModel
# --- CORREÇÃO (IMPORTAÇÃO CIRCULAR) ---
# REMOVIDO: from app.crud.crud_user import user as crud_user
# Esta importação será movida para dentro da função 'get_current_user_from_token'
# --- FIM DA CORREÇÃO ---
from app.core.config import settings # Importar settings

# Define oauth2_scheme (ISTO SERÁ USADO APENAS PELO ENDPOINT /token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") 

# --- NOVO ESQUEMA BEARER ---
# Este esquema será usado por TODOS os endpoints protegidos
# Ele diz ao Swagger "apenas peça um token Bearer"
bearer_scheme = HTTPBearer(
    description="Insira o Access Token JWT (com 'Bearer ') e.g. 'Bearer eyJ...'"
)
# --- FIM NOVO ESQUEMA ---

# --- DEPENDÊNCIA DA CHAVE DE API (X-API-Key) ---
api_key_scheme = APIKeyHeader(name="X-API-Key", description="Chave de API para endpoints /mgmt")
# --- FIM DEPENDÊNCIA ---

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme) # <-- CORREÇÃO: Usando get_db
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # CORREÇÃO: Usa a chave e algoritmo do Hub (FASE 1)
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # O 'sub' do token é o email do usuário
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        token_data = TokenPayload(sub=email)

    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Busca o usuário no banco de dados LOCAL do sales-api
    user = await crud_user.get_by_email(db, email=token_data.sub)
    
    if user is None:
        # Se o usuário é válido mas não existe no DB local, ele não foi sincronizado
        raise HTTPException(
            status_code=status.HTTP_44_NOT_FOUND, # Erro 404
            detail="User profile not found in Sales system. Needs sync.",
        )
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

# --- get_current_user logic (MODIFICADA) ---
async def get_current_user_from_token(
    db: AsyncSession = Depends(get_db),
    # MODIFICADO: Trocar de Depends(oauth2_scheme) para Depends(bearer_scheme)
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UserModel:
    
    # --- CORREÇÃO (IMPORTAÇÃO CIRCULAR) ---
    # A importação do crud_user foi movida para aqui para quebrar o loop
    from app.crud.crud_user import user as crud_user
    # --- FIM DA CORREÇÃO ---

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        # ATUALIZADO: O header para o HTTPBearer
        headers={"WWW-Authenticate": "Bearer"},
    )

    # credentials.scheme deve ser "Bearer"
    if creds.scheme.lower() != "bearer":
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esquema de autorização inválido. Use 'Bearer'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # credentials.credentials é o token
    token = creds.credentials
    
    # --- LOG DE DEBUG REMOVIDO ---
    # logger.debug(f"Recebido para decodificação - Scheme: '{creds.scheme}', Token: '{token}'")
    # --- FIM LOG DE DEBUG ---

    payload = security.decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
         user_id = int(user_id_str)
    except ValueError:
         raise credentials_exception

    user = await crud_user.get(db, id=user_id)
    if user is None:
        raise credentials_exception
    return user



# ELA ESTÁ AQUI E SEMPRE ESTEVE! O ERRO É CAUSADO PELO LOOP ACIMA.
async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user_from_token),
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- NOVA DEPENDÊNCIA DE ADMIN (RBAC) ---
async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    """
    Dependência que verifica se o usuário ativo possui a role 'admin'
    em seus custom_claims.
    """
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Não autorizado. Requer privilégios de administrador.",
    )

    if not current_user.custom_claims:
        # Se custom_claims for None ou {}
        raise forbidden_exception

    roles = current_user.custom_claims.get("roles")
    
    if not roles or not isinstance(roles, list) or "admin" not in roles:
        # Se 'roles' não existir,
        # ou não for uma lista,
        # ou 'admin' não estiver na lista
        raise forbidden_exception
        
    return current_user
# --- FIM NOVA DEPENDÊNCIA ---


# --- DEPENDÊNCIA DA CHAVE DE API (X-API-Key) ---
async def get_api_key(api_key: str = Depends(api_key_scheme)) -> str:
    """
    Verifica se a X-API-Key enviada no header é válida.
    """
    if not settings.INTERNAL_API_KEY:
        # Erro de segurança: a chave nem está configurada no servidor
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_API_KEY não está configurada no servidor",
        )
    # Compara as chaves de forma segura para evitar timing attacks
    if not secrets.compare_digest(api_key, settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida ou ausente",
        )
    return api_key
# --- FIM DEPENDÊNCIA DA CHAVE DE API ---