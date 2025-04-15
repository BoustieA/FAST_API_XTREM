from pathlib import Path

from loguru import logger as loguru_logger


class LoggerManager:
    _instance = None

    def __new__(cls):
        """Implémentation du pattern Singleton"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.logger = loguru_logger
        self._configure()

    def _configure(self):
        """Configuration interne du logger"""
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.logger.add(
            self.logs_dir / "app.log",
            rotation="10 MB",
            level="INFO",
            enqueue=True,
            backtrace=True,
            encoding="utf-8"
        )

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str):
        self.logger.error(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def success(self, message: str):
        self.logger.success(message)

    def catch(self, exception=Exception):
        """Décorateur de gestion d'exceptions"""
        return self.logger.catch(exception)

    def __repr__(self):
        return f"<LoggerManager logs_dir={self.logs_dir}>"
