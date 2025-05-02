import logging
from datetime import datetime
from typing import List

from copilotkit.state import CopilotKitState
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition

from agents.common.logging_utils import llm_response_to_log
from agents.models import OpenAIModel
from agents.pricecomparison import price_lookup_tools
from agents.tools import receipttools

logger = logging.getLogger(__name__)


class ChatState(CopilotKitState):
    input: HumanMessage = None
    items: List[dict] = None

    def make_instance():
        return ChatState(
            messages=[],
            input=None,
        )


class ChatFlow:
    llm_model: None

    def __init__(self, llm_model=None):
        llm_model = llm_model or OpenAIModel(use_cache=False).get_model()
        # allow the model to do price lookups
        self.llm_model = llm_model.bind_tools(self.get_tools())

    def get_tools(self) -> list:
        return price_lookup_tools.get_tools() + receipttools.get_tools()

    def get_primary_assistant_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                You are a helfpul assistant that can use tools to perform requests.

                Current time: {time}.
                """
                ),
                ("human", "{input}"),
                ("placeholder", "{messages}"),
            ]
        ).partial(time=datetime.now)

    async def chat_agent(self, state: ChatState, config: RunnableConfig) -> dict:
        logger.debug(f"run invoked with state: {llm_response_to_log(state)}")

        # store the latest human input
        messages = state["messages"].copy()
        messages.append(state["input"])

        prompt = self.get_primary_assistant_prompt().invoke({"messages": messages, "input": state["input"]})
        result = await self.llm_model.ainvoke(prompt)

        logger.debug(f"Result returned: {llm_response_to_log(result)}")

        # store the response and return the modified state object
        messages.append(result)
        return {"messages": messages}

    # Custom tool node so that we can return the items from the price lookup tool
    # and use them in the next steps through the state, if needed
    def chat_tool_node(self, state: ChatState) -> dict:
        last_message = state["messages"][-1]
        logger.info(f"Processing {len(last_message.tool_calls)} tool calls")

        # process each tool call and record their results in the messages
        tools_by_name = {tool.name: tool for tool in self.get_tools()}
        messages = []
        items = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            tool = tools_by_name[tool_name]
            tool_msg = tool.invoke(tool_call["args"])
            logger.debug(f"Tool call {tool_name}, result: {tool_msg}")
            if "price_lookup" in tool_name:
                logger.debug(f"Processing results from price lookup tool: {tool}")
                messages.append(ToolMessage(content=tool_msg["message"], tool_call_id=tool_call["id"]))
                items.append(tool_msg["items"])
            else:
                messages.append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

        logger.info(f"Tool execution complete. State now has {len(messages)} messages")

        return {
            "messages": messages,
            "items": items,
        }

    def as_subgraph(self):
        """
        Returns the workflow (StateGraph) before compilation, so it can be used as a subgraph in other graphs.
        """
        # needs to be StateGraph so that the chatbot remembers previous interactions
        workflow = StateGraph(state_schema=ChatState)
        workflow.add_node("chat_agent", self.chat_agent)
        # workflow.add_node("tools", make_tool_node(messages_key="messages", tools=self.get_tools()))
        workflow.add_node("tools", self.chat_tool_node)

        workflow.add_edge(START, "chat_agent")
        workflow.add_edge("tools", "chat_agent")
        workflow.add_conditional_edges("chat_agent", tools_condition)

        return workflow
