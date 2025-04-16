import pytest
from unittest.mock import patch, MagicMock
from fast_api_xtrem.db.db_manager import DBManager


@pytest.fixture
def fake_logger():
    return MagicMock()


@patch("fast_api_xtrem.db.db_manager.DBManager._get_package_root")
def test_check_db_file_creates_dir_if_not_exists(mock_root, fake_logger, tmp_path):
    # Arrange
    fake_root = tmp_path
    mock_root.return_value = fake_root
    db_path = fake_root / "database"
    assert not db_path.exists()

    # Act
    DBManager("sqlite:///placeholder.db", logger=fake_logger)

    # Assert
    assert db_path.exists()
    fake_logger.info.assert_called()


@patch("fast_api_xtrem.db.db_manager.create_engine")
@patch("fast_api_xtrem.db.db_manager.DBManager._create_tables")
def test_connect_success(mock_create_engine, fake_logger):
    # Arrange
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine
    mock_engine.connect.return_value.__enter__.return_value.begin.return_value.__enter__.return_value = None

    db = DBManager("sqlite:///test.db", logger=fake_logger)

    # Act
    result = db.connect()

    # Assert
    assert result is True
    fake_logger.success.assert_called()


def test_disconnect_logs(fake_logger):
    db = DBManager("sqlite:///test.db", logger=fake_logger)
    db.engine = MagicMock()

    db.disconnect()

    fake_logger.info.assert_called_with("🔌 Déconnexion de la base de données effectuée")
    db.engine.dispose.assert_called()


def test_disconnect_without_engine_logs_warning(fake_logger):
    db = DBManager("sqlite:///test.db", logger=fake_logger)
    db.disconnect()

    fake_logger.warning.assert_called_with("Tentative de déconnexion sans connexion active")


def test_get_db_without_connect_raises(fake_logger):
    db = DBManager("sqlite:///test.db", logger=fake_logger)

    with pytest.raises(Exception, match="Base de données non connectée"):
        list(db.get_db())

    fake_logger.error.assert_called()
