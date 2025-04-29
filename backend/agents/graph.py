from langgraph.graph import START, MessagesState, StateGraph

from agents.chat import ChatFlow, ChatState
from agents.common import make_classifier
from agents.mealplanner import MealPlannerFlow, MealPlannerState


# overall global state
class GlobalState(MessagesState):
    def make_instance():
        return GlobalState(messages=[])


class Graph:
    def __init__(self, config=None):
        self.config = config

    def as_subgraph(self):
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
            chat_result = chat_graph.invoke(chat_state, config=self.config)

            # let langgraph update the state with the new messages
            return {"messages": chat_result["messages"]}

        def meal_planner_graph_node(global_state: GlobalState) -> dict:
            # initialize the new state
            meal_planner_state = MealPlannerState.make_instance()
            meal_planner_state["messages"] = global_state["messages"].copy()

            # Run the meal_planner with the converted state
            meal_planner_result = meal_planner_graph.invoke(meal_planner_state, config=self.config)

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
        # main_graph = main_flow.compile(checkpointer=memory)

        return main_flow
