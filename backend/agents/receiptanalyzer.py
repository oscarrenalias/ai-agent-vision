import base64
import logging

from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import chain

from .models import Model
from .receiptanalyzerprompt import ReceiptAnalyzerPrompt
from .receiptstate import Receipt, ReceiptState

logger = logging.getLogger(__name__)


class ReceiptAnalyzer:
    """
    Analyzes purchases receipts
    """

    # Keeps track of the LLM model
    model: None

    # path to the file containing the receipt, if used
    receipt_file_path: None

    def __init__(self):
        logger.info("ReceiptAnalyzer initialized")
        self.create_llm()

    def create_llm(self):
        """
        Get the LLM model
        """
        self.model = Model("openai").get_model()

    def run(self, state: ReceiptState) -> ReceiptState:
        """
        Analyze the receipt
        """
        logger.info("ReceiptAnalyzer run")

        chain = self.set_up_chain()
        logger.info("state = " + str(state))

        input_data = {"receipt_file_path": state["receipt_image_path"]}
        response = chain.invoke(input_data)
        logger.info("response = " + str(response))

        # update the state with the receipt and return
        state["receipt"] = response
        return state

    def set_up_chain(self):
        extraction_model = self.model
        prompt = ReceiptAnalyzerPrompt()
        parser = JsonOutputParser(pydantic_object=Receipt)

        load_image_chain = TransformChain(
            input_variables=["receipt_file_path"],
            output_variables=["image"],
            transform=self.load_image,
        )

        # build custom chain that includes an image
        @chain
        def receipt_model_chain(inputs: dict) -> dict:
            """Invoke model"""
            msg = extraction_model.invoke(
                [
                    HumanMessage(
                        content=[
                            {"type": "text", "text": prompt.template},
                            {"type": "text", "text": parser.get_format_instructions()},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{inputs['image']}"},  # noqa: E231, E702
                            },
                        ]
                    )
                ]
            )
            return msg.content

        return load_image_chain | receipt_model_chain | parser

    @staticmethod
    def load_image(path: dict) -> dict:
        """Load image and encode it as base64."""

        def encode_image(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        image_base64 = encode_image(path["receipt_file_path"])
        return {"image": image_base64}
