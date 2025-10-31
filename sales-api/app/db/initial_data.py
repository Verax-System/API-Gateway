import asyncio
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from app.db.session import get_session_local, dispose_engine
from app.core.config import settings
from app.crud.crud_user import crud_user
from app.models.user import User 
from app.core.security import get_password_hash 

async def create_initial_user():
    AsyncSessionLocal = get_session_local()
    if not AsyncSessionLocal:
        logger.error("Fábrica de sessão (AsyncSessionLocal) não foi inicializada.")
        return

    logger.info("Iniciando a verificação/criação do superutilizador inicial...")
    
    try:
        async with AsyncSessionLocal() as db_session:
        
            ADMIN_EMAIL = settings.FIRST_SUPERUSER_EMAIL
            ADMIN_PASSWORD = settings.FIRST_SUPERUSER_PASSWORD
            
            if not ADMIN_EMAIL or not ADMIN_PASSWORD:
                logger.error("FIRST_SUPERUSER_EMAIL ou FIRST_SUPERUSER_PASSWORD não definidos.")
                return

            user = await crud_user.get_by_email(db=db_session, email=ADMIN_EMAIL)
            
            if not user:
                logger.info(f"A criar superutilizador: {ADMIN_EMAIL}")
                user_obj_in = User(
                    email=ADMIN_EMAIL,
                    hashed_password=get_password_hash(ADMIN_PASSWORD),
                    full_name="Admin",
                    is_active=True,     
                    is_verified=True,   
                    is_superuser=True,  # <--- AGORA ESTE CAMPO FUNCIONARÁ
                    custom_claims={"roles": ["admin"]}
                )
                
                db_session.add(user_obj_in)
                log_message = "criado com sucesso."
            else:
                # --- Força a ativação se já existe (corrige o 403 anterior) ---
                if not user.is_active or not user.is_superuser:
                    user.is_active = True
                    user.is_verified = True
                    user.is_superuser = True
                    db_session.add(user)
                    log_message = "ativado e definido como superuser."
                else:
                    log_message = "já existe e está ativo."

            await db_session.commit()
            logger.info(f"Superutilizador {ADMIN_EMAIL} {log_message}")
    
    except Exception as e:
        logger.error(f"Erro ao criar superutilizador: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        await dispose_engine()

async def main() -> None:
    await create_initial_user()

if __name__ == "__main__":
    if os.name == 'nt':
        try:
            asyncio.get_event_loop_policy()
        except asyncio.MissingEventLoopPolicyError:
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    logger.info("Executando script de dados iniciais...")
    asyncio.run(main())