import logging
from typing import Any, Dict, List, Optional

from copilotkit import CopilotKitState
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.types import interrupt
from pydantic import BaseModel, Field

from agents.models import OpenAIModel
from agents.recipes.reciperetriever import RecipeRetriever

"""
from agents.recipes.recipeflow import RecipeFlow
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from dotenv import load_dotenv
load_dotenv(verbose=True)
config = {"configurable": { "thread_id": 1 }}
g = RecipeFlow().as_subgraph().compile(checkpointer=MemorySaver())
g.invoke({"messages": ""}, config=config)
result = g.invoke(Command(resume="https://breaddad.com/easy-banana-bread-recipe/"), config=config)
print(f"Recipe: {result.recipe}")
"""

logger = logging.getLogger(__name__)

# New format for time ranges: {"min": minutes, "max": minutes}
# Both min and max are integer values representing minutes


class Recipe(BaseModel):
    name: Optional[str] = Field(description="Name of the recipe")
    description: Optional[str] = Field(description="Description of the recipe")
    ingredients: Optional[List[str]] = Field(description="List of ingredients")
    steps: Optional[List[str]] = Field(description="List of steps to prepare the recipe")
    yields: Optional[int] = Field(description="Number of yields for this recipe")
    url: Optional[str] = Field(description="Original site with the source for this recipe")

    # min and max cooking and preparation times as dictionaries with minutes
    cooking_time: Optional[int] = Field(description="Cooking time in minutes")
    preparation_time: Optional[int] = Field(description="Preparation time in minutes")

    # list of tags
    tags: List[str] = Field(description="List of tags for the recipe")


class RecipeState(CopilotKitState):
    site_url: Optional[str]
    recipe_content: Optional[str]
    recipe: Recipe

    def make_instance():
        return RecipeState(
            site_url=None,
            recipe=Recipe(
                name=None,
                description=None,
                ingredients=[],
                steps=None,
                cooking_time=None,
                preparation_time=None,
                yields=None,
                url=None,
                tags=[],
            ),
        )


class RecipeFlow:
    """
    Recipe flow agent for managing recipes.
    """

    def __init__(self):
        self.state = RecipeState.make_instance()

    async def receipt_agent_check(self, state: RecipeState, config: RunnableConfig) -> RecipeState:
        """
        This node is only here to handle the interrupt and provide the URL of the site that contains the recipe.
        """
        top_message = state["messages"][-1].content.strip()
        if top_message == "":
            # no message, we need to ask for the URL
            state["site_url"] = interrupt(
                "Please provide a URL of the site that contains the recipe, or paste the text of the recipe."
            )
        else:
            # there is some body, let's assume it's a receipt
            state["recipe_content"] = top_message

        return state

    def get_tools(self) -> list:
        return [self.page_retriever, self.recipe_parser, self.save_recipe_tool]

    async def receipt_agent(self, state: RecipeState, config: RunnableConfig) -> RecipeState:
        prompt_template_messages = [
            SystemMessage(
                content="""
                    You are a helpful assistant that can fetch and extract recipes from either a URL, or page content.

                    If you are provided with something that looks like URL of a site that should contain a recipe, your first task is to use the
                    page_retriever tool to retrieve the page content.

                    If you are provided with a block of text that looks like a recipe, instead of a URL, your next task is to
                    use the recipe_parser tool.

                    After retrieving the content, or if the state already contains a recipe, your next task is to
                    use the recipe_parser tool to generate a JSON object out of the recipe content. Do not call the page_retriever_tool again.
                    Do not return the JSON payload in your response, just return a brief summary of the recipe for the user.

                    After the recipe has been parsed, it can be saved to the database with the save_recipe_tool. Only do this when
                    there is a JSON object representing the receipt in the state, do not attempt to save a receipt that is still
                    in plain text format. After saving the receipt, you can end the flow.

                    If you are provided with text that does not look like a receipt, the page does not contain a recipe, or you cannot
                    retrieve the page content, please return a message indicating the nature of the issue and do not use the tools.
                    """
            ),
            ("human", "Site URL: {site_url}"),
            ("human", "{recipe_content}"),
            ("human", "{messages}"),
        ]

        prompt_template = ChatPromptTemplate.from_messages(prompt_template_messages)

        prompt = prompt_template.invoke(
            {
                "site_url": state.get("site_url", ""),
                "messages": state.get("messages", []),
                "recipe_content": state.get("recipe_content", ""),
            }
        )

        model_with_tools = OpenAIModel(use_cache=True).get_model().bind_tools(self.get_tools())
        result = await model_with_tools.ainvoke(prompt, config=config)
        messages = [*state["messages"], result]

        return {"messages": messages, "recipe": state.get("recipe", "")}

    async def tools_node(self, state: RecipeState, config: RunnableConfig) -> RecipeState:
        """
        Process tool calls and update state with tool results.
        Implements Option 3: Tools return state updates directly with a standard format.

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
                tool_result = await tool.ainvoke(tool_args)

                # Process the tool result
                if isinstance(tool_result, dict):
                    # Update state with the tool's result (Option 3 approach)
                    for key, value in tool_result.items():
                        if key != "messages" and key != "description":  # Don't update these special fields
                            state[key] = value

                    # Use the tool's provided description or fall back to string representation
                    tool_msg = tool_result.get("description", str(tool_result))
                else:
                    # Fallback for tools that don't return state updates
                    tool_msg = str(tool_result)

                logger.debug(f"Tool {tool_name} result: {tool_msg}")
                state["messages"].append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

            except Exception as e:
                error_msg = f"Error executing tool {tool_call.get('name', 'unknown')}: {str(e)}"
                logger.error(error_msg)
                state["messages"].append(ToolMessage(content=error_msg, tool_call_id=tool_call["id"]))

        return state

    @tool
    @staticmethod
    def page_retriever(url: str) -> Dict[str, Any]:
        """
        Retrieve the page content from the given URL so that it can be provided back to the
        LLM to extract the recipe.

        Parameters:
        - url: URL of the page to retrieve

        Returns:
        - Dictionary with state updates: recipe_content and site_url
        """
        # Create recipe retriever instance and use it to get the recipe content
        retriever = RecipeRetriever()
        return retriever.retrieve_recipe(url)

    @tool
    @staticmethod
    def recipe_parser(recipe_content: str) -> Dict[str, Any]:
        """
        Parse the page content to extract the recipe.

        Parameters:
        - recipe_content: Content of the page

        Returns:
        - Dictionary with state updates containing the parsed recipe in JSON format
        """
        json_output_parser = JsonOutputParser(pydantic_object=Recipe)
        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a helpful assistant that can extract recipes from the given page content.

                    You are provided with the contents from a website that contains a recipe. Your task is to process its contents
                    and generate a recipe with the following structure:

                    - Name of the recipe
                    - List of ingredients: please convert the measurements to metric
                    - List of steps: Extract the preparation steps as a list of individual steps, not as a single blob of text
                    - preparation time: A dictionary with 'min' and optional 'max' keys, with integer values in minutes
                    - cooking time: A dictionary with 'min' and optional 'max' keys, with integer values in minutes
                    - tags: list of tags, such as complexity (easy, medium, etc), effort required (quick, long, etc)
                    taste (sweet, savory, etc), main ingredients (fruit, meat, pasta), type of meal (dinner, lunch, breakfast, vegan)

                    Important guidelines:
                    1. Steps MUST be returned as an array of strings, with each step as a separate item
                    2. Convert any imperial measurements to metric equivalents
                    3. Extract cooking and preparation times as dictionaries with 'min' and optional 'max' keys, with values in minutes
                    4. Include a rich set of relevant tags to facilitate searching and categorization
                    5. If the content appears to be pre-structured (like from recipe-scrapers), preserve that structure
                    """
                ),
                ("human", "Recipe content: {recipe_content}"),
                ("human", "{parser_instructions}"),
            ]
        )

        extraction_model = OpenAIModel(use_cache=True).get_model()
        chain = extraction_model | json_output_parser

        prompt = prompt_template.invoke(
            {"recipe_content": recipe_content, "parser_instructions": json_output_parser.get_format_instructions()}
        )

        result = chain.invoke(prompt)

        recipe = result.content if hasattr(result, "content") else result

        # Create a description based on the recipe content
        description = "Parsed recipe content"
        if recipe and hasattr(recipe, "name") and recipe.name:
            description = f"Successfully parsed recipe: {recipe.name}"

        # Return state updates directly with description
        return {"recipe": recipe, "description": description}

    @tool
    @staticmethod
    def save_recipe_tool(recipe: Recipe) -> dict:
        """
        This tool persists a Recipe object to the data store.

        Parameters:
        - recipe: an object of type Recipe

        Returns:
        - A dictionary with state updates
        """
        try:
            from common.repository_factory import get_recipe_repository

            # Get the recipe repository instance
            recipe_repo = get_recipe_repository()

            # Save the recipe to the database
            recipe_id = recipe_repo.save_recipe(recipe)

            if not recipe_id:
                return {"description": "Failed to save recipe to the database.", "success": False}

            return {
                "description": f"Recipe '{recipe.name}' saved successfully with ID: {recipe_id}",
                "recipe_id": recipe_id,
                "success": True,
            }

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Error saving recipe: {str(e)}")
            return {"description": f"Error saving recipe: {str(e)}", "success": False}

    def as_subgraph(self):
        workflow = StateGraph(state_schema=RecipeState)

        workflow.add_node("receipt_agent", self.receipt_agent)
        workflow.add_node("receipt_agent_check", self.receipt_agent_check)
        workflow.add_node("tools", self.tools_node)

        workflow.add_edge(START, "receipt_agent_check")
        workflow.add_edge("receipt_agent_check", "receipt_agent")
        workflow.add_edge("tools", "receipt_agent")
        workflow.add_conditional_edges("receipt_agent", tools_condition)

        return workflow
