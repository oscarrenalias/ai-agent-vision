import logging
from typing import List, TypedDict

from copilotkit import CopilotKitState
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from agents.models import OpenAIModel
from agents.tools import recipetools

logger = logging.getLogger(__name__)


class Meal(TypedDict):
    day: str
    type: str
    recipe: str


class ShoppingListState(CopilotKitState):
    meals: List[Meal]
    shopping_list: List[str] = []


class ShoppingListFlow:

    @tool
    @staticmethod
    def initialize_meal_plan(state: ShoppingListState) -> dict:
        """
        Tool to initialize a meal plan.

        Inputs:
        None

        Outputs:
        - description: A human-readable description of the action taken
        - meals: An empty list of meals to start with
        """
        logger.info("Initializing meal plan")
        return {"description": "Meal plan initialized", "meals": []}

    @tool
    @staticmethod
    def add_to_meal_plan(state: ShoppingListState, day: str, type: str, recipe: str) -> dict:
        """
        This tool adds a meal to the meal plan based on the meal (the recipe), the day of the week,
        and the type of meal

        Inputs:
        - day: The day of the week for which to add the meal
        - type: type of meal: dinner, or lunch
        - recipe: the recipe to add to the meal plan

        Outputs:
        - description: A human-readable description of the action taken
        - meals: Updated list of meals in the meal plan
        """
        meal = Meal(day=day, type=type, recipe=recipe)

        logger.info("Calling add_to_meal_plan")
        return {"description": f"Meal added to {day} {type}", "meals": state.get("meals", []) + [meal]}

    @tool
    @staticmethod
    def convert_meal_plan_to_shopping_list(state: ShoppingListState, meals: List[Meal]) -> dict:
        """
        Tool to convert the meal plan to a shopping list.

        Inputs:
        - meals: List of meals in the meal plan

        Outputs:
        - description: A human-readable description of the action taken
        - shopping_list: A shopping list of items
        """
        logger.info("convert_meal_plan_to_shopping_list")

        return {"description": "Meal plan converted to shopping list", "shopping_list": []}

    @tool
    @staticmethod
    def add_to_shopping_list(state: ShoppingListState, item: str) -> dict:
        """
        Tool to add an item to the shopping list.

        Inputs:
        - item: The item to add to the shopping list

        Outputs:
        - description: A human-readable description of the action taken
        - shopping_list: Updated shopping list with the new item added
        """
        logger.info(f"Adding item '{item}' to shopping list")

        # Assuming state has a 'shopping_list' field
        shopping_list = state.get("shopping_list", [])
        shopping_list.append(item)

        return {"description": f"Item '{item}' added to shopping list", "shopping_list": shopping_list}

    def get_tools(self):
        return [
            self.initialize_meal_plan,
            self.add_to_meal_plan,
            self.convert_meal_plan_to_shopping_list,
            *recipetools.get_tools(),
        ]

    async def planning_node(self, state: ShoppingListState, config: RunnableConfig) -> ShoppingListState:
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a helpful assistant that helps to plan meals and manage a shopping list.

                    You should ask the necessary questions from the user to plan a number of meals, for as many
                    days as the user required.

                    You have tools available at your disposal to:

                    - initialize or reset a meal plan
                    - add a meal to the plan
                    - query for recipes in the database
                    - convert a meal plan to a shopping list
                    - add additional items to the shopping list

                    You should plan the days one by one, ask the user if they have any preferences for this day, find
                    matching recipes, ask which one the user would prefer and when the selection is made, add it to the list
                    and move to the next day. All of this should be explained to the user as they are helped
                    through the process.

                    At the end, please call the tool to convert the meal plan to a shopping list so that
                    it can be provided to the user.
                    """
                ),
                ("human", "{messages}"),
                ("human", "Meals so far: {meals}"),
            ]
        )

        model_with_tools = OpenAIModel(use_cache=True).get_model().bind_tools(self.get_tools())
        prompt = prompt_template.invoke({"messages": state.get("messages", ""), "meals": "\n".join(state.get("meals", []))})

        result = await model_with_tools.ainvoke(prompt, config=config)
        messages = [*state["messages"], result]

        return {"messages": messages, "meals": state.get("meals", [])}

    async def tools_node(self, state: ShoppingListState, config: RunnableConfig) -> ShoppingListState:
        """
        Each tool should return a dictionary with:
        - Any state fields to update
        - A 'description' field with a human-readable message about the result
        """
        tools_by_name = {tool.name: tool for tool in self.get_tools()}

        for tool_call in state["messages"][-1].tool_calls:
            try:
                tool_name = tool_call["name"]
                if tool_name not in tools_by_name:
                    error_msg = f"Unknown tool: {tool_name}"
                    logger.error(error_msg)
                    state["messages"].append(ToolMessage(content=error_msg, tool_call_id=tool_call["id"]))
                    continue

                tool = tools_by_name[tool_name]
                tool_args = tool_call["args"]

                logger.debug(f"Invoking tool {tool_name} with args: {tool_args}")
                # call the tool, but inject the current state into calls
                tool_result = await tool.ainvoke({"state": state, **tool_args})

                # try if it's a json string
                import json

                try:
                    tool_result_json = json.loads(tool_result)
                    tool_result = {"description": tool_result_json}
                except json.JSONDecodeError:
                    logger.info("Tool result is not a JSON string, using as is.")
                    tool_result = {"description": str(tool_result)}

                # Process the tool result
                if isinstance(tool_result, dict):
                    # Update state with the tool's result
                    for key, value in tool_result.items():
                        if key != "messages" and key != "description":  # Don't update these special fields
                            state[key] = value

                        tool_msg = tool_result.get("description", str(tool_result))
                else:
                    tool_msg = str(tool_result)

                logger.debug(f"Tool {tool_name} result: {tool_msg}")
                state["messages"].append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

            except Exception as e:
                import traceback

                error_msg = f"Error executing tool {tool_call.get('name', 'unknown')}: {str(e)}"
                stack_trace = traceback.format_exc()
                logger.error(f"Error: {error_msg}, Stack trace: {stack_trace}")
                state["messages"].append(ToolMessage(content=error_msg, tool_call_id=tool_call["id"]))

        return state

    def as_subgraph(self):
        workflow = StateGraph(state_schema=ShoppingListState)

        workflow.add_node("planning_node", self.planning_node)
        workflow.add_node("tools", self.tools_node)

        workflow.add_edge(START, "planning_node")
        workflow.add_edge("tools", "planning_node")
        workflow.add_conditional_edges("planning_node", tools_condition)

        return workflow
