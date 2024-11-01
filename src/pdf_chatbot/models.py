from pydantic import BaseModel
from datetime import datetime

# PDFUploadModel for returning response
class PDFUploadModel(BaseModel):
    filename: str
    upload_date: datetime
    session_id: str
