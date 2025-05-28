import os
from dotenv import load_dotenv
from logging.config import fileConfig
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

load_dotenv() # Load environment variables from .env

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from server.models.base import Base # Import Base from where models will be defined
target_metadata = Base.metadata # Use the Base metadata for autogenerate

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    db_url = os.getenv("DATABASE_URL")
    if db_url is None:
        print("Warning: DATABASE_URL not found in .env for Alembic. Falling back to SQLite.")
        # Construct path to 'test.db' in the project root (TubeTrends/test.db)
        # __file__ is server/alembic/env.py
        # ../.. takes it to TubeTrends/
        project_root_for_sqlite = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        db_url = f"sqlite:///{os.path.join(project_root_for_sqlite, 'test.db')}"
        print(f"Alembic using SQLite at: {db_url}")
        # For SQLite, ensure connect_args for check_same_thread if it's used by create_engine implicitly
        # However, engine_from_config handles this if 'connect_args' is part of the config.
        # We might need to add connect_args to 'configuration' if issues arise.

    configuration["sqlalchemy.url"] = db_url

    connectable = engine_from_config(
        configuration, # Use the modified configuration
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
