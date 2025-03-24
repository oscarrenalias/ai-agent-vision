from .receiptstate import ReceiptState
from .models import Model
import logging
#from langchain_huggingface import (ChatHuggingFace, HuggingFaceEndpoint)
from huggingface_hub import login
import os
import base64
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from langchain.chains import TransformChain
from langchain_core.runnables import chain

class ReceiptAnalyzer:
    """
        Analyzes purchases receipts
    """

    # Keeps track of the LLM model
    model: None

    # path to the file containing the receipt, if used
    receipt_file_path: None

    system_prompt = """
        You are analyzing a Finnish grocery receipt. Your task is to extract structured information in JSON format. Please follow the rules carefully.
        
        Do not guess. If some information is missing just return "N/A" in the relevant field. If you determine that the image is not of a receipt, just set all the fields in the formatting instructions to "N/A". 
       
        You must obey the output format under all circumstances. Please follow the formatting instructions exactly.
        Do not return any additional comments or explanation. 

        1. List of Items
        For each line item (product), extract the following:
        - name_fi: Name of the item in Finnish
        - name_en: Translated name in English
        - unit_of_measure: Unit of measure (e.g., kg, unit, pkg, box, etc.). Include it as a string. If the unit is not specified, set to null.
        - quantity: Number of units, kilos, or packages (include unit type: e.g., kg, unit, pkg, box, etc.). Only include the number, do not include the unit type.
        - unit_price: Price per unit (e.g., €/kg or €/unit). Only include the number, do not include the currency or anything else.
        - total_price: Total price paid for this item before discount
        - loyalty_discount: If a discount is listed under the item (indicated by a line starting with PLUSSA-ETU), include the total discount for that item. Otherwise, set to null.
        - has_loyalty_discount: true or false depending on whether a loyalty discount was applied to this item
        Lines that start with PLUSSA-TASAERÄ can be ignored.

        2. Receipt Summary
        Extract the following:
        - total_before_discounts: Total value of the items before loyalty discounts
        - total_loyalty_savings: Total amount saved via loyalty card discounts (PLUSSAT-EDUT YHTEENSÄ)
        - total_paid: Total amount paid by the customer (including taxes)
    """

    def __init__(self):
        logging.info("ReceiptAnalyzer initialized")
        self.create_llm()

    def create_llm(self):
        """
            Get the LLM model
        """
        self.model = Model("openai").get_model()
        
    def set_receipt_from_file(self, receipt_file_path: str):
        """
            Set the receipt to be analyzed based on a local file
        """
        logging.info(f"Setting receipt from file {receipt_file_path}")
        self.receipt_file = receipt_file_path

    def run(self, state: ReceiptState) -> ReceiptState:
        """
            Analyze the receipt
        """        
        logging.info("ReceiptAnalyzer run")

        chain = self.set_up_chain()
        logging.info("state = " + str(state))
        input_data = {"receipt_file_path": state["receipt_image_path"]}
        response = chain.invoke(input_data)
        logging.info("response = " + str(response))
        state["messages"] = response
        return(state)

    def set_up_chain(self):
        extraction_model = self.model
        #prompt = VisionReceiptExtractionPrompt()
        prompt = self.system_prompt
        #parser = JsonOutputParser(pydantic_object=ReceiptInformation)

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
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{inputs['image']}"
                                },
                            },
                        ]
                    )
                ]
            )
            return msg.content

        return load_image_chain | receipt_model_chain
    
    @staticmethod
    def load_image(path: dict) -> dict:
        """Load image and encode it as base64."""

        def encode_image(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        image_base64 = encode_image(path["receipt_file_path"])
        return {"image": image_base64}