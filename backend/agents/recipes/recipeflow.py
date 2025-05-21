import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from copilotkit import CopilotKitState
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.types import interrupt
from pydantic import BaseModel, Field, field_serializer, field_validator

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

# TimeRange type is a tuple of (min_time, max_time) where max_time is optional
TimeRange = Tuple[timedelta, Optional[timedelta]]


def format_time_range(time_range: Optional[TimeRange]) -> str:
    """Format a time range into a human-readable string"""
    if not time_range:
        return ""

    min_time, max_time = time_range
    if max_time is None:
        return format_timedelta(min_time)
    return f"{format_timedelta(min_time)} to {format_timedelta(max_time)}"


# Helper functions for timedelta serialization/deserialization
def serialize_timedelta(td: Optional[timedelta]) -> Optional[Dict[str, int]]:
    """Convert timedelta to a MongoDB and JSON-serializable format"""
    if td is None:
        return None
    return {"total_seconds": int(td.total_seconds())}


def deserialize_timedelta(data: Optional[Dict[str, int]]) -> Optional[timedelta]:
    """Recreate timedelta from serialized format"""
    if data is None or "total_seconds" not in data:
        return None
    return timedelta(seconds=data["total_seconds"])


def serialize_time_range(tr: Optional[TimeRange]) -> Optional[List[Dict[str, int]]]:
    """Convert TimeRange to a MongoDB and JSON-serializable format"""
    if tr is None:
        return None
    min_time, max_time = tr
    result = [serialize_timedelta(min_time)]
    if max_time is not None:
        result.append(serialize_timedelta(max_time))
    return result


def deserialize_time_range(data: Optional[List[Dict[str, int]]]) -> Optional[TimeRange]:
    """Recreate TimeRange from serialized format"""
    if not data or not isinstance(data, list) or len(data) == 0:
        return None

    min_time = deserialize_timedelta(data[0])
    max_time = deserialize_timedelta(data[1]) if len(data) > 1 else None

    return (min_time, max_time)


def format_timedelta(td: timedelta) -> str:
    """Format a timedelta into a human-readable string for recipe times."""
    total_minutes = int(td.total_seconds() / 60)
    hours, minutes = divmod(total_minutes, 60)

    if hours > 0 and minutes > 0:
        return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minute{'s' if minutes > 1 else ''}"
    elif hours > 0:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    else:
        return f"{minutes} minute{'s' if minutes > 1 else ''}"


class Recipe(BaseModel):
    name: Optional[str] = Field(description="Name of the recipe")
    description: Optional[str] = Field(description="Description of the recipe")
    ingredients: Optional[List[str]] = Field(description="List of ingredients")
    steps: Optional[List[str]] = Field(description="List of steps to prepare the recipe")

    # min and max cooking and preparation times
    cooking_time_range: Optional[TimeRange] = Field(description="Cooking time range")
    preparation_time_range: Optional[TimeRange] = Field(description="Preparation time range")

    # list of tags
    tags: List[str] = Field(description="List of tags for the recipe")


class ReceiptState(CopilotKitState):
    site_url: Optional[str]
    page_content: Optional[str]
    recipe: Recipe

    def make_instance():
        return ReceiptState(
            site_url=None,
            recipe=Recipe(
                name=None,
                description=None,
                ingredients=[],
                steps=None,
                cooking_time_range=None,
                preparation_time_range=None,
                tags=[],
            ),
        )

    # Serialization for timedelta fields
    @field_serializer("cooking_time", "preparation_time")
    def serialize_timedelta(self, td: Optional[timedelta]) -> Optional[Dict[str, int]]:
        return serialize_timedelta(td)

    # Serialization for TimeRange fields
    @field_serializer("cooking_time_range", "preparation_time_range")
    def serialize_time_range(self, tr: Optional[TimeRange]) -> Optional[List[Dict[str, int]]]:
        return serialize_time_range(tr)

    # Validator to deserialize timedelta from dict when loading from MongoDB
    @field_validator("cooking_time", "preparation_time", mode="before")
    @classmethod
    def deserialize_timedelta(cls, value):
        if isinstance(value, dict) and "total_seconds" in value:
            return timedelta(seconds=value["total_seconds"])
        return value

    # Validator to deserialize TimeRange from dict when loading from MongoDB
    @field_validator("cooking_time_range", "preparation_time_range", mode="before")
    @classmethod
    def deserialize_time_range(cls, value):
        if isinstance(value, list):
            return deserialize_time_range(value)
        return value

    # Convert to MongoDB-friendly dictionary
    def to_mongo(self) -> Dict[str, Any]:
        """Convert to MongoDB-friendly dictionary"""
        # Use Pydantic's model_dump and post-process timedeltas
        data = self.model_dump()
        # No need to process further as field serializers handle the conversion
        return data

    # Create from MongoDB document
    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "ReceiptState":
        """Create instance from MongoDB document"""
        # The field validators will handle conversion back
        return cls.model_validate(data)


class RecipeFlow:
    """
    Recipe flow agent for managing recipes.
    """

    def __init__(self):
        self.state = ReceiptState.make_instance()

    def receipt_agent_check(self, state: ReceiptState, config: RunnableConfig) -> ReceiptState:
        """
        This node is only here to handle the interrupt and provide the URL of the site that contains the recipe.
        """
        state["site_url"] = interrupt("Please provide a URL of the site that contains the recipe.")
        return state

    def get_tools(self) -> list:
        return [self.page_retriever, self.receipt_parser]

    def receipt_agent(self, state: ReceiptState, config: RunnableConfig) -> ReceiptState:
        prompt_template_messages = [
            SystemMessage(
                content="""
                    You are a helpful assistant that can fetch and extract recipes from either a URL, or page content.

                    If you are provided with a URL of a site that should contain a recipe, your first task is to use the
                    page_retriever tool to retrieve the page content.

                    After retrieving the content, or if the state already contains a recipe, your next task is to
                    use the receipt_parser tool to generate a JSON object out of the recipe content. Do not call the page_retriever_tool again.
                    Do not return the JSON payload in your response, just return a brief summary of the recipe for the user.

                    If the page does not contain a recipe, or you cannot retrieve the page content, please
                    return a message indicating the nature of the issue and do not use the tools.
                    """
            ),
            ("human", "Site URL: {site_url}"),
            ("human", "{page_content}"),
            ("human", "{messages}"),
        ]

        prompt_template = ChatPromptTemplate.from_messages(prompt_template_messages)

        prompt = prompt_template.invoke(
            {
                "site_url": state.get("site_url", ""),
                "messages": state.get("messages", []),
                "page_content": state.get("page_content", ""),
            }
        )

        model_with_tools = OpenAIModel(use_cache=True).get_model().bind_tools(self.get_tools())
        result = model_with_tools.invoke(prompt, config=config)
        messages = [*state["messages"], result]

        return {"messages": messages, "recipe": state.get("recipe", "")}

    def tools_node(self, state: ReceiptState, config: RunnableConfig) -> ReceiptState:
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
                tool_result = tool.invoke(tool_args)

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
        - Dictionary with state updates: page_content and site_url
        """
        # Create recipe retriever instance and use it to get the recipe content
        retriever = RecipeRetriever()
        return retriever.retrieve_recipe(url)

    @tool
    @staticmethod
    def receipt_parser(page_content: str) -> Dict[str, Any]:
        """
        Parse the page content to extract the recipe.

        Parameters:
        - page_content: Content of the page

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
                    - preparation time: min and max range, if known (format as minutes)
                    - cooking time: min and max range, if known (format as minutes)
                    - tags: list of tags, such as complexity (easy, medium, etc), effort required (quick, long, etc)
                    taste (sweet, savory, etc), main ingredients (fruit, meat, pasta), type of meal (dinner, lunch, breakfast, vegan)

                    Important guidelines:
                    1. Steps MUST be returned as an array of strings, with each step as a separate item
                    2. Convert any imperial measurements to metric equivalents
                    3. Extract cooking and preparation times in minutes
                    4. Include a rich set of relevant tags to facilitate searching and categorization
                    5. If the content appears to be pre-structured (like from recipe-scrapers), preserve that structure
                    """
                ),
                ("human", "Page content: {page_content}"),
                ("human", "{parser_instructions}"),
            ]
        )

        extraction_model = OpenAIModel(use_cache=True).get_model()
        chain = extraction_model | json_output_parser

        prompt = prompt_template.invoke(
            {"page_content": page_content, "parser_instructions": json_output_parser.get_format_instructions()}
        )

        result = chain.invoke(prompt)

        recipe = result.content if hasattr(result, "content") else result

        # Create a description based on the recipe content
        description = "Parsed recipe content"
        if recipe and hasattr(recipe, "name") and recipe.name:
            description = f"Successfully parsed recipe: {recipe.name}"

        # Return state updates directly with description
        return {"recipe": recipe, "description": description}

    def as_subgraph(self):
        workflow = StateGraph(state_schema=ReceiptState)

        workflow.add_node("receipt_agent", self.receipt_agent)
        workflow.add_node("receipt_agent_check", self.receipt_agent_check)
        workflow.add_node("tools", self.tools_node)

        workflow.add_edge(START, "receipt_agent_check")
        workflow.add_edge("receipt_agent_check", "receipt_agent")
        workflow.add_edge("tools", "receipt_agent")
        workflow.add_conditional_edges("receipt_agent", tools_condition)

        return workflow


# MongoDB customization example - for PyMongo
def setup_mongodb_codecs():
    """
    Example of setting up custom codecs for PyMongo if needed
    """
    from bson.codec_options import CodecOptions, TypeCodec, TypeRegistry

    class TimedeltaCodec(TypeCodec):
        python_type = timedelta
        bson_type = dict

        def transform_python(self, value):
            return serialize_timedelta(value)

        def transform_bson(self, value):
            return deserialize_timedelta(value)

    # Register the codec with PyMongo
    type_registry = TypeRegistry([TimedeltaCodec()])
    codec_options = CodecOptions(type_registry=type_registry)

    # Use with your MongoDB client
    # Example: db.get_collection('recipes', codec_options=codec_options)

    return codec_options
