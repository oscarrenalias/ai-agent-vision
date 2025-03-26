from .receiptstate import ReceiptState
from .models import Model
import logging
from langchain_core.messages import HumanMessage
from .itemclassifierprompt import ItemClassifierPrompt

class ItemClassifier:
    """
        Classifies items in the receipt according to their type
    """

    # Keeps track of the LLM model
    model: None

    def __init__(self):
        logging.info("ItemClassifier initialized")
        self.model = Model("openai").get_model()

    def run(self, state: ReceiptState) -> ReceiptState:
        logging.info("ItemClassifier run")

        # TODO: I should probably use a prompt template here (https://python.langchain.com/docs/concepts/prompt_templates/)
        message = [HumanMessage(
            content = [
                {"type": "text", "text": ItemClassifierPrompt.template},
                {"type": "text", "text": str(state["receipt"]["items"])},
            ]
        )]

        response = self.model.invoke(message)
        logging.info("response = " + str(response.content))

        return(state)