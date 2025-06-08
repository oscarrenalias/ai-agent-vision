import logging

from copilotkit.langgraph import copilotkit_customize_config
from langchain.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage
from langchain_core.runnables import RunnableConfig

from agents.models import OpenAIModel

"""
This is a factory method for generating classifier nodes based on a simple dictionary:

```python
from agents.common.classifiernode import make_classifier
from langchain_core.messages import HumanMessage, SystemMessage
classifier_edge = make_classifier(routing_map = {
    "upload": "If the message is a request to upload, scan or process a receipt file. Example: I want to upload my receipt.",
    "planner": "If the message is about meal planning. Example: I want to plan my meals for the week.",
    "chat": "Anything else. Example: I want to chat with you",
}, default_node = "chat")

classifier_edge({"messages": [HumanMessage(content="I want to upload my receipt")]}) # produces "upload"
classifier_edge({"messages": [HumanMessage(content="What's the weather like today")]}) # produces "chat"
classifier_edge({"messages": [HumanMessage(content="I don't know what to eat next week")]}) # produces "planner"
classifier_edge({"messages": [HumanMessage(content="whatever")]}) # produces "chat"
```


"""


def get_prompt_template(routing_map: dict, default_node: str):
    # build a list with the keys as a string in double quotes, separated by commas
    keys_str = ", ".join([f'"{key}"' for key in routing_map.keys()])

    # build the longer list of options, with each criteria and example
    options_str = "\n".join([f"- {key}: {value}" for key, value in routing_map.items()])

    # build the system prompt
    # flake8: noqa: E231
    system_prompt = f"""
            Classify the following user message as one of: {keys_str} based on the following criteria:

            {options_str}

            Reply with only one of these words. Do not include anything else in your response.

            If none of the options apply, reply with "{default_node}".
            """

    # create the prompt template
    prompt = ChatPromptTemplate.from_messages([SystemMessage(content=(system_prompt)), ("human", "{input}")])

    return prompt


def _classify_message(state: dict, config: RunnableConfig, routing_map: dict, default_node: str):
    logger = logging.getLogger(__name__)

    # GPT-4.1-nano model is fast and cost-effective for this task
    llm_model = OpenAIModel(use_cache=False, openai_model="gpt-4.1-mini").get_model()

    # configure copilotkit so that it doesn't emit intermediate messages
    internal_config = copilotkit_customize_config(
        config,
        emit_messages=False,
    )

    # return default node if no messages are present (should rarely happen)
    if len(state["messages"]) == 0:
        logger.warning("No messages found in state. Returning default node.")
        return default_node

    # Get the last message which should contain the user input
    last_message = state["messages"][-1]
    logger.info(f"Classifying message: {last_message.content}")

    # Get the user input from the last message
    user_input = last_message.content
    # Generate the classification using the LLM
    prompt_str = get_prompt_template(routing_map=routing_map, default_node=default_node).invoke({"input": user_input})
    logger.info(f"Prompt string: {prompt_str}")

    classification = llm_model.invoke(prompt_str, config=internal_config).content.strip()
    # Check if the classification is in the routing map
    if classification in routing_map:
        # If it is, return the corresponding node
        return classification
    else:
        # If not, return the default node
        return default_node


def make_classifier(routing_map: dict, default_node: str):
    def classifier(state: dict, config: RunnableConfig):
        return _classify_message(state=state, config=config, routing_map=routing_map, default_node=default_node)

    return classifier
