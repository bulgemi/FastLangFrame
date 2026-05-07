import pytest
from unittest.mock import MagicMock, patch
from src.utils.connectors.db.database import Database
from src.common.exceptions.custom import ConnectorError

def test_get_session_success():
    """Test get_session successfully commits and closes."""
    mock_session = MagicMock()
    mock_factory = MagicMock(return_value=mock_session)
    
    db = Database()
    with patch.object(db, "get_scoped_session", return_value=mock_factory):
        gen = db.get_session()
        session = next(gen)
        
        assert session == mock_session
        
        try:
            next(gen)
        except StopIteration:
            pass
            
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.rollback.assert_not_called()

def test_get_session_exception():
    """Test get_session rollbacks and closes on general exception."""
    mock_session = MagicMock()
    mock_factory = MagicMock(return_value=mock_session)
    
    db = Database()
    with patch.object(db, "get_scoped_session", return_value=mock_factory):
        gen = db.get_session()
        session = next(gen)
        
        with pytest.raises(ConnectorError):
            gen.throw(Exception("Random error"))
            
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        mock_session.commit.assert_not_called()

def test_get_session_connector_error():
    """Test get_session rollbacks and closes on ConnectorError."""
    mock_session = MagicMock()
    mock_factory = MagicMock(return_value=mock_session)
    
    db = Database()
    with patch.object(db, "get_scoped_session", return_value=mock_factory):
        gen = db.get_session()
        session = next(gen)
        
        with pytest.raises(ConnectorError):
            gen.throw(ConnectorError("DB error"))
            
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
