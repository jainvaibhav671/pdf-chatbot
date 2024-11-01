from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import sessionmaker
from pprint import pprint as print
from datetime import datetime
import json
from typing import List

from db.models.Session import Base as SessionBase, Session
from pdf_chatbot.utils import generate_session_id

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


def create_session(document_path: str, document_content: List[str]) -> str:
    session = SessionLocal()

    session_id = generate_session_id()
    new_document = Session(
        session_id=session_id,
        document_path=document_path,
        date=datetime.now(),
        updated_at=datetime.now(),
        context=json.dumps(document_content),
        history="",
    )
    session.add(new_document)
    session.commit()
    session.refresh(new_document)

    return session_id


def get_session_data(session_id: str) -> Session:
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
    print(f"Statement: {stmt}")
    response = db.execute(stmt)

    # Return the session data if found, otherwise return None
    return response.all()[0][0]


def update_session_data(session_data: Session, question: str, answer: str) -> Session:
    session = SessionLocal()

    session_id = session_data.session_id
    print(f"Session ID: {session_id}")

    try:
        new_history: List[str] = json.loads(str(session_data.history))
        new_history.extend([question, answer])

        stmt = (
            update(Session)
            .where(Session.session_id == session_id)
            .values(
                history=json.dumps(new_history),
                updated_at=datetime.now(),
            )
            .returning(Session)
        )
        new_session_data = session.execute(stmt).first()
        if not new_session_data:
            return session_data

        print("New Session", new_session_data.tuple()[0])
        return new_session_data.tuple()[0]
    except Exception as e:
        print(e)
        return session_data


# Create the database table(s)
SessionBase.metadata.create_all(bind=engine)
