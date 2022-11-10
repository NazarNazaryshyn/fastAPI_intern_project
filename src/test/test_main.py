import pytest
from src.config import settings
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app=app)



def test_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Working"}