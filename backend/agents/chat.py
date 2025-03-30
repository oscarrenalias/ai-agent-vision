import logging
from datetime import datetime

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import START, Graph, MessagesState
from langgraph.prebuilt import tools_condition

from .models import OpenAIModel

logger = logging.getLogger(__name__)


@tool
def multiply(a: int, y: int) -> int:
    """
    Multiplies two numbers.

    Args:
        a (int): The first number to multiply.
        y (int): The second number to multiply.
    """
    logger.info(f"a={a}, y={y}")
    return a * y


@tool
def get_weather(city: str) -> str:
    """
    Gets the weather for a given city.

    Args:
        city (str): The name of the city to get the weather for.
    """
    logger.info(f"Getting weather for {city}")
    # Simulate a weather API call
    result = "it's very cold" if city.lower() == "helsinki" else "sunny and 25C"
    return result


# List of tools that can be utilized
tools = [multiply, get_weather]


class ChatState(MessagesState):
    pass


class ChatAgent:
    # Keeps track of the LLM model
    model: None

    system_message: str = """
    You are a helpful assistant that can use tools to perform requests.

    IMPORTANT INSTRUCTIONS FOR TOOL USAGE:
    1. Only use tools when necessary to answer the user's question
    2. After you get the tool results, provide a final answer to the user
    3. DO NOT call the same tool repeatedly with the same parameters
    4. Once you have the information needed, respond directly to the user without calling more tools
    5. If you've already called a tool and received results, use those results instead of calling the tool again
    """

    def __init__(self):
        logger.info("Chat initialized")
        model = OpenAIModel(use_cache=False).get_model()

        # bind with tools and keep in the class
        self.model = model.bind_tools(tools)

    def get_primary_assistant_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="You are a helfpul assistant that can use tools to perform requests.\nCurrent time: {time}."
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        ).partial(time=datetime.now)

    def run(self, state: ChatState) -> ChatState:
        # todo: check if this will scale during repeated invocations
        logger.info(f"ChatAgent run invoked with state: {state}")

        model_executor = self.get_primary_assistant_prompt() | self.model

        result = model_executor.invoke(state["messages"])
        logger.info(f"LLM invoke result: {result}")
        state["messages"].append(result)

        logger.info(f"ChatState result returned: {state}")
        return state


class CustomToolNode:
    """Custom tool executor that preserves message history."""

    def __init__(self, tools):
        logging.info(f"CustomToolNod initialized with tools: {tools}")
        self.tools = tools

    def run(self, state: ChatState) -> ChatState:
        """Execute tools while preserving all messages in state."""
        # Get the last message which should contain tool calls
        last_message = state["messages"][-1]
        logger.info(f"CustomToolNode processing {len(last_message.tool_calls)} tool calls")

        # process each tool call and record their results in the messages
        tools_by_name = {tool.name: tool for tool in self.tools}
        for tool_call in last_message.tool_calls:
            tool = tools_by_name[tool_call["name"]]
            tool_msg = tool.invoke(tool_call["args"])
            logger.info(f"Tool call {tool_call['name']}, result: {tool_msg}")
            state["messages"].append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

        logger.info(f"Tool execution complete. State now has {len(state['messages'])} messages")
        return state


class ChatManager:
    """
    Manages the chat session and handles the conversation flow.
    """

    def __init__(self):
        pass

    def run(self, message: str):
        """
        Run the chat session with the provided message.
        """
        # build graph and edges
        chat_agent = ChatAgent()
        workflow = Graph()
        workflow.add_node("chat_agent", chat_agent.run)

        tool_node = CustomToolNode(tools=tools)
        workflow.add_node("tools", tool_node.run)

        workflow.add_edge(START, "chat_agent")
        workflow.add_edge("tools", "chat_agent")
        workflow.add_conditional_edges("chat_agent", tools_condition)

        graph = workflow.compile()

        # Create an initial chat state and call the graph
        initial_state = ChatState(messages=[HumanMessage(content=message)])
        response = graph.invoke(initial_state)
        logger.info(f"Response: {response}")
        return response
