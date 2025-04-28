import logging

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from agents.chat import ChatFlow, ChatState
from common.logging import configure_logging

# set things up
load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)


def main():
    # build the graph and setup the checkpointer
    chat_flow = ChatFlow()
    memory = MemorySaver()
    graph = chat_flow.as_subgraph().compile(checkpointer=memory)

    # Graph configuration
    config = {"configurable": {"thread_id": "1"}}

    # create the state
    state = ChatState()

    """Run the chat in interactive mode, reading input from keyboard."""
    print("\n=== AI Agent Vision Chat ===")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    idx = 0
    step_type = "message"
    while True:
        try:
            user_input_str = input("Your input: ")

            # generate the right type of input for the graph
            if step_type == "message":
                state["input"] = HumanMessage(content=user_input_str)
                user_input = state
            elif step_type == "interrupt":
                user_input = Command(resume=user_input_str)

            print()
            print(f"--- Conversation Turn {idx + 1} ---")
            print()
            print(f"User: {user_input}")
            print()
            for update in graph.stream(
                user_input,
                config=config,
                stream_mode="updates",
            ):
                for node_id, value in update.items():
                    if isinstance(value, dict) and value.get("messages", []):
                        last_message = value["messages"][-1]
                        if isinstance(last_message, dict) or last_message.type != "ai":
                            continue
                        print(f"Response: {node_id}: {last_message.content}")
                        step_type = "message"

                    if "__interrupt__" in node_id:
                        step_type = "interrupt"
                        print(f"Response: {node_id}: {value[-1].value}")

            # increment the index for the next turn
            idx += 1

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
