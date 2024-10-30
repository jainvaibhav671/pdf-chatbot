from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from db.models.Session import Base as SessionBase, Session

# SQLAlchemy setup
DATABASE_URL = "sqlite:///./main.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_session_data(session_id: str):
    """
    Get session data from the database based on the session_id.
    
    Parameters:
    - session_id: str - The ID of the session to retrieve.

    Returns:
    - Session: The session object if found, otherwise None.
    """

    db = SessionLocal()

    # Query the session data from the database using session_id
    # session_data = db.query(SessionBase).filter_by(session_id=session_id).first()
    stmt = select(Session).where(Session.session_id == session_id)
    response = db.execute(stmt)

    # Return the session data if found, otherwise return None
    return response.all()[0][0]


# Create the database table(s)
SessionBase.metadata.create_all(bind=engine)
