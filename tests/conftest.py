import pytest
from fastapi.testclient import TestClient

from src.multi_agent_chat.app import app


@pytest.fixture
def client():
    return TestClient(app)
