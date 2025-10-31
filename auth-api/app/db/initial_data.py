import asyncio
import logging
import os

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 1. Imports de Sessão e Configs
from app.db.session import get_session_local, dispose_engine
from app.core.config import settings

# 2. Imports para criação do utilizador
from app.crud.crud_user import crud_user
from app.models.user import User # Importar o modelo User
from app.core.security import get_password_hash # Importar o hasher

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
                # --- Criação (como vimos antes) ---
                logger.info(f"A criar superutilizador: {ADMIN_EMAIL}")
                user_obj_in = User(
                    email=ADMIN_EMAIL,
                    hashed_password=get_password_hash(ADMIN_PASSWORD),
                    full_name="Admin",
                    is_active=True,
                    is_verified=True,
                    is_superuser=True,
                    custom_claims={"roles": ["admin"]} # Opcional: define a role
                )
                db_session.add(user_obj_in)
                log_message = "criado com sucesso."
            else:
                # --- Atualização Forçada (para garantir que flags estão True) ---
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
