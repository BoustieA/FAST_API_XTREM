import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fast_api_xtrem.db.base import Base
from fast_api_xtrem.db.models.user import User


# Fixture for setting up and tearing down the database
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_user(session):
    utilisateur = User(
        nom="Alice", email="alice@example.com", pswd="secure123"
    )
    session.add(utilisateur)
    session.commit()

    result = session.query(User).filter_by(email="alice@example.com").first()

    assert result is not None
    assert result.nom == "Alice"
    assert result.email == "alice@example.com"
    assert result.pswd == "secure123"
