from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_session, get_current_active_user
from app.crud.crud_user import crud_user
from app.schemas.user import User, UserCreate, UserUpdate
from app.core.security import get_password_hash # Importado para hashear senha
from app.models.user import User as UserModel # Importado para o endpoint de sync

router = APIRouter()

# --- NOVO ENDPOINT DE SINCRONIZAÇÃO (FASE 4) ---
@router.post("/internal/sync_user", response_model=User, status_code=status.HTTP_201_CREATED)
async def sync_user_profile(
    *,
    db: AsyncSession = Depends(get_session),
    user_in: UserCreate,
):
    """
    Endpoint interno para o auth-api criar um perfil de usuário local.
    """
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        return user
    
    # Cria um usuário básico no sistema de vendas
    hashed_password = get_password_hash(user_in.password)
    user_create_data = user_in.model_dump()
    user_create_data["hashed_password"] = hashed_password
    del user_create_data["password"] # Remove a senha em texto plano
    
    # Cria o usuário com os dados e senha hasheada
    db_obj = UserModel(**user_create_data)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

# --- FIM DO NOVO ENDPOINT ---


@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get current user.
    """
    return current_user

@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_in: UserCreate,
):
    """
    Create new user.
    """
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud_user.create(db, obj_in=user_in)
    
    # TODO: Sincronizar este usuário de volta para o auth-api?
    # (Atualmente, a criação só deve acontecer pelo Hub)
    
    return user

@router.get("/", response_model=list[User])
async def read_users(
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """
    Retrieve users.
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=User)
async def read_user_by_id(
    user_id: str,
    db: AsyncSession = Depends(get_session),
):
    """
    Get a specific user by id.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: str,
    user_in: UserUpdate,
):
    """
    Update a user.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = await crud_user.update(db, db_obj=user, obj_in=user_in)
    return user

@router.delete("/{user_id}", response_model=User)
async def delete_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_id: str,
):
    """
    Delete a user.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = await crud_user.remove(db, id=user_id)
    return user