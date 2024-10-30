from langchain_core.documents import Document
from typing import List
from datetime import datetime
from fastapi import Depends, FastAPI, UploadFile, File, Request
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from langchain_community.document_loaders import PyPDFLoader

from db import get_db, get_session_data
from db.models.Session import Session as SessionModel
from pdf_chatbot.models import PDFUploadModel
from pdf_chatbot.utils import generate_session_id, get_logger, log, save_file

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...),
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

        loader = PyPDFLoader(file_path)
        pages: List[Document] = []
        for page in loader.load():
            pages.append(page)

        # Add the document to the database
        session_id = generate_session_id()
        new_document = SessionModel(
            session_id=session_id,
            document_path=file_path,
            date=datetime.now(),
            context="\n\n".join(map(lambda page: page.page_content, pages)),
        )
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        # vector_store = InMemoryVectorStore.from_documents(pages, ServerSideEmbedding())
        # docs = vector_store.similarity_search("hello world", k=3)

        # for doc in docs:
        #     print(f'Page {doc.metadata["page"]}: {doc.page_content[:300]}\n')

        log(logger, file_path.split("/")[-1], str(datetime.now()))
        return PDFUploadModel(
            filename=file_path.split("/")[-1],
            upload_date=datetime.now(),
            session_id = session_id
        )
    except Exception as e:
        logger.error(e)
        return {
            "success": False,
            "message": "An error occurred while processing the PDF file.",
        }


@app.websocket("/question")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # Wait for the initial message that includes user_id and document_id
        data = await websocket.receive_json()
        session_id = data["session_id"]
        
        # Fetch the session data using user_id and document_id
        session_data = get_session_data(session_id)

        if session_data:
            await websocket.send_text(f"Session loaded for document {session_id}. You can ask questions.")
        else:
            await websocket.send_text("Session not found.")
            await websocket.close()

        # Handle subsequent questions
        while True:
            question = await websocket.receive_text()
            
            # Here, implement the logic to answer questions using the context from session_data
            # For now, we simulate with a static response based on the context.
            if question:
                # Example: You can use the context to search for relevant answers
                answer = f"Answering your question '{question}' using document {session_id} context."
                await websocket.send_text(answer)
                
    except WebSocketDisconnect:
        print("WebSocket disconnected")


def main():
    import uvicorn

    uvicorn.run("pdf_chatbot.app:app", reload=True)
