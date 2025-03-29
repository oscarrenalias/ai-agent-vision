import logging

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from .itemclassifierprompt import ItemClassifierPrompt
from .models import Model
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
        logger.info("ItemClassifier initialized")
        self.model = Model("openai").get_model()

    def run(self, state: ReceiptState) -> ReceiptState:
        logger.info("ItemClassifier run")

        # call the LLM model to classify the items and map the response to the JSON object accordingly
        # Create prompt template with output format instructions
        parser = JsonOutputParser(pydantic_object=Receipt)
        prompt = PromptTemplate(
            template=ItemClassifierPrompt.template + "\n{format_instructions}\n{receipt}",
            input_variables=["receipt"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.model | parser
        response = chain.invoke({"receipt": state["receipt"]})
        logger.info("Response from classifier = " + str(response))

        # update the state with the new information
        state["receipt"] = response
        return state
