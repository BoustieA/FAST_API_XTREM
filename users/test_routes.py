import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


@pytest.fixture
def test_login_success():
    data = {"nom": "Alice", "pswd": "secure123"}

    response = client.post("/login", json=data)

    assert response.status_code == 200
    assert "Succès" in response.json()["message"]


def test_login_incorrect():
    data = {"nom": "Alice", "pswd": "wrongpassword"}

    response = client.post("/login", json=data)

    assert response.status_code == 401
    assert "Erreur" in response.json()["message"]


def test_login_not_found():
    data = {"nom": "Jack", "pswd": "secure123"}

    response = client.post("/login", json=data)

    assert response.status_code == 404
    assert "Erreur" in response.json()["message"]


def test_login_no_data():
    data = {}

    response = client.post("/login", json=data)

    assert response.status_code == 400
    assert "Erreur" in response.json()["message"]
