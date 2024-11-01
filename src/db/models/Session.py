import json
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Document Model for chat session
class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id= Column(String, unique=True, nullable=False)  # Foreign key if users exist
    document_path = Column(String, unique=True, nullable=False)
    date = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    context = Column(String, nullable=False)

    history = Column(String, nullable=True, default="")

    def __repr__(self):
        return json.dumps({
            "id": self.id,
            "session_id": self.session_id,
            "document_path": self.document_path,
            "date": self.date.isoformat(),  # Convert DateTime to ISO format
            "updated_at": self.updated_at.isoformat(),
            # "context": self.context,
        })
