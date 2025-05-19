import json
import logging
from datetime import datetime
from typing import List

from copilotkit import CopilotKitState
from copilotkit.langgraph import copilotkit_customize_config
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
            items=[],
        )


class ChatFlow:
    llm_model: None

    """
    Use this attribute to set the maximum number of messages to keep in the chat history. More messages
    will be summarized and kept in the chat history. The default is 6 messages.
    """
    max_messages: int

    def __init__(self, llm_model=None, max_messages=6):
        llm_model = llm_model or OpenAIModel(use_cache=False).get_model()
        # allow the model to do price lookups
        self.llm_model = llm_model.bind_tools(self.get_tools())
        self.max_messages = max_messages

    def get_tools(self) -> list:
        return price_lookup_tools.get_tools() + receipttools.get_tools()

    def get_primary_assistant_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                You are a helfpul assistant that can use tools to perform requests related to:

                - grocery shopping
                - price comparison and price lookups, which you can perform using price lookup toools

                If asked to perform a price lookup, you will use the tools to perform the lookup and return the results. Do
                not return the results of the tool calls in the response, but instead do an analysis and return the
                most relevant information to the user such as the highest price, lowest price. The rest of items from the
                tools call will be presented to the user in a specifi format, hence you do not need to return them.

                Current time: {time}.
                """
                ),
                ("human", "{input}"),
                ("placeholder", "{messages}"),
            ]
        ).partial(time=datetime.now)

    async def summarize_messages(self, messages: list, config: RunnableConfig) -> str:
        """
        Summarize a list of messages using the LLM. Returns a summary string.
        """
        modifiedConfig = copilotkit_customize_config(
            config,
            emit_messages=False,  # if you want to disable message streaming
        )

        summary_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="Summarize the following conversation history for future context. Be concise but preserve important facts, decisions, and user preferences."
                ),
                ("placeholder", "{messages}"),
            ]
        )
        prompt = summary_prompt.invoke({"messages": messages})
        model = OpenAIModel(use_cache=False, openai_model="gpt-4.1-nano").get_model()
        summary = await model.ainvoke(prompt, config=modifiedConfig)
        return str(summary.content) if hasattr(summary, "content") else str(summary)

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

    async def chat_summarize_node(self, state: ChatState, config: RunnableConfig) -> dict:
        """
        Summarize old messages in the chat history if needed, and return updated state.
        """
        messages = state["messages"].copy()
        if len(messages) > self.max_messages:
            logger.debug(f"Chat history is too long, summarizing the last {len(messages)} messages")
            old_messages = messages[: -self.max_messages]
            recent_messages = messages[-self.max_messages :]
            if old_messages:
                from langchain_core.messages import AIMessage, ToolMessage

                last_turn_idx = None
                for i in reversed(range(len(old_messages))):
                    if isinstance(old_messages[i], (AIMessage, ToolMessage)):
                        last_turn_idx = i
                        break
                if last_turn_idx is not None:
                    to_summarize = old_messages[: last_turn_idx + 1]
                    to_keep = old_messages[last_turn_idx + 1 :] + recent_messages
                else:
                    to_summarize = old_messages
                    to_keep = recent_messages

                def msg_to_str(msg):
                    if hasattr(msg, "content"):
                        return str(msg.content)
                    return str(msg)

                old_messages_str = [msg_to_str(m) for m in to_summarize]
                summary_text = await self.summarize_messages(old_messages_str, config=config)
                summary_message = SystemMessage(content=f"Summary of previous conversation and tool results: {summary_text}")
                messages = [summary_message] + to_keep
        return {"messages": messages, "input": state["input"], "items": state.get("items", [])}

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

                content = json.dumps(tool_msg["items"])
                # messages.append(ToolMessage(content=tool_msg["message"], tool_call_id=tool_call["id"]))
                messages.append(ToolMessage(content=content, tool_call_id=tool_call["id"]))
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
        workflow = StateGraph(state_schema=ChatState)
        workflow.add_node("chat_summarize", self.chat_summarize_node)
        workflow.add_node("chat_agent", self.chat_agent)
        workflow.add_node("tools", self.chat_tool_node)

        workflow.add_edge(START, "chat_summarize")
        workflow.add_edge("chat_summarize", "chat_agent")
        workflow.add_edge("tools", "chat_summarize")
        workflow.add_conditional_edges("chat_agent", tools_condition)

        return workflow
