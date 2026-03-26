import pytest
import pytest_asyncio
import os
from sqlalchemy import Column, Integer, String, select, delete, update
from sqlalchemy.orm import declarative_base
from src.utils.connectors.db.db_client import DBClient
from src.common.configs.settings import FastLangFrameSettings

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "test_users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50))
    email = Column(String(50))

@pytest.fixture(scope="module")
def db_settings():
    db_path = "./test_crud.db"
    # Ensure a clean start
    if os.path.exists(db_path):
        os.remove(db_path)
    return FastLangFrameSettings(database_url=f"sqlite+aiosqlite:///{db_path}")

@pytest_asyncio.fixture(scope="module")
async def db_client_instance(db_settings):
    client = DBClient(settings=db_settings)
    # Create tables
    async with client.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield client
    # Cleanup after tests
    if os.path.exists("./test_crud.db"):
        try:
            os.remove("./test_crud.db")
        except PermissionError:
            pass

@pytest.mark.asyncio
async def test_db_crud_lifecycle(db_client_instance):
    client = db_client_instance
    # 1. Create
    async for session in client.get_session():
        new_user = UserModel(name="Antigravity", email="anti@gravity.ai")
        session.add(new_user)
        await session.commit()
    
    # 2. Read
    async for session in client.get_session():
        result = await session.execute(select(UserModel).where(UserModel.name == "Antigravity"))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.email == "anti@gravity.ai"
        user_id = user.id

    # 3. Update
    async for session in client.get_session():
        await session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(email="updated@gravity.ai")
        )
        await session.commit()
        
        result = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        assert user.email == "updated@gravity.ai"

    # 4. Delete
    async for session in client.get_session():
        await session.execute(delete(UserModel).where(UserModel.id == user_id))
        await session.commit()
        
        result = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        assert user is None
