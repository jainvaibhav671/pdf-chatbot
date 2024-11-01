from fastapi.websockets import WebSocketDisconnect
from langchain_core.documents import Document
import pytest
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from pdf_chatbot.app import app

    return TestClient(app)


@pytest.fixture
async def async_client():
    from pdf_chatbot.app import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_root_index(async_client: AsyncClient):
    response = await async_client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
@patch("pdf_chatbot.app.save_file", return_value="test.pdf")
@patch("pdf_chatbot.app.read_pdf", return_value=[Document("HelloWorld")])
@patch("pdf_chatbot.app.create_session", return_value="mock_session_id")
async def test_upload_pdf(
    _mock_generate_session_id,
    _mock_read_pdf,
    _mock_save_file,
    async_client: AsyncClient,
):
    files = {"file": ("test.pdf", open("./static/test.pdf", "rb"), "application/pdf")}
    response = await async_client.post("/upload-pdf", files=files)

    assert response.status_code == 200

    data = response.json()
    assert data["filename"].split("-")[-1] == "test.pdf"
    assert "upload_date" in data
    assert data["session_id"] == "mock_session_id"

@pytest.mark.asyncio
async def test_websocket_endpoint(client: TestClient):
    # Mock dependencies
    with patch("pdf_chatbot.app.get_session_data") as mock_get_session_data, \
         patch("pdf_chatbot.app.init_chat_model") as mock_init_chat_model, \
         patch("pdf_chatbot.app.update_session_data") as mock_update_session_data:

        # Set up mock return values
        mock_get_session_data.return_value = MagicMock(document_path="./static/test.pdf")

        mock_chain = MagicMock()
        mock_chain.invoke = MagicMock(return_value={"answer": "Mocked Answer"})
        mock_init_chat_model.return_value = mock_chain

        # Connect to WebSocket
        with client.websocket_connect("/question") as websocket:
            # Send initial data with session_id
            websocket.send_json({"session_id": "mock_session_id"})

            # Receive session loaded message
            message = websocket.receive_text()
            assert "<p class='chat-log'><b>**Session Loaded**</b></p>" in message

            # Send a question
            question = "What is AI?"
            websocket.send_text(question)

            # Receive the mocked answer
            response = websocket.receive_text()
            assert "<p class='chat-answer'>Mocked Answer</p>" in response

            # Verify `update_session_data` was called with correct parameters
            mock_update_session_data.assert_called_with(
                mock_get_session_data.return_value, question, "Mocked Answer"
            )
