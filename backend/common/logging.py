import logging


def configure_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Configure our own specific loggers
    info_loggers = ["agents", "common"]
    for logger_name in info_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

    # This pesky logger is used by langchain and we don't want to see its output
    logging.getLogger("httpx").disabled = True
