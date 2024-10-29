from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models.Document import Base as DocumentBase

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


# Create the database table(s)
DocumentBase.metadata.create_all(bind=engine)
