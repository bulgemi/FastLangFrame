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

def test_database_get_session_integration():
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
    SQLModel.metadata.create_all(db.engine)
    
    # Use the dependency-style generator
    gen = db.get_session()
    session = next(gen)
    
    try:
        user = User(username="integrated", email="integrated@example.com")
        session.add(user)
        # The generator will commit on success
    finally:
        try:
            next(gen)
        except StopIteration:
            pass
            
    # Verify it was committed using a new session
    with Session(db.engine) as new_session:
        db_user = new_session.exec(select(User).where(User.username == "integrated")).first()
        assert db_user is not None
        assert db_user.email == "integrated@example.com"
