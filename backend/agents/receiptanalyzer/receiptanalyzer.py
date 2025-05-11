import base64
import logging
from pprint import pformat

from copilotkit.langchain import copilotkit_customize_config
from copilotkit.langgraph import copilotkit_emit_message
from langchain.chains import TransformChain
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig, chain
from langgraph.graph import END
from langgraph.types import Command, interrupt

from agents.models import OpenAIModel
from common.server.utils import get_uploads_folder

from .receiptanalyzerprompt import ReceiptAnalyzerPrompt
from .receiptstate import Receipt, ReceiptState

logger = logging.getLogger(__name__)

"""
Usage example:

```python
from agents.receiptanalyzer.receiptanalyzer import ReceiptAnalyzer
from agents.receiptanalyzer.receiptstate import ReceiptState
analyzer=ReceiptAnalyzer()
state=ReceiptState.make_instance()
state["receipt_image_path"] = "../data/samples/receipt_sample_1_small.jpg"
analyzer.run(state)
```

"""


class ReceiptAnalyzer:
    model: None

    def __init__(self):
        self.model = OpenAIModel(openai_model="o4-mini").get_model()

    async def run(self, state: ReceiptState, config: RunnableConfig) -> Command:
        chain = self.set_up_chain()
        logger.debug("state = " + str(state))

        copilotkit_customize_config(config, emit_messages=False)

        state["receipt_image_path"] = interrupt("Please provide an image with the receipt.")

        if state["receipt_image_path"] == "__CANCEL__":
            # emit a message to the UI to indicate that the receipt is being processed,
            # and terminate the process
            await copilotkit_emit_message(config, "Receipt processing cancelled")
            return Command(goto=END)

        # emit a message to the UI to indicate that the receipt is being processed
        await copilotkit_emit_message(config, "Receipt is being processed...")

        full_image_path = get_uploads_folder() / state["receipt_image_path"]
        state["receipt_image_path"] = str(full_image_path)

        response = await chain.ainvoke({"receipt_image_path": state["receipt_image_path"]})
        logger.debug("response = " + pformat(response, indent=2))

        # return {"receipt": response}
        return Command(goto="classify_items", update={"receipt": response})

    def set_up_chain(self):
        extraction_model = self.model
        prompt = ReceiptAnalyzerPrompt()
        parser = JsonOutputParser(pydantic_object=Receipt)

        load_image_chain = TransformChain(
            input_variables=["receipt_image_path"],
            output_variables=["image"],
            transform=self.load_image,
        )

        # build custom chain that includes an image
        @chain
        def receipt_model_chain(inputs: dict) -> dict:
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

    def load_image(self, path: dict) -> dict:
        def encode_image(path):
            with open(path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode("utf-8")

        image_base64 = encode_image(path["receipt_image_path"])
        return {"image": image_base64}
