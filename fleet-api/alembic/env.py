import os
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy import engine_from_config
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from alembic import context

# --- (1) Importar as configurações da sua aplicação ---
# Isso garante que estamos usando a DATABASE_URL do .env
from app.core.config import settings

# --- (2) Importar sua Base declarativa ---
# Isso é necessário para que o 'autogenerate' encontre seus modelos
# (Ajuste o caminho se sua Base estiver em outro lugar)
from app.db.base_class import Base 

# --- (3) Configuração Padrão do Alembic ---
config = context.config

# Carrega a configuração de logging do alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- (4) Configurar a URL do Banco de Dados ---
# Ignora a URL do alembic.ini e usa a URL do .env
# Isso é CRUCIAL para o Docker funcionar
config.set_main_option("sqlalchemy.url", settings.DATABASE_URI)

# --- (5) Configurar os Metadados ---
target_metadata = Base.metadata

# --- (6) Funções de Migração ---

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
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
    """Função auxiliar para a migração online."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    """
    # Cria a engine assíncrona
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section('alembic', {}), # <-- CORREÇÃO
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
        )
    )

    # Conecta e executa as migrações
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# --- (7) Lógica de Execução ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Executa no modo assíncrono
    asyncio.run(run_migrations_online())