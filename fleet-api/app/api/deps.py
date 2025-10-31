from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.models.user_model import User
from app.crud.crud_user import User as crud_user
from app.schemas.token_schema import TokenPayload # Garantido que TokenPayload existe
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.crud_demo_usage import demo_usage as crud_demo_usage


# tokenUrl agora é apenas nominal
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# --- DEFINIÇÃO DE CONSTANTES DE LIMITE DE DEMO ---
# Estes limites são usados pelo dashboard e check_demo_limit, baseando-se em settings
DEMO_TOTAL_LIMITS = {
    "vehicles": getattr(settings, 'DEMO_LIMIT_VEHICLES', 5),
    "clients": getattr(settings, 'DEMO_LIMIT_CLIENTS', 5),
    "implements": getattr(settings, 'DEMO_LIMIT_IMPLEMENTS', 5),
    "users": getattr(settings, 'DEMO_LIMIT_USERS', 5),
    "parts": getattr(settings, 'DEMO_LIMIT_PARTS', 20),
}

DEMO_MONTHLY_LIMITS = {
    "maintenance_requests": getattr(settings, 'DEMO_LIMIT_MAINTENANCE', 10),
    "journeys": getattr(settings, 'DEMO_LIMIT_JOURNEYS', 100),
    "fuel_logs": getattr(settings, 'DEMO_LIMIT_FUEL_LOGS', 15),
    "fines": getattr(settings, 'DEMO_LIMIT_FINES', 5),
}
# --- FIM DAS CONSTANTES ---


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
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
    
    # Busca o usuário no banco de dados LOCAL do fleet-api
    user = crud_user.get_by_email(db, email=token_data.sub)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found in Fleet system. Needs sync.",
        )
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# CORREÇÃO: Implementação da dependência ausente
def get_current_active_manager(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Dependência para garantir que o usuário ativo seja um gestor ou superusuário.
    """
    if not (current_user.is_manager or current_user.is_superuser):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

def get_current_active_manager_or_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    if not (current_user.is_manager or current_user.is_superuser):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

def check_demo_limit(resource_type: str):
    """
    Cria uma dependência para verificar se uma organização DEMO excedeu 
    o limite de criação para o recurso especificado.
    """
    async def limit_checker(
        db: AsyncSession = Depends(get_db), 
        current_user: User = Depends(get_current_active_user)
    ):
        is_demo = getattr(current_user.organization, 'is_demo', False)
        if not is_demo:
            return 

        limit = 0
        
        if resource_type in DEMO_TOTAL_LIMITS:
            limit = DEMO_TOTAL_LIMITS[resource_type]
        elif resource_type in DEMO_MONTHLY_LIMITS:
            limit = DEMO_MONTHLY_LIMITS[resource_type]
        else:
            return 

        current_usage = await crud_demo_usage.get_or_create_usage(
            db, organization_id=current_user.organization_id, resource_type=resource_type
        )

        if current_usage.usage_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Limite de {limit} {resource_type} excedido para conta DEMO. Por favor, atualize sua assinatura.",
            )
        
    return limit_checker
