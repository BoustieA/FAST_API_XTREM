import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fast_api_xtrem.db.models.user import User
from fast_api_xtrem.db.base import Base


@pytest.fixture(scope="function")
def session():
    # Crée une base SQLite en mémoire
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_user(session):
    user = User(nom="Alice", email="alice@example.com", pswd="secret")
    session.add(user)
    session.commit()

    result = session.query(User).filter_by(email="alice@example.com").first()
    assert result is not None
    assert result.nom == "Alice"
    assert result.email == "alice@example.com"
    assert result.pswd == "secret"


def test_user_table_name():
    assert User.__tablename__ == "users"


def test_user_fields():
    columns = User.__table__.columns
    assert "id" in columns
    assert "nom" in columns
    assert "email" in columns
    assert "pswd" in columns
    assert columns["nom"].nullable is False
    assert columns["email"].nullable is False
