import logging

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from agents.mealplanner import MealPlannerFlow
from agents.mealplanner.mealplanner import MealPlannerState


# Configure logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(module)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Configure specific loggers
    for logger_name in ["agents", "common"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)


# set things up
load_dotenv()
configure_logging()
logger = logging.getLogger(__name__)


def main():
    load_dotenv()

    # build the graph and setup the checkpointer
    meal_planner = MealPlannerFlow()
    memory = MemorySaver()
    graph = meal_planner.as_subgraph().compile(checkpointer=memory)

    # Graph configuration
    config = {"configurable": {"thread_id": "1"}}

    # create the state
    state = MealPlannerState()

    def run_interactive_mode():
        idx = 0
        step_type = "message"
        while True:
            user_input_str = input("Your input: ")

            # generate the right type of input for the graph
            if step_type == "message":
                state.messages = [HumanMessage(content=user_input_str)]
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

    def run_automatic_mode():
        # initialize the state and push the first message
        state.messages = [(HumanMessage(content="I'd like to plan meals for 4 people."))]

        inputs = [
            # 1st round of conversation,
            state,
            # Since we're using `interrupt`, we'll need to resume using the Command primitive.
            # 2nd round of conversation,
            Command(resume="I need to plan just for the week."),
            Command(resume="I like fish, as well as indian food"),
            Command(resume="I am only interested in dinner meals."),
            Command(resume="My budget is between 50 and 100 euros."),
        ]

        for idx, user_input in enumerate(inputs):
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

                    if "__interrupt__" in node_id:
                        print(f"Response: {node_id}: {value[-1].value}")

    # parse command line arguments, if "-i" is provided, then run in interactive mode
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        run_interactive_mode()
    else:
        run_automatic_mode()


if __name__ == "__main__":
    main()
