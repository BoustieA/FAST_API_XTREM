from pathlib import Path

from loguru import logger as loguru_logger


class LoggerManager:
    _instance = None

    def __new__(cls):
        """Implementation of the Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        self.logs_dir = Path(__file__).parent.parent / "logs"
        self._logger = loguru_logger  # Store the logger in a private attribute
        self._configure()

    def _configure(self):
        """Internal logger configuration"""
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        # Confirm directory creation
        print(
            f"Log directory created at: {self.logs_dir}")

        self._logger.add(
            self.logs_dir / "app.log",
            rotation="10 MB",
            level="INFO",
            enqueue=True,
            backtrace=True,
            encoding="utf-8",
        )
        print(
            "Logger configured successfully.")  # Confirm logger configuration

    @property
    def logger(self):
        return self._logger  # Return the private logger attribute

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
        """Exception handling decorator"""
        return self.logger.catch(exception)

    def __repr__(self):
        return f"<LoggerManager logs_dir={self.logs_dir}>"
