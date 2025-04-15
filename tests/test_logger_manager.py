from unittest.mock import patch
from loguru import logger as loguru_logger

from fast_api_xtrem.logger.logger_manager import LoggerManager


def test_singleton_pattern():
    """Vérifie que le singleton fonctionne correctement."""
    LoggerManager._instance = None  # Réinitialiser le singleton
    manager1 = LoggerManager()
    manager2 = LoggerManager()
    assert manager1 is manager2, "Les instances doivent être identiques"


def test_logs_directory_creation(monkeypatch, tmp_path):
    """Teste la création du répertoire de logs."""
    # Get the parent directory of tmp_path to match the actual behavior
    parent_dir = tmp_path.parent

    # Mock du __file__ pour contrôler l'emplacement des logs
    fake_file = tmp_path / "fake_module.py"
    monkeypatch.setattr("fast_api_xtrem.logger.logger_manager.__file__",
                        str(fake_file))

    LoggerManager._instance = None
    manager = LoggerManager()

    assert manager.logs_dir.exists(), "Le répertoire de logs doit être créé"
    # Check against parent_dir instead of tmp_path
    assert manager.logs_dir == parent_dir / "logs", "Chemin des logs incorrect"


def test_info_method_calls_loguru(mocker):
    """Vérifie que LoggerManager.info() appelle loguru.info()."""
    mock_info = mocker.patch.object(loguru_logger, 'info')
    LoggerManager._instance = None
    manager = LoggerManager()

    test_msg = "Message info de test"
    manager.info(test_msg)

    mock_info.assert_called_once_with(test_msg)


def test_error_method_calls_loguru(mocker):
    """Vérifie que LoggerManager.error() appelle loguru.error()."""
    mock_error = mocker.patch.object(loguru_logger, 'error')
    LoggerManager._instance = None
    manager = LoggerManager()

    test_msg = "Message d'erreur de test"
    manager.error(test_msg)

    mock_error.assert_called_once_with(test_msg)


def test_repr_method():
    """Teste la représentation textuelle de l'instance."""
    LoggerManager._instance = None
    manager = LoggerManager()

    expected = f"<LoggerManager logs_dir={manager.logs_dir}>"
    assert repr(manager) == expected


def test_catch_decorator_propagates_to_loguru():
    """Vérifie que le décorateur catch utilise bien loguru."""
    LoggerManager._instance = None
    manager = LoggerManager()

    with patch.object(loguru_logger, 'catch') as mock_catch:
        decorator = manager.catch(ValueError)
        mock_catch.assert_called_once_with(ValueError)
        assert decorator == mock_catch.return_value


def test_log_file_creation_and_content(monkeypatch, tmp_path):
    """Test d'intégration vérifiant l'écriture dans le fichier de log."""
    # Create a fake module file for testing
    fake_file = tmp_path / "fake_module.py"
    monkeypatch.setattr("fast_api_xtrem.logger.logger_manager.__file__", str(fake_file))

    # Reset LoggerManager instance and initialize it
    LoggerManager._instance = None
    manager = LoggerManager()

    # Define a test message
    test_msg = "Message de test intégration"
    manager.info(test_msg)

    # Check if the log file exists
    log_file = manager.logs_dir / "app.log"
    assert log_file.exists(), "Le fichier de log doit exister"

    # Read the log file content with proper encoding
    log_content = log_file.read_text(encoding="utf-8")

    # Assert that the test message is part of the log content
    assert test_msg in log_content, f"Le message '{test_msg}' doit être dans le fichier de log"
