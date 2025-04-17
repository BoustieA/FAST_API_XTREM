"""
Tests unitaires pour le modèle User de l'application FastAPI Xtrem.

Ce module vérifie la création d'un utilisateur, le nom de la table associée
et la structure des champs définis dans le modèle SQLAlchemy.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fast_api_xtrem.db.base import Base
from fast_api_xtrem.db.models.user import User


@pytest.fixture(scope="function")
def db_session():
    """
    Fixture Pytest pour fournir une session de base de données
    SQLite en mémoire pour les tests.

    Yields:
        SQLAlchemy Session : session de base de données pour test.
    """
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    testing_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()


def test_create_user(db_session):
    """
    Vérifie la création d'un utilisateur dans la base de données.
    """
    user = User(nom="Alice", email="alice@example.com", pswd="secret")
    db_session.add(user)
    db_session.commit()

    result = db_session.query(User).filter_by(email="alice@example.com").first()
    assert result is not None
    assert result.nom == "Alice"
    assert result.email == "alice@example.com"
    assert result.pswd == "secret"


def test_user_table_name():
    """
    Vérifie que le nom de la table associée au modèle User est correct.
    """
    assert User.__tablename__ == "users"


def test_user_fields():
    """
    Vérifie que tous les champs du modèle User existent
    et que les champs requis ne sont pas nullables.
    """
    columns = User.__table__.columns
    assert "id" in columns
    assert "nom" in columns
    assert "email" in columns
    assert "pswd" in columns
    assert columns["nom"].nullable is False
    assert columns["email"].nullable is False
