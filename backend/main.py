import logging
import sys

from dotenv import load_dotenv

from agents import Orchestrator


# Configure logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Configure specific loggers
    for logger_name in ["agents", "common"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)


# Create a logger for this module
logger = logging.getLogger(__name__)


def main():
    # Use the first command line argument as image path or default to the sample
    receipt_image_path = sys.argv[1] if len(sys.argv) > 1 else "../data/samples/receipt_sample_1.jpg"

    logger.info(f"Processing receipt image: {receipt_image_path}")

    # Run the orchestrator agent
    load_dotenv()
    orchestrator = Orchestrator()
    result = orchestrator.run(receipt_image_path=receipt_image_path)

    logger.info(f"Processing complete. Receipt data: {result}")
    return result


if __name__ == "__main__":
    configure_logging()
    main()
