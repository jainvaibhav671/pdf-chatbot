from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# PDFUploadModel for returning response
class PDFUploadModel(BaseModel):
    filename: str
    upload_date: datetime
    content: List[str]  # List of page content (text extracted from the PDF)

    class Config:
        from_attributes = True

# Model for input fields
class UploadPDFInputModel(BaseModel):
    user: Optional[str] = None  # Optional field to specify who uploaded the PDF
    description: Optional[str] = None  # Optional description of the uploaded document

    class Config:
        json_scheme_extra = {
            "example": {
                "user": "John Doe",
                "description": "This is a sample legal document for analysis."
            }
        }
