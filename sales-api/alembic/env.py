import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
from app.db.base import Base  # Importa sua Base declarativa
from app.core.config import settings # <-- IMPORTADO

# Carrega a configuração de logging do alembic.ini
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- CORREÇÃO (FASE 3) ---
# Ignora a URL do alembic.ini e usa a URL do .env
# Isso garante que ele se conecte a 'sales-db', não 'localhost'
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
# --- FIM DA CORREÇÃO ---

# Modelo de metadados para 'autogenerate'
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    # Usa a configuração do alembic.ini (agora corrigida com a DATABASE_URL)
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.main_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())