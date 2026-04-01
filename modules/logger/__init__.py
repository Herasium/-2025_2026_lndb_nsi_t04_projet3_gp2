from modules.data import data
import datetime
from typing import List


class Logger:

    def __init__(self, name: str) -> None:

        self.name: str = name

        self.levels: List[str] = [
            "DEBUG",
            "INFO",
            "SUCCESS",
            "WARNING",
            "ERROR",
        ]

        self.colors: List[str] = [
            "\033[0m",
            "\033[36m",
            "\033[92m",
            "\033[33m",
            "\033[31m",
        ]

        self.history: List[str] = []

    def _header(self, level: int) -> str:

        timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d | %H:%M:%S.%f")

        header: str = (
            f"{self.colors[level]}LogicBox v.{data.VERSION} | {self.name} | {timestamp} | {self.levels[level]} | "
        )

        return header

    def debug(self, message: str) -> None:

        if data.LOGGER_MIN > 0:
            return
        log_data: str = f"{self._header(0)}{message}{self.colors[0]}"
        self.history.append(log_data)
        print(log_data)

    def print(self, message: str) -> None:

        if data.LOGGER_MIN > 1:
            return
        log_data: str = f"{self._header(1)}{message}{self.colors[0]}"
        self.history.append(log_data)
        print(log_data)

    def info(self, message: str) -> None:

        if data.LOGGER_MIN > 1:
            return
        log_data: str = f"{self._header(1)}{message}{self.colors[0]}"
        self.history.append(log_data)
        print(log_data)

    def success(self, message: str) -> None:

        if data.LOGGER_MIN > 2:
            return
        log_data: str = f"{self._header(2)}{message}{self.colors[0]}"
        self.history.append(log_data)
        print(log_data)

    def warning(self, message: str) -> None:

        if data.LOGGER_MIN > 2:
            return
        log_data: str = f"{self._header(3)}{message}{self.colors[0]}"
        self.history.append(log_data)
        print(log_data)

    def error(self, message: str) -> None:

        if data.LOGGER_MIN > 4:
            return
        log_data: str = f"{self._header(4)}{message}{self.colors[0]}"
        self.history.append(log_data)
        print(log_data)