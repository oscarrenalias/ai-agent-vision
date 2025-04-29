import logging

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.types import Command

from agents.chat import ChatFlow, ChatState
from agents.common import make_classifier
from agents.mealplanner import MealPlannerFlow, MealPlannerState
from common.logging import configure_logging

# set things up
load_dotenv()
configure_logging(logging.DEBUG)
logger = logging.getLogger(__name__)


# overall global state
class GlobalState(MessagesState):
    def make_instance():
        return GlobalState(messages=[])


# checkpointer
memory = MemorySaver()

# graph configuration
config = {"configurable": {"thread_id": "1"}}

# chat graph
chat_flow = ChatFlow()
chat_graph = chat_flow.as_subgraph().compile()

# meal planner graph
meal_planner_flow = MealPlannerFlow()
meal_planner_graph = meal_planner_flow.as_subgraph().compile()

main_flow = StateGraph(state_schema=GlobalState)


def chat_graph_node(global_state: GlobalState) -> dict:
    # initialize the new state
    chat_state = ChatState.make_instance()
    chat_state["messages"] = global_state["messages"].copy()
    chat_state["input"] = global_state["messages"][-1]

    # Run the chat_graph with the converted state
    chat_result = chat_graph.invoke(chat_state, config=config)

    # let langgraph update the state with the new messages
    return {"messages": chat_result["messages"]}


def meal_planner_graph_node(global_state: GlobalState) -> dict:
    # initialize the new state
    meal_planner_state = MealPlannerState.make_instance()
    meal_planner_state["messages"] = global_state["messages"].copy()

    # Run the meal_planner with the converted state
    meal_planner_result = meal_planner_graph.invoke(meal_planner_state, config=config)

    # let langgraph update the state with the new messages
    return {"messages": meal_planner_result["messages"]}


# main_flow.add_node("chat", chat_graph)
main_flow.add_node("chat", chat_graph_node)
main_flow.add_node("meal_planner", meal_planner_graph_node)

# add routing
classifier_routes = {
    "meal_planner": "If the message is about meal planning. Example: I want to plan my meals for the week.",
    "chat": "Everything else. Example: I want to chat with you.",
}
main_flow.add_conditional_edges(START, make_classifier(routing_map=classifier_routes, default_node="chat"))

# Configure and compile the graph
main_graph = main_flow.compile(checkpointer=memory)

state = GlobalState.make_instance()

message_list = [
    # goes to chat
    HumanMessage(content="My name is John Doe"),
    # goes to meal planner
    HumanMessage(
        content="""
        I'd like to plan dinners for the weekend, only two persons. No dietary restrictions. Our budget
        is up to 100 euros. We like mediterranean food, pasta and salads. Please suggest a meal plan.
    """
    ),
]

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
            state["messages"].append(state["input"])
            user_input = state
        elif step_type == "interrupt":
            user_input = Command(resume=user_input_str)

        print()
        print(f"--- Conversation Turn {idx + 1} ---")
        print()
        print(f"User: {user_input}")
        print()
        for update in main_graph.stream(
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
