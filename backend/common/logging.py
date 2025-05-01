import logging
import logging.config

# ANSI color codes for log levels
LOG_COLORS = {
    "DEBUG": "\033[95m",  # Purple
    "INFO": "\033[92m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[91m",  # Red (same as error)
}
RESET_COLOR = "\033[0m"


class ColoredLevelFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in LOG_COLORS:
            record.levelname = f"{LOG_COLORS[levelname]}{levelname.upper()}{RESET_COLOR}"
        else:
            levelname = levelname.lower()
        return super().format(record)


logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": ColoredLevelFormatter,
            "fmt": "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(asctime)s | %(levelname)-8s | access: %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "webapp": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "agents": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "common": {"handlers": ["default"], "level": "INFO", "propagate": False},
    },
}


def configure_logging(default_log_level=logging.INFO):
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    logging.config.dictConfig(logging_config)

    # Configure our own specific loggers
    info_loggers = ["agents", "common"]
    for logger_name in info_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(default_log_level)

    # This pesky logger is used by langchain and we don't want to see its output
    logging.getLogger("httpx").disabled = True
