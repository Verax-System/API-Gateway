from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
# --- IMPORTAR A NOVA DEPENDÊNCIA DE ADMIN ---
from app.api.dependencies import get_current_active_user, get_current_admin_user
# --- FIM IMPORTAÇÃO ---
from app.crud.crud_user import crud_user
from app.db.session import get_db
from app.schemas.user import User as UserSchema, UserCreate, UserUpdate, EmailRequest # Importado EmailRequest
# Importar dependência de autenticação do módulo auth
from app.models.user import User as UserModel
from app.services.email_service import send_verification_email # Importar serviço de email
from fastapi import BackgroundTasks # Importar BackgroundTasks~
from loguru import logger

router = APIRouter()

@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
async def resend_verification_email(
    *,
    db: AsyncSession = Depends(get_db),
    request_body: EmailRequest,
    background_tasks: BackgroundTasks
):
    user = await crud_user.get_by_email(db, email=request_body.email)
    
    # NOVO LOG: Verifica se o usuário foi encontrado e qual é o status dele
    if user:
        logger.info(f"User found for resend verification. Active: {user.is_active}, Verified: {user.is_verified}")
    else:
        logger.info(f"User not found for resend verification.")
        
    # Verifica se o usuário existe, está ativo e NÃO está verificado
    if user and user.is_active and not user.is_verified:
        try:
            # Esta função (generate_verification_token) agora deve funcionar (após a correção no crud_user.py)
            db_user, verification_token = await crud_user.generate_verification_token(db, user=user)
            
            # Envia o e-mail em segundo plano
            background_tasks.add_task(
                send_verification_email, 
                email_to=db_user.email, 
                verification_token=verification_token
            )
            logger.info(f"Background task added for email resend to: {user.email}")
            
        except Exception as e:
            # Log de erro interno no background task.
            logger.error(f"FATAL ERROR in background task during email resend for {user.email}: {e}")
            pass 
            
    return {"msg": "Se o e-mail existir e não estiver verificado, um novo link foi enviado."}

@router.post("/", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
    background_tasks: BackgroundTasks # Adicionar BackgroundTasks
) -> Any:
    """
    Cria um novo usuário (registro) e envia email de verificação.
    (Este endpoint permanece público, sem autenticação)
    """
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    # create agora retorna o usuário E o token
    db_user, verification_token = await crud_user.create(db, obj_in=user_in)

    # --- Enviar email em background ---
    background_tasks.add_task(
        send_verification_email,
        email_to=db_user.email,
        verification_token=verification_token
    )
    # --- Fim envio email ---

    # Retorna o usuário criado (sem o token)
    return db_user

@router.get("/me", response_model=UserSchema)
async def read_user_me(
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Retorna o usuário logado atualmente (token deve ser válido e usuário ativo).
    (Endpoint seguro, requer usuário ativo)
    """
    # A dependência get_current_active_user já validou o token e buscou o usuário.
    # Basta retornar o objeto do usuário.
    return current_user # Adicione esta seção inteira


@router.get("/", response_model=List[UserSchema])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    # --- ADICIONAR PROTEÇÃO DE ADMIN ---
    admin_user: UserModel = Depends(get_current_admin_user)
    # --- FIM PROTEÇÃO ---
) -> Any:
    """
    Retorna uma lista de usuários.
    (Protegido: Somente usuários com a role 'admin' podem acessar)
    """
    users = await crud_user.get_multi(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserSchema)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # --- ADICIONAR PROTEÇÃO DE ADMIN ---
    admin_user: UserModel = Depends(get_current_admin_user)
    # --- FIM PROTEÇÃO ---
) -> Any:
    """
    Busca um usuário pelo ID.
    (Protegido: Somente usuários com a role 'admin' podem acessar)
    """
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Futuramente, você poderia adicionar uma lógica aqui:
    # if admin_user.id == user.id or admin_user.is_admin: ...
    # Mas por enquanto, apenas admins podem ver outros usuários.
    return user

@router.put("/me", response_model=UserSchema)
async def update_user_me(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Atualiza os dados do próprio usuário logado.
    (Este endpoint permanece como estava, requer apenas usuário ativo)
    """
    user = await crud_user.update(db, db_obj=current_user, obj_in=user_in)
    return user