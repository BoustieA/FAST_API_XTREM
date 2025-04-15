import pytest
from fastapi import Depends
from routes import login
from db.database import get_db


@pytest.fixture
def test_login_success():
    data = {"nom": "Alice", "pswd": "secure123"}

    response = login(data, Depends(get_db))

    assert response.status_code == 200


def test_login_incorrect():
    data = {"nom": "Alice", "pswd": "wrongpassword"}

    response = login(data, Depends(get_db))

    assert response.status_code == 401


def test_login_not_found():
    data = {"nom": "Jack", "pswd": "secure123"}

    response = login(data, Depends(get_db))

    assert response.status_code == 404


def test_login_no_data():
    data = {}

    response = login(data, Depends(get_db))

    assert response.status_code == 400
