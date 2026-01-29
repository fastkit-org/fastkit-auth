from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import sys
import os
import importlib
from alembic import context
from fastkit_core.database import build_database_url, Base
from fastkit_core.config import ConfigManager

sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def import_all_models():
    MODULES = [
        'fastkit_auth.users.models',
        'fastkit_auth.tokens.models',
    ]

    for module_name in MODULES:
        try:
            print(f"  - {module_name}")
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            print(f"    (module not found, skipping)")
        except Exception as e:
            print(f"    Warning: {e}")


    if Base.metadata.tables:
        print(f"Tables: {list(Base.metadata.tables.keys())}")
    else:
        print("WARNING: No tables found! Check if models are using the correct Base.")


import_all_models()

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
    configuration_manager = ConfigManager(modules=['database'])
    url = build_database_url(configuration_manager)

    print(f"\nDatabase URL: {url}")

    configuration = {
        'sqlalchemy.url': url
    }

    ini_section = config.get_section(config.config_ini_section)
    if ini_section:
        configuration.update(ini_section)

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()