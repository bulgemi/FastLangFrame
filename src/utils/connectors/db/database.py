"""Database module."""

import os
import asyncio
import inspect
import logging
import traceback
import urllib.parse
from contextlib import asynccontextmanager, contextmanager
from types import ModuleType
from typing import Any, Callable, ContextManager, Generator

from autologging import logged
import sqlalchemy
from alembic import command as alembic_cmd
from alembic.config import Config as AlembicConfig
from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    async_engine_from_config,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import scoped_session, sessionmaker
# from sqlalchemy_filters import apply_filters, apply_pagination, apply_sort
from sqlmodel import Session, SQLModel, engine_from_config
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.main import FieldInfo as sqlmodel_FieldInfo

from src.common.configs.settings import get_settings
from src.common.exceptions.custom import ConnectorError

settings = get_settings()
APP_SCHEMA = settings.database_schema
# APP_SCHEMA = "public"
SQLModel.metadata = sqlalchemy.MetaData(schema=APP_SCHEMA)

__all__ = [
    "Database",
    "db_config",
]


sqlmodel_Session = Session
sqlmodel_AsyncSession = AsyncSession


def flatten_json(y):
    out = {}

    def flatten(x, name=""):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + "_")
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + "_")
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out


@logged
class Database:
    def __init__(
        self,
        settings: get_settings = None,
    ) -> None:
        """ """
        self.settings = settings or get_settings()

        # Engines and Session Factories Caches
        self._engines = {}
        self._async_engines = {}
        self._session_factories = {}
        self._async_session_factories = {}
        self._scoped_sessions = {}
        self._async_scoped_sessions = {}

        # Defer initialization to first use (Lazy)
        self.db_url = None  # Will be set on first engine creation

    @property
    def engine(self) -> sqlalchemy.engine.Engine:
        return self.get_engine()

    @property
    def async_engine(self):
        return self.get_async_engine()

    @property
    def session(self) -> scoped_session:
        return self.get_scoped_session()

    @property
    def async_session(self) -> async_scoped_session:
        return self.get_async_scoped_session()

    def _get_db_extra_config(self) -> dict[str, Any]:
        driver = self.settings.database_driver
        if driver == "sqlite":
            db_url = f"sqlite:///{self.settings.database_dbname}"
            db_extra_config_dict = {
                "database.url": db_url,
            }
            return db_extra_config_dict

        if driver == "mysql":
            connector = "mysql+pymysql"
        elif driver == "postgresql":
            connector = "postgresql+psycopg2"
        elif driver == "postgresql-async":
            connector = "postgresql+asyncpg"
        else:
            connector = driver

        encoded_username = urllib.parse.quote_plus(self.settings.database_username)
        encoded_password = urllib.parse.quote_plus(self.settings.database_password)
        db_url = f"{connector}://{encoded_username}:{encoded_password}@{self.settings.database_host}:{self.settings.database_port}/{self.settings.database_dbname}"

        db_extra_config_dict = {
            "database.url": db_url,
            "database.connect_args": {"options": f"-csearch_path={self.settings.database_schema}"},
            "database.execution_options": {"schema_translate_map": {APP_SCHEMA: self.settings.database_schema}},
        }
        return db_extra_config_dict

    def get_engine(self, project_name: str = None) -> sqlalchemy.engine.Engine:
        if project_name not in self._engines:
            config_dict = self._get_db_extra_config()
            self._engines[project_name] = engine_from_config(
                config_dict,
                prefix="database.",
            )
            if project_name is None:
                self.db_url = str(self._engines[project_name].url)
        return self._engines[project_name]

    def get_async_engine(self, project_name: str = None):
        if project_name not in self._async_engines:
            config_dict = self._get_db_extra_config()
            self._async_engines[project_name] = async_engine_from_config(
                config_dict,
                prefix="database.",
                future=True,
            )
        return self._async_engines[project_name]

    def get_scoped_session(self, project_name: str = None) -> scoped_session:
        if project_name not in self._scoped_sessions:
            engine = self.get_engine(project_name)
            factory = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=sqlmodel_Session,
            )
            self._session_factories[project_name] = factory
            self._scoped_sessions[project_name] = scoped_session(
                session_factory=factory
            )
        return self._scoped_sessions[project_name]

    def get_async_scoped_session(
        self, project_name: str = None
    ) -> async_scoped_session:
        if project_name not in self._async_scoped_sessions:
            async_engine = self.get_async_engine(project_name)
            factory = async_sessionmaker(
                bind=async_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
                class_=sqlmodel_AsyncSession,
            )
            self._async_session_factories[project_name] = factory
            self._async_scoped_sessions[project_name] = async_scoped_session(
                session_factory=factory,
                scopefunc=asyncio.current_task,
            )
        return self._async_scoped_sessions[project_name]

    def get_session(
        self, project_name: str = None
    ) -> Generator[sqlmodel_Session, None, None]:
        session_factory = self.get_scoped_session(project_name)
        session: sqlmodel_Session = session_factory()
        try:
            yield session
        except ConnectorError as known_e:
            session.rollback()
            raise known_e
        except Exception as e:
            session.rollback()
            raise ConnectorError(f"Database error: {e}") from e
        else:
            session.commit()
        finally:
            session.close()

    @staticmethod
    @contextmanager
    def session_context_manager(session: sqlmodel_Session):
        try:
            yield session
        except ConnectorError as known_e:
            try:
                session.rollback()
            except Exception:
                pass  # 이미 롤백된 상태이거나 세션이 닫힌 경우 무시
            raise known_e
        except Exception as e:
            try:
                session.rollback()
            except Exception:
                pass  # 이미 롤백된 상태이거나 세션이 닫힌 경우 무시
            raise ConnectorError(f"Database error: {e}") from e
        else:
            try:
                session.commit()
            except Exception:
                pass  # 이미 커밋된 상태이거나 세션이 닫힌 경우 무시
        finally:
            try:
                session.close()
            except Exception:
                pass  # 이미 닫힌 상태인 경우 무시

    async def get_async_session(self, project_name: str = None):
        scoped_session = self.get_async_scoped_session(project_name)
        session = scoped_session()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        else:
            await session.commit()
        finally:
            await scoped_session.remove()

    @property
    def metadata(self):
        return SQLModel.metadata

    def create_database(self, model_modules=[]) -> None:
        """Arguments:
        ---------
            model_modules: List[module]
                This argument is not used internally,
                but It enforces importing ORM models of SQLModel before calling `create_all`.

        """
        try:
            self.metadata.create_all(self.engine)
        except Exception as e:
            raise e

    def apply_migration(
        self, alembic_config_filepath: str = "alembic.ini", project_name: str = None
    ):
        try:
            alembic_cfg = AlembicConfig(alembic_config_filepath)
            
            # Use self.settings directly
            from sqlalchemy.engine.url import URL

            driver = self.settings.database_driver
            if driver == "postgresql":
                driver = "postgresql+psycopg"
            elif driver == "mysql":
                driver = "mysql+pymysql"

            db_url = URL.create(
                drivername=driver,
                username=self.settings.database_username,
                password=self.settings.database_password,
                host=self.settings.database_host,
                port=int(self.settings.database_port) if self.settings.database_port else None,
                database=self.settings.database_dbname,
            ).render_as_string(hide_password=False)

            alembic_cfg.set_main_option("sqlalchemy.url", db_url)

            # Pass schema to env.py via attributes
            alembic_cfg.attributes["target_schema"] = self.settings.database_schema
            alembic_cfg.set_main_option("target_schema", self.settings.database_schema)
            if project_name:
                alembic_cfg.set_main_option("named_db_name", project_name)

            alembic_cmd.upgrade(alembic_cfg, "head")
        except Exception as e:
            self.__log.error(
                "Alembic migration failed for project %s:\n%s",
                project_name or "default",
                traceback.format_exc(),
            )
            raise

    def insert_seeds(self) -> bool:
        """Arguments:
        ---------
            domain_modules:
            project_name: str (default: None)

        Example:
        -------
            Example 1:
            >>> from agentapp.core.database import db
            >>> db.insert_seeds()

            Example 2:
            >>> from agentapp.core.database import db
            >>> from agentapp.domains import example, school
            >>> db.insert_seeds([example, school])

        """
        return True

    def prepare(
        self,
        alembic_config_filepath: str = "alembic.ini",
        domain_modules: list[ModuleType] = None,
    ):
        """Arguments:
        ---------
            alembic_config_filepath: str
                Filepath
            domain_modules: list[ModuleType]
                Modules of domains

        Example:
        -------
            Example 1:
            >>> from agentapp.core.database import db
            >>> db.insert_seeds()

            Example 2:
            >>> from agentapp.core.database import db
            >>> from agentapp.domains import example, school
            >>> db.insert_seeds([example, school])

        """
        # 1. Prepare Default Database
        self.__log.info("Preparing default database...")
        self.apply_migration(alembic_config_filepath=alembic_config_filepath)
        self.insert_seeds(domain_modules)

        # 2. Prepare Project-specific Databases
        if self.project_configs:
            self.__log.info(
                f"Preparing {len(self.project_configs)} project-specific databases..."
            )
            for project_name in self.project_configs:
                try:
                    self.__log.info(f"Preparing database for project: {project_name}")
                    self.apply_migration(
                        alembic_config_filepath=alembic_config_filepath,
                        project_name=project_name,
                    )
                    self.__log.info(f"Migration completed for project: {project_name}")
                    self.insert_seeds(domain_modules, project_name=project_name)
                    self.__log.info(f"Seeds completed for project: {project_name}")
                except Exception as e:
                    self.__log.error(
                        f"Failed to prepare database for project {project_name}. "
                        f"Skipping to ensure application startup. Error: {e}",
                        exc_info=True,
                    )
        else:
            self.__log.info("No project-specific databases to prepare.")

    def ping(self) -> bool:
        session: sqlmodel_Session = self.session()
        try:
            session.exec(text("SELECT 1;"))
            session.commit()
            return True
        except Exception as e:
            return False
        finally:
            session.close()


# pagination.py

# Initialize Database with settings
db = Database(settings=settings)


def get_session() -> Generator[sqlmodel_Session, None, None]:
    """FastAPI dependency for database session"""
    yield from db.get_session()


async def get_async_session() -> Generator[AsyncSession, None, None]:
    """FastAPI dependency for async database session"""
    async for session in db.get_async_session():
        yield session


__all__ = [
    "PageMetadata",
    "Page",
    "PageableParams",
    "pageable_params",
    "apply_pageable_params",
    "apply_sort_params",
]


class PageMetadata(BaseModel):
    number: int
    size: int
    totalElements: int
    totalPages: int


class Page(BaseModel):
    content: Any
    pageMetadata: PageMetadata

    def __init__(
        self,
        content: Any = None,
        page_number: int = None,
        page_size: int = None,
        total_results: int = None,
        num_pages: int = None,
    ):
        pageMetadata = PageMetadata(
            number=page_number,
            size=page_size,
            totalElements=total_results,
            totalPages=num_pages,
        )

        super().__init__(
            content=content,
            pageMetadata=pageMetadata,
        )

        # self.content = content
        # self.pageMetadata = pageMetadata


def get_pk_list(table_or_record):
    return [
        name
        for name, property in table_or_record.model_fields.items()
        if isinstance(property, sqlmodel_FieldInfo) and property.primary_key
    ]


def get_pk_values(record):
    pk_list = get_pk_list(record)
    return [getattr(record, pk) for pk in pk_list]


class PageableParams(BaseModel):
    page: int = 1
    size: int
    # limit: int
    # offset: int
    sort: list[str]
    # page: int = 1
    # size: int = 10
    # limit: int = 50
    # offset: int = 100
    # sort: List[str] = Query(
    #     ["model_version:desc"],
    # )


async def pageable_params(
    page: int = 1,
    size: int = 10,
    # limit: int = 50,
    # offset: int = 100,
    sort: list[str] = Query(
        [],
    ),
    # ) -> Dict[str, Any]:
) -> PageableParams:
    # return locals()
    return PageableParams(**locals())


def apply_pageable_params(
    query: sqlalchemy.orm.query.Query,
    pageable_params: PageableParams,
) -> Page:
    if pageable_params.sort:
        query = apply_sort_params(query, pageable_params.sort)

    query, pagination = apply_pagination(
        query,
        page_number=pageable_params.page,
        page_size=pageable_params.size,
    )
    page_number, page_size, num_pages, total_results = pagination

    return Page(
        content=query.all(),
        page_number=page_number,
        page_size=page_size,
        total_results=total_results,
        num_pages=num_pages,
    )


def _gen_sort_spec(sort_param):
    return {
        "model": "ModelDeployable",
        "field": sort_param[0],
        "direction": sort_param[1],
    }


def apply_sort_params(
    query: sqlalchemy.orm.query.Query,
    sort: list[str],
) -> sqlalchemy.orm.query.Query:
    sort_params = [s.split(":") for s in sort]
    sort_spec = [_gen_sort_spec(s) for s in sort_params]
    # sort_spec = [
    #     {"model": "ModelDeployable", "field": "name", "direction": "asc"},
    #     {"model": "ModelDeployable", "field": "id", "direction": "desc"},
    # ]
    return apply_sort(query, sort_spec)


__all__ = [
    "apply_nullable_filters",
]


def apply_nullable_filters(query, filter_spec: list):
    return apply_filters(
        query,
        filter(lambda x: x.get("value", None) is not None, filter_spec),
    )
