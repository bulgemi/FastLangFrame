import os
import pytest
from sqlmodel import Session, select, create_engine, SQLModel
from src.utils.connectors.db.database import Database
from src.common.types.models import User
from src.common.configs.settings import FastLangFrameSettings

@pytest.fixture(name="session")
def session_fixture():
    # Use an in-memory SQLite database for testing CRUD logic
    # SQLite doesn't support schema prefixes like 'public.table'
    SQLModel.metadata.schema = None
    for table in SQLModel.metadata.tables.values():
        table.schema = None
        
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_user_crud_operations(session: Session):
    # ... (rest of test_user_crud_operations)
    new_user = User(username="testuser", email="test@example.com", full_name="Test User")
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    assert new_user.id is not None
    assert new_user.username == "testuser"
    
    # 2. Read
    statement = select(User).where(User.username == "testuser")
    user = session.exec(statement).first()
    assert user is not None
    assert user.id == new_user.id
    
    # 3. Update
    user.full_name = "Updated User"
    session.add(user)
    session.commit()
    session.refresh(user)
    
    assert user.full_name == "Updated User"
    
    # 4. Delete
    session.delete(user)
    session.commit()
    
    statement = select(User).where(User.username == "testuser")
    deleted_user = session.exec(statement).first()
    assert deleted_user is None

@pytest.mark.asyncio
async def test_database_get_session_integration():
    """Test the actual Database.get_session integration with sqlite."""
    # Ensure schema is cleared for sqlite
    SQLModel.metadata.schema = None
    for table in SQLModel.metadata.tables.values():
        table.schema = None
        
    settings = FastLangFrameSettings(
        database_driver="sqlite",
        database_dbname=":memory:"
    )
    db = Database(settings=settings)
    
    # We need to create tables on the lazy-loaded engine
    # For SQLite memory, we should use the same engine for creation and access
    # Since get_session uses async_engine, let's use that
    async with db.async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    # Use the dependency-style generator
    async for session in db.get_session():
        user = User(username="integrated", email="integrated@example.com")
        session.add(user)
        # The generator (db.get_async_session) handles commit/rollback/close

    # Verify it was committed using a new session
    async for session in db.get_session():
        statement = select(User).where(User.username == "integrated")
        result = await session.execute(statement)
        db_user = result.scalar_one_or_none()
        assert db_user is not None
        assert db_user.email == "integrated@example.com"
