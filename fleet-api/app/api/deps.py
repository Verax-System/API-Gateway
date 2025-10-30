from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.config import settings
from app.models.user_model import User
from app.crud.crud_user import crud_user
from app.schemas.token_schema import TokenPayload

# tokenUrl agora é apenas nominal
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        
        token_data = TokenPayload(sub=email)

    except (JWTError, ValidationError):
        raise credentials_exception
    
    # Busca o usuário no banco de dados LOCAL do fleet-api
    user = crud_user.get_by_email(db, email=token_data.sub)
    
    if user is None:
        # Se o usuário é válido mas não existe no DB local, ele não foi sincronizado
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