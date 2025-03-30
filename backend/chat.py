import argparse
import logging

from dotenv import load_dotenv

from agents.chat import ChatManager


# Configure logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Configure specific loggers
    for logger_name in ["agents", "common"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)


logger = logging.getLogger(__name__)

load_dotenv()

chat_manager = ChatManager()


def interactive_chat_mode():
    """Run the chat in interactive mode, reading input from keyboard."""
    print("\n=== AI Agent Vision Chat ===")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")

            # Check if user wants to exit
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            # Process the user input
            result = chat_manager.run(message=user_input)

            # Extract the last AI message for display
            if result and "messages" in result and len(result["messages"]) > 0:
                last_message = result["messages"][-1]
                if hasattr(last_message, "content"):
                    print(f"\nAI: {last_message.content}")
                else:
                    print(f"\nAI: {last_message}")
            else:
                print("\nAI: No response generated.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            print(f"\nAn error occurred: {e}")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Agent Vision Chat")
    parser.add_argument("-i", action="store_true", help="Run in interactive chatbot mode")
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    if args.i:
        # Run in interactive mode
        interactive_chat_mode()
    else:
        # Run with a predefined question
        result = chat_manager.run(message="What is 3 times 2?")
        logger.info(f"Chat complete. Result: {result}")
        return result


if __name__ == "__main__":
    configure_logging()
    main()
