from logging.config import fileConfig
import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы можно было импортировать src и settings
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from settings import settings

# this is the Alembic Config object
config = context.config

# Используем DATABASE_URL из настроек, но заменяем asyncpg на psycopg2 для синхронного подключения
sync_database_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
config.set_main_option('sqlalchemy.url', sync_database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Импортируем Base из src.database
from src.database import Base  # noqa

# --- НАЧАЛО ИМПОРТА МОДЕЛЕЙ ---
# ВАЖНО: Импортируем модели ПОСЛЕ Base, чтобы Base "узнал" о них
from src.models.users import User  # noqa
# from src.models.posts import Post  # noqa
# from src.models.comments import Comment  # noqa
# Импортируй все свои модели здесь, чтобы Alembic их "увидел"
# --- КОНЕЦ ИМПОРТА МОДЕЛЕЙ ---

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()