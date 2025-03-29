import logging

import uvicorn


# Configure logging before starting uvicorn
def configure_logging():
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Configure specific loggers if needed
    for logger_name in ["webapp", "agents", "common"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

    # Prevent uvicorn access logs from overriding our configuration
    logging.getLogger("uvicorn.access").propagate = False


if __name__ == "__main__":
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                # Tweaked the default format for the access log to make it consistent with the rest of the app
                "fmt": '%(asctime)s | %(levelname)-8s | access: %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
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
            # added this app's own loggers to prevent them from being overridden by uvicorn
            "webapp": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "agents": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "common": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
    }

    configure_logging()

    uvicorn.run(
        "webapp.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info",
        log_config=logging_config,  # Use the custom logging configuration
    )
