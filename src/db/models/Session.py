
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Document Model for chat session
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id= Column(String, unique=True, nullable=False)  # Foreign key if users exist
    document_path = Column(String, unique=True, nullable=False)
    date = Column(DateTime, nullable=False)
    context = Column(String, nullable=False)

    # Chat objects stored as string
    chat = Column(String, nullable=True, default="")
