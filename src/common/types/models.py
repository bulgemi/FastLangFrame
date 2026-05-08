import os
import importlib
import logging
from typing import Optional
from sqlmodel import SQLModel, Field

logger = logging.getLogger(__name__)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    full_name: Optional[str] = None
    is_active: bool = Field(default=True)

# Dynamic Project Model Discovery
# This allows project-specific models (like ChatHistory) to be registered 
# in SQLModel.metadata without being hardcoded in the framework core.
project_name = os.getenv("PROJECT_NAME")
if project_name:
    try:
        # Ensure project models are loaded so they are registered in metadata
        importlib.import_module(f"{project_name}.common.models")
    except ImportError as e:
        # Only log if it's not a "module not found" for the project itself
        # as some projects might not have a models.py yet.
        if f"No module named '{project_name}'" not in str(e):
            logger.debug(f"Could not load models for project {project_name}: {e}")
    except Exception as e:
        logger.error(f"Error during dynamic model discovery for {project_name}: {e}")
