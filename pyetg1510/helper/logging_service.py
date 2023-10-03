"""Python Logging 制御モジュール"""
from logging.handlers import SysLogHandler
from logging.handlers import RotatingFileHandler
from logging import handlers
import logging
import socket
from enum import Enum
import os


class LoggingLevel(Enum):
    ALL: logging = logging.NOTSET
    DEBUG: logging = logging.DEBUG
    INFO: logging = logging.INFO
    WARNING: logging = logging.WARNING
    ERROR: logging = logging.ERROR
    CRITICAL: logging = logging.CRITICAL
    DISABLE: None = None


class SysLog:
    address: str = "127.0.0.1"
    port: int = handlers.SYSLOG_UDP_PORT
    facility: int = handlers.SysLogHandler.LOG_USER
    socktype: socket = socket.SOCK_DGRAM
    file_path: os.PathLike = "../../soft.log"
    app_name: str = __name__
    logger: logging.Logger = logging.getLogger(app_name)

    @classmethod
    def console_log_configuration(cls, level: LoggingLevel = logging.CRITICAL):
        log_level = level.value
        if log_level is not None:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(
                logging.Formatter("%(asctime)s : %(levelname)s : %(module)s : %(lineno)d : %(message)s")
            )
            stream_handler.setLevel(log_level)
            cls.logger.addHandler(stream_handler)

    @classmethod
    def rotation_log_configuration(cls, level: LoggingLevel = logging.CRITICAL):
        log_level = level.value
        if log_level is not None:
            filename = cls.file_path
            file_handler = RotatingFileHandler(filename=filename, maxBytes=100000, backupCount=10, encoding="utf-8")

            file_handler.setFormatter(
                logging.Formatter("%(asctime)s : %(levelname)s : %(module)s : %(lineno)d : %(message)s")
            )
            file_handler.setLevel(log_level)
            cls.logger.addHandler(file_handler)

    @classmethod
    def syslog_configuration(cls, level: LoggingLevel = logging.CRITICAL):
        log_level = level.value
        if log_level is not None:
            formatter = logging.Formatter(cls.app_name + ": %(levelname)s : %(module)s : %(lineno)d : %(message)s")

            syslog_handler = SysLogHandler(
                address=(cls.address, cls.port),
                facility=cls.facility,
                socktype=cls.socktype,
            )
            syslog_handler.setFormatter(formatter)
            syslog_handler.setLevel(log_level)
            cls.logger.addHandler(syslog_handler)

    @classmethod
    def set_loglevel(cls, level: LoggingLevel = logging.CRITICAL):
        cls.logger.setLevel(level.value)
