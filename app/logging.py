import logging
from enum import StrEnum

"""
%(levelname)s → logging level (INFO, ERROR, DEBUG, WARN)
%(message)s → the actual message you log
%(pathname)s → full path of the Python file where the log was triggered
%(funcName)s → function name where it happened
%(lineno)d → line number in the file
"""
LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


class LogLevels(StrEnum):
    """
    INFO (general app flow)
    WARNING (something odd, but not fatal)
    ERROR (failure in one part of the app)
    DEBUG (developer’s microscope)
    """

    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def configure_logging(log_level: str = LogLevels.error):
    """
    This sets up the logging system for your app.
    Default log level is ERROR.
    """

    log_level = str(log_level).upper()
    log_levels = [level.value for level in LogLevels]

    # If level not valid, falls back to ERROR
    if log_level not in log_levels:
        logging.basicConfig(level=LogLevels.error)
        return

    # If the chosen level is DEBUG, it uses the special detailed format.
    if log_level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=log_level)
