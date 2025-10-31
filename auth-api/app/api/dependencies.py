# auth_api/app/api/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
import secrets 

from app.db.session import get_db
from app.core.config import settings

# --- CORREÇÕES CRÍTICAS AQUI ---
# 1. Importar o MODELO com um alias (UserModel) para evitar conflito.
from app.models.user import User as UserModel
# 2. Importar a INSTÂNCIA CRUD (que tem os métodos .get e .get_by_email)
from app.crud.crud_user import crud_user 
# --- FIM CORREÇÕES CRÍTICAS ---

from app.schemas.token import TokenPayload
from app.core import security # Necessário para security.decode_access_token

# Define oauth2_scheme (Para o endpoint /token - Password Flow)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token") 

# --- ESQUEMAS DE SEGURANÇA ---
bearer_scheme = HTTPBearer(
    description="Insira o Access Token JWT (com 'Bearer ') e.g. 'Bearer eyJ...'"
)
api_key_scheme = APIKeyHeader(name="X-API-Key", description="Chave de API para endpoints /mgmt")
# --- FIM ESQUEMAS ---


# --- FUNÇÃO 1: PARA O LOGIN /TOKEN (usa OAuth2PasswordBearer) ---
async def get_current_user(
    db: AsyncSession = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    """Busca o usuário através do token do Password Flow (OAuth2PasswordBearer)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        token_data = TokenPayload(sub=email)

    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Usa a instância CRUD para buscar o usuário
    user = await crud_user.get_by_email(db, email=token_data.sub)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found or requires synchronization.",
        )
    return user


# --- FUNÇÃO 2: PARA OS ENDPOINTS PROTEGIDOS (usa HTTPBearer) ---
async def get_current_user_from_token(
    db: AsyncSession = Depends(get_db),
    # Obtém o token do header 'Authorization: Bearer <token>'
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UserModel:
    """Busca o usuário através do token de Access (HTTPBearer)."""
    
    # ATENÇÃO: O erro anterior foi resolvido removendo a importação circular incorreta aqui.
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esquema de autorização inválido. Use 'Bearer'.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = creds.credentials
    payload = security.decode_access_token(token)
    
    if payload is None:
        raise credentials_exception

    user_id_str = payload.get("sub") # Supondo que o SUB do access token é o ID do usuário
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception # ID inválido

    # ESTA ERA A LINHA QUE ESTAVA A FALHAR (L149 NO SEU TRACEBACK)
    # user = await crud_user.get(db, id=user_id) 
    # Agora, o 'crud_user' é a instância CRUD importada no topo.
    user = await crud_user.get(db, id=user_id) 
    
    if user is None:
        raise credentials_exception
    return user


# --- DEPENDÊNCIAS FINAIS ---

async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user_from_token),
) -> UserModel:
    if not current_user.is_active:
        # A inatividade deve, pela lógica de segurança moderna, ser 403 ou 401. 
        # Mantendo 400 se for a convenção do seu projeto, mas 403 é mais comum 
        # para "o token é válido, mas o utilizador não tem permissão de ativo."
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Mude get_current_active_superuser para:
async def get_current_active_superuser(
    current_user: UserModel = Depends(get_current_user_from_token),
) -> UserModel:
    if not current_user.is_superuser:
        # 403 Forbidden é o status correto para "token é válido, mas o utilizador não tem o papel/privilégio"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    """
    Dependência que verifica se o usuário ativo possui a role 'admin'
    em seus custom_claims (RBAC).
    """
    forbidden_exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Não autorizado. Requer privilégios de administrador.",
    )

    if not current_user.custom_claims:
        raise forbidden_exception

    roles = current_user.custom_claims.get("roles")
    
    if not roles or not isinstance(roles, list) or "admin" not in roles:
        raise forbidden_exception
        
    return current_user

async def get_api_key(api_key: str = Depends(api_key_scheme)) -> str:
    """
    Verifica se a X-API-Key enviada no header é válida.
    """
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="INTERNAL_API_KEY não está configurada no servidor",
        )
    
    if not secrets.compare_digest(api_key, settings.INTERNAL_API_KEY):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida ou ausente",
        )
    return api_key