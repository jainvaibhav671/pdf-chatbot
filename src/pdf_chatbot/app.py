from langchain_core.documents import Document
from typing import List
from datetime import datetime
from fastapi import Depends, FastAPI, UploadFile, File, Form
from sqlalchemy.orm import Session

from langchain_community.document_loaders import PyPDFLoader
# from langchain_core.vectorstores import InMemoryVectorStore
# from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_google_genai.google_vector_store import ServerSideEmbedding

from db import get_db
from db.models import Document as DocumentModel
from pdf_chatbot.models import PDFUploadModel
from pdf_chatbot.utils import get_logger, log, save_file

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Server is running"}


@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
    user_id: str = Form(...),
    db: Session = Depends(get_db),
):
    logger = get_logger("[upload-pdf]")
    try:
        if not file.filename:
            return {"success": False, "message": "No file uploaded."}

        if file.content_type != "application/pdf":
            return {
                "success": False,
                "message": "Invalid file type. Please upload a PDF file.",
            }


        file_path = save_file(file)

        # Add the document to the database
        new_document = DocumentModel(user_id=user_id, file_path=file_path)
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        loader = PyPDFLoader(file_path)
        pages: List[Document] = []
        for page in loader.load():
            pages.append(page)

        # vector_store = InMemoryVectorStore.from_documents(pages, ServerSideEmbedding())
        # docs = vector_store.similarity_search("hello world", k=3)

        # for doc in docs:
        #     print(f'Page {doc.metadata["page"]}: {doc.page_content[:300]}\n')

        log(logger, file_path.split("/")[-1], str(datetime.now()))
        return PDFUploadModel(
            filename=file_path.split("/")[-1],
            upload_date=datetime.now(),
            content=list(map(lambda page: page.page_content, pages)),
        )
    except Exception as e:
        logger.error(e)
        return {
            "success": False,
            "message": "An error occurred while processing the PDF file.",
        }


def main():
    import uvicorn

    uvicorn.run("pdf_chatbot.app:app", reload=True)
