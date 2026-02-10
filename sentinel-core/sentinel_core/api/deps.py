"""
Dependency Injection

Shared dependencies for FastAPI routes.
"""

from sqlmodel import Session
from sentinel_core.memory.db import get_engine


def get_db_session() -> Session:
    """
    Get database session.
    
    Yields:
        Session: SQLModel database session
        
    Example:
        @app.get("/tasks")
        def get_tasks(session: Session = Depends(get_db_session)):
            ...
    """
    engine = get_engine()
    with Session(engine) as session:
        yield session
