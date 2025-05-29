import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(base_url="http://localhost:8000") as ac:
        response = await ac.post("/tasks", json={
            "title": "Test Task",
            "description": "Description here",
            "priority": 5
        })
        print("Response JSON:", response.json()) 
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Task"
        assert data["priority"] == 5
