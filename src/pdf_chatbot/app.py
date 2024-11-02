from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Request
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from langchain_core.messages import AIMessage, HumanMessage

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from db import create_session, get_session_data, update_session_data
from pdf_chatbot.models import PDFUploadModel
from pdf_chatbot.utils import get_logger, init_chat_model, log, read_pdf, save_file

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create a Limiter instance
limiter = Limiter(key_func=get_remote_address)
# Add the Limiter middleware and exception handler to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.post("/upload-pdf")
@limiter.limit("5/minute")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
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

        pages = read_pdf(file_path)
        pages = list(map(lambda page: page.page_content, pages))

        # Add the document to the database
        session_id = create_session(file_path, pages)

        log(logger, file_path.split("/")[-1], str(datetime.now()))
        return PDFUploadModel(
            filename=file_path.split("/")[-1],
            upload_date=datetime.now(),
            session_id=session_id,
        )
    except Exception as e:
        print(e)
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
        rag_chain = init_chat_model(session_data.document_path)
        chat_history = []

        if session_data:
            await websocket.send_text(
                "<p class='chat-log'><b>**Session Loaded**</b></p>"
            )
        else:
            await websocket.send_text("<p class='chat-log'>Session not found.</p>")
            await websocket.close()

        # Handle subsequent questions
        while True:
            question = await websocket.receive_text()
            if len(question) > 0:
                print(question)
                chat_history.append(HumanMessage(content=question))
                results = rag_chain.invoke({"history": chat_history, "input": question})
                print(results)
                answer = f"<p class='chat-answer'>{results["answer"]}</p>"
                chat_history.append(AIMessage(content=answer))

                session_data = update_session_data(
                    session_data, question, results["answer"]
                )
                await websocket.send_text(answer)

    except WebSocketDisconnect:
        print("WebSocket disconnected")


def main():
    import uvicorn

    uvicorn.run("pdf_chatbot.app:app", reload=True)
