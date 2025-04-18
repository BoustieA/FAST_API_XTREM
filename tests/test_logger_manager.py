"""
Test suite for the LoggerManager class.

This module contains unit tests to verify the functionality
of the LoggerManager,
including its singleton behavior, log directory creation,
integration with loguru,
and proper logging to files.
"""

from unittest.mock import patch

import pytest
from loguru import logger as loguru_logger

from fast_api_xtrem.logger.logger_manager import LoggerManager
from fast_api_xtrem.app.config import LoggerConfig

logger_config = LoggerConfig()


@pytest.fixture(autouse=True)
def reset_logger_manager_fixture():
    """Fixture to reset LoggerManager singleton before each test."""
    LoggerManager.reset_instance()
    yield


def test_singleton_pattern():
    """Vérifie que le singleton fonctionne correctement."""
    manager1 = LoggerManager(logger_config)
    manager2 = LoggerManager(logger_config)
    assert manager1 is manager2, "Les instances doivent être identiques"


def test_logs_directory_creation(monkeypatch, tmp_path):
    """
    Teste la création du répertoire de logs.
    """
    # Crée un faux fichier source dans tmp_path
    fake_file = tmp_path / "fake_module.py"
    monkeypatch.setattr(
        "fast_api_xtrem.logger.logger_manager.__file__", str(fake_file)
    )

    # L'instance va créer logs_dir à partir du parent.parent de fake_file
    expected_logs_dir = fake_file.resolve().parent.parent / "logs"
    manager = LoggerManager(logger_config)

    assert manager.logs_dir.exists(), "Le répertoire de logs doit être créé"
    assert manager.logs_dir == expected_logs_dir, \
        (f"Chemin des logs incorrect : attendu {expected_logs_dir}, "
         f"obtenu {manager.logs_dir}")


def test_info_method_calls_loguru(mocker):
    """
    Vérifie que LoggerManager.info() appelle loguru.info().
    """
    # Utilise mocker.spy pour espionner loguru_logger.info
    spy_info = mocker.spy(loguru_logger, "info")
    manager = LoggerManager(logger_config)

    test_msg = "Message info de test"
    manager.info(test_msg)

    # Vérifie que loguru_logger.info a été appelé avec le bon message
    # Ignorer les appels internes en filtrant sur le dernier appel
    assert spy_info.call_args_list[-1] == mocker.call(test_msg)


def test_error_method_calls_loguru(mocker):
    """Vérifie que LoggerManager.error() appelle loguru.error()."""
    mock_error = mocker.patch.object(loguru_logger, "error")
    manager = LoggerManager(logger_config)

    test_msg = "Message d'erreur de test"
    manager.error(test_msg)

    mock_error.assert_called_once_with(test_msg)


def test_success_method_calls_loguru(mocker):
    """Vérifie que LoggerManager.success() appelle loguru.success()."""
    mock_success = mocker.patch.object(loguru_logger, "success")
    manager = LoggerManager(logger_config)

    test_msg = "Message de succès de test"
    manager.success(test_msg)

    mock_success.assert_called_once_with(test_msg)


def test_debug_method_calls_loguru(mocker):
    """Vérifie que LoggerManager.debug() appelle loguru.debug()."""
    mock_debug = mocker.patch.object(loguru_logger, "debug")
    manager = LoggerManager(logger_config)

    test_msg = "Message de débogage de test"
    manager.debug(test_msg)

    mock_debug.assert_called_once_with(test_msg)


def test_warning_method_calls_loguru(mocker):
    """Vérifie que LoggerManager.warning() appelle loguru.warning()."""
    mock_warning = mocker.patch.object(loguru_logger, "warning")
    manager = LoggerManager(logger_config)

    test_msg = "Message d'avertissement de test"
    manager.warning(test_msg)

    mock_warning.assert_called_once_with(test_msg)


def test_repr_method():
    """Teste la représentation textuelle de l'instance."""
    manager = LoggerManager(logger_config)

    expected = f"<LoggerManager logs_dir={manager.logs_dir}>"
    assert repr(manager) == expected


def test_catch_decorator_propagates_to_loguru():
    """Vérifie que le décorateur catch utilise bien loguru."""
    manager = LoggerManager(logger_config)

    with patch.object(loguru_logger, "catch") as mock_catch:
        decorator = manager.catch(ValueError)
        mock_catch.assert_called_once_with(ValueError)
        assert decorator == mock_catch.return_value


def test_log_file_creation_and_content(monkeypatch, tmp_path):
    """
    Test d'intégration vérifiant l'écriture dans le fichier de log.

    Vérifie que les messages sont correctement écrits dans le fichier de log.
    """
    # Create a fake module file for testing
    fake_file = tmp_path / "fake_module.py"
    monkeypatch.setattr(
        "fast_api_xtrem.logger.logger_manager.__file__", str(fake_file)
    )

    manager = LoggerManager(logger_config)

    # Define a test message
    test_msg = "Message de test intégration"
    manager.info(test_msg)

    # Check if the log file exists
    log_file = manager.logs_dir / "fast_api.log"
    assert log_file.exists(), "Le fichier de log doit exister"

    # Initialize log_content to an empty string as a fallback
    log_content = ""
    try:
        log_content = log_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        pytest.fail("Log file was not found.")
    except PermissionError:
        pytest.fail("Insufficient permissions to read the log file.")
    except IOError as e:
        pytest.fail(f"An I/O error occurred while reading the log file: {e}")
    except UnicodeDecodeError as e:
        pytest.fail(f"Failed to read log file with UTF-8 encoding: {e}")

    # Assert that the test message is part of the log content
    assert (
        test_msg in log_content
    ), f"Le message '{test_msg}' doit être dans le fichier de log"
