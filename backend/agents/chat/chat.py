import logging
from datetime import datetime

from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import tools_condition

from agents.common.logging_utils import llm_response_to_log
from agents.common.toolnode import make_tool_node
from agents.models import OpenAIModel
from agents.pricecomparison import price_lookup_tools

logger = logging.getLogger(__name__)


class ChatState(MessagesState):
    input: HumanMessage = None
    pass


class ChatFlow:
    llm_model: None

    def __init__(self, llm_model=None):
        llm_model = llm_model or OpenAIModel(use_cache=False).get_model()
        # allow the model to do price lookups
        self.llm_model = llm_model.bind_tools(self.get_tools())

    def get_tools(self) -> list:
        return price_lookup_tools.get_tools()

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

    def chat_agent(self, state: ChatState) -> dict:
        logger.debug(f"run invoked with state: {llm_response_to_log(state)}")

        # store the latest human input
        messages = state["messages"].copy()
        messages.append(state["input"])

        prompt = self.get_primary_assistant_prompt().invoke({"messages": messages, "input": state["input"]})
        result = self.llm_model.invoke(prompt)

        logger.debug(f"Result returned: {llm_response_to_log(result)}")

        # store the response and return the modified state object
        messages.append(result)
        return {"messages": messages}

    def as_subgraph(self):
        """
        Returns the workflow (StateGraph) before compilation, so it can be used as a subgraph in other graphs.
        """
        # needs to be StateGraph so that the chatbot remembers previous interactions
        workflow = StateGraph(state_schema=ChatState)
        workflow.add_node("chat_agent", self.chat_agent)
        workflow.add_node("tools", make_tool_node(messages_key="messages", tools=self.get_tools()))

        workflow.add_edge(START, "chat_agent")
        workflow.add_edge("tools", "chat_agent")
        workflow.add_conditional_edges("chat_agent", tools_condition)

        return workflow
