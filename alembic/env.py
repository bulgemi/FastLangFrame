from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- CUSTOM IMPORTS ---
from sqlmodel import SQLModel
from src.common.configs.settings import get_settings
from src.common.types.models import User # Ensure models are imported for metadata
# ----------------------

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = SQLModel.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

settings = get_settings()

def get_url():
    from sqlalchemy.engine.url import URL
    driver = settings.database_driver
    if driver == "postgresql":
        driver = "postgresql+psycopg"
    elif driver == "mysql":
        driver = "mysql+pymysql"
    elif driver == "sqlite":
        # SQLite doesn't need credentials/host/port
        return f"sqlite:///{settings.database_dbname}"
    
    return URL.create(
        drivername=driver,
        username=settings.database_username,
        password=settings.database_password,
        host=settings.database_host,
        port=int(settings.database_port) if settings.database_port else None,
        database=settings.database_dbname,
    ).render_as_string(hide_password=False)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
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
    # Overwrite sqlalchemy.url with dynamic URL
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Add schema support if needed
            # version_table_schema=settings.database_schema,
            # include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
