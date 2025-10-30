from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import Any, List, Optional
from app.api import deps
from app.crud.crud_user import crud_user
from app.schemas.user_schema import User, UserCreate, UserUpdate
# from app.core.security import get_password_hash # Não é necessário, o crud_user faz
from app.models.user_model import User as UserModel
from app.services.file_service import save_upload_file

router = APIRouter()

# --- NOVO ENDPOINT DE SINCRONIZAÇÃO (FASE 4) ---
@router.post("/internal/sync_user", response_model=User, status_code=status.HTTP_201_CREATED)
def sync_user_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
):
    """
    Endpoint interno para o auth-api criar um perfil de usuário local.
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        return user
    
    # Cria um usuário básico no sistema de frota
    # O crud_user.create já lida com o hash da senha
    user = crud_user.create(db, obj_in=user_in)
    return user

# --- FIM DO NOVO ENDPOINT ---


@router.get("/me", response_model=User)
def read_users_me(
    current_user: UserModel = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Create new user. (Apenas SuperUser)
    """
    user = crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = crud_user.create(db, obj_in=user_in)
    
    # TODO: Sincronizar este usuário de volta para o auth-api
    # (Atualmente, a criação só deve acontecer pelo Hub)
    
    return user

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_manager_or_superuser)
) -> Any:
    """
    Retrieve users.
    """
    users = crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(deps.get_db),
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    current_user: UserModel = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update own user.
    """
    user_in = UserUpdate()
    if password:
        user_in.password = password
    if full_name:
        user_in.full_name = full_name
    if email:
        user_in.email = email
    
    if avatar:
        avatar_path = save_upload_file(upload_file=avatar, destination="avatars")
        user_in.avatar_url = avatar_path

    user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user

@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: UserModel = Depends(deps.get_current_active_manager_or_superuser)
) -> Any:
    """
    Get a specific user by id.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
def update_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Update a user.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud_user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=User)
def delete_user(
    *,
    db: Session = Depends(deps.get_db),
    user_id: int,
    current_user: UserModel = Depends(deps.get_current_active_superuser)
) -> Any:
    """
    Delete a user.
    """
    user = crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = crud_user.remove(db, id=user_id)
    return user