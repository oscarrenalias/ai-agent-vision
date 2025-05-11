import logging

from copilotkit.langchain import copilotkit_customize_config
from copilotkit.langgraph import copilotkit_emit_message
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig

from agents.models import OpenAIModel

from .itemclassifierprompt import ItemClassifierPrompt
from .receiptstate import Receipt, ReceiptState

logger = logging.getLogger(__name__)


class ItemClassifier:
    """
    Classifies items in the receipt according to their type
    """

    # Keeps track of the LLM model
    model: None

    def __init__(self):
        """
        Initialize the ItemClassifier
        """
        self.model = OpenAIModel(openai_model="o4-mini").get_model()

    async def run(self, state: ReceiptState, config: RunnableConfig) -> ReceiptState:
        logger.info("ItemClassifier run")

        copilotkit_customize_config(config, emit_messages=False)

        # call the LLM model to classify the items and map the response to the JSON object accordingly
        # Create prompt template with output format instructions
        parser = JsonOutputParser(pydantic_object=Receipt)
        prompt = PromptTemplate(
            template=ItemClassifierPrompt.template + "\n{format_instructions}\n{receipt}",
            input_variables=["receipt"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.model | parser
        await copilotkit_emit_message(config, "Classifying items in the receipt...")
        response = await chain.ainvoke({"receipt": state["receipt"]})
        logger.info("Response from classifier = " + str(response))

        # update the state with the new information
        state["receipt"] = response
        return state
