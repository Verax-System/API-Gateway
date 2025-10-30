import httpx # ADICIONADO
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_session, get_current_active_superuser
from app.crud.crud_user import crud_user
from app.schemas.user import User, UserCreate, UserUpdate
from app.models.user import User as UserModel

router = APIRouter()

@router.post("/admin/users/", response_model=User, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    *,
    db: AsyncSession = Depends(get_session),
    user_in: UserCreate,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    Admin cria um novo usuário.
    """
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    new_user = await crud_user.create(db, obj_in=user_in)

    # --- INÍCIO DA SINCRONIZAÇÃO (FASE 4) ---
    async with httpx.AsyncClient() as client:
        # Prepara dados seguros para sincronização
        user_data_safe = {
            "email": user_in.email,
            "full_name": user_in.full_name,
            "is_active": user_in.is_active,
            "is_superuser": user_in.is_superuser,
            "password": user_in.password # Envia a senha para o outro sistema criar o hash
        }
        
        # 1. Sincroniza com o 'fleet-api'
        try:
            await client.post(
                "http://gateway/api/fleet/users/internal/sync_user",
                json=user_data_safe,
                timeout=5.0
            )
        except httpx.RequestError as e:
            print(f"ALERTA: Falha ao sincronizar usuário com FLEET-API: {e}")
            pass # Não falha a criação principal

        # 2. Sincroniza com o 'sales-api'
        try:
            await client.post(
                "http://gateway/api/sales/users/internal/sync_user",
                json=user_data_safe,
                timeout=5.0
            )
        except httpx.RequestError as e:
            print(f"ALERTA: Falha ao sincronizar usuário com SALES-API: {e}")
            pass # Não falha a criação principal
    # --- FIM DA SINCRONIZAÇÃO ---

    return new_user

@router.get("/admin/users/", response_model=list[User])
async def admin_read_users(
    db: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    Admin lê todos os usuários.
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/admin/users/{user_id}", response_model=User)
async def admin_read_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    Admin lê um usuário por ID.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/admin/users/{user_id}", response_model=User)
async def admin_update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    Admin atualiza um usuário.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = await crud_user.update(db, db_obj=user, obj_in=user_in)
    
    # TODO: Sincronizar atualização de usuário com outros serviços
    
    return user

@router.delete("/admin/users/{user_id}", response_model=User)
async def admin_delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_active_superuser),
):
    """
    Admin deleta um usuário.
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    deleted_user = await crud_user.remove(db, id=user_id)
    
    # TODO: Sincronizar deleção de usuário com outros serviços
    
    return deleted_user