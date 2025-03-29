import logging

import uvicorn


# Configure logging before starting uvicorn
def configure_logging():
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Configure specific loggers if needed
    for logger_name in ["webapp", "agents", "common"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

    # Prevent uvicorn access logs from overriding our configuration
    logging.getLogger("uvicorn.access").propagate = False


if __name__ == "__main__":
    configure_logging()

    uvicorn.run(
        "webapp.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info",
    )
