import pytest
from httpx import AsyncClient, ASGITransport
from fastapi import status


@pytest.fixture
async def async_client():
    from pdf_chatbot.app import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_rate_limit(async_client: AsyncClient):
    # Sending 5 requests within a minute should be allowed
    for _ in range(5):
        response = await async_client.post(
            "/upload-pdf",
            files={"file": ("test.pdf", b"dummy content", "application/pdf")},
        )
        assert response.status_code == status.HTTP_200_OK or status.HTTP_201_CREATED

    # The 6th request should exceed the rate limit
    response = await async_client.post("/upload-pdf", files={
        "file": ("test.pdf", b"dummy content", "application/pdf")
    })
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "rate limit exceeded" in response.text.lower()

    # Wait for a minute before trying again if you want to test for reset (optional)
