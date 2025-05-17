import base64
import logging
from pprint import pformat

# from copilotkit.langchain import copilotkit_customize_config
from copilotkit.langgraph import copilotkit_emit_message
from langchain.chains import TransformChain
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig, chain
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from agents.common import make_tool_node
from agents.models import OpenAIModel
from agents.receiptanalyzer.receiptanalyzerprompt import ReceiptAnalyzerPrompt
from agents.receiptanalyzer.receiptstate import Receipt, ReceiptState
from common.server.utils import get_uploads_folder

logger = logging.getLogger(__name__)

"""
Usage example:

```python
from agents.receiptanalyzer.receiptanalysis import ReceiptAnalysisFlow
from langgraph.types import Command
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
load_dotenv()
f = ReceiptAnalysisFlow()
g = f.as_subgraph().compile(checkpointer=MemorySaver())
config = {"configurable": { "thread_id": 1 }}

# this should cause an interrupt
g.invoke({"messages": "foo"}, config=config)
g.invoke(Command(resume="kk.jpg"), config=config)
```

"""


@tool
def receipt_analyzer_tool(image_path: str) -> Receipt:
    """
    Analyze a receipt image and return the extracted information.

    Input parameters:
    - image_path (str): The path to the receipt image.

    Returns:
    - Receipt: An object containing the extracted information from the receipt in JSON format.
    """
    logger.info(f"receipt_analyzer_tool called: {image_path}")

    chain = setup_chain()
    response = chain.invoke({"receipt_image_path": image_path})
    logger.debug("response = " + pformat(response, indent=2))

    return response


def setup_chain():
    extraction_model = OpenAIModel().get_model()
    prompt = ReceiptAnalyzerPrompt()
    parser = JsonOutputParser(pydantic_object=Receipt)

    load_image_chain = TransformChain(
        input_variables=["receipt_image_path"],
        output_variables=["image"],
        transform=load_image,
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


def load_image(path: dict) -> dict:
    def encode_image(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    image_base64 = encode_image(path["receipt_image_path"].strip())
    return {"image": image_base64}


class ReceiptAnalysisFlow:
    model: None

    def __init__(self):
        model = OpenAIModel(openai_model="o4-mini").get_model()

        # bind the tools to the model
        # model_with_tools = model.bind_tools(self.get_tools(), tool_choice="receipt_analyzer_tool")
        model_with_tools = model.bind_tools(self.get_tools())
        self.model = model_with_tools

    def get_tools(self):
        return [receipt_analyzer_tool]

    def receipt_analysis_start(self, state: ReceiptState, config: RunnableConfig) -> dict:
        state["receipt_image_path"] = interrupt("Please provide an image with the receipt.")

        if state["receipt_image_path"] == "__CANCEL__":
            # emit a message to the UI to indicate that the receipt is being processed,
            # and terminate the process
            copilotkit_emit_message(config, "Receipt processing cancelled")
            return Command(goto=END)

        full_image_path = get_uploads_folder() / state["receipt_image_path"]
        state["receipt_image_path"] = str(full_image_path)

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a grocery receipt analyzer. Your only task is to analyze the receipt image
                    by using the receipt_analyzer_tool tool and return the extracted information in JSON format.

                    Do not provide any additional information or context, only the JSON output from the tool.
                    """
                ),
                ("human", "Receipt image path:{receipt_image_path}"),
            ]
        )

        prompt = prompt_template.invoke({"receipt_image_path": state["receipt_image_path"]})
        response = self.model.invoke(prompt)
        logger.debug("response = " + pformat(response, indent=2))

        return {"messages": response, "receipt": response}

    def as_subgraph(self):
        workflow = StateGraph(state_schema=ReceiptState)

        # nodes
        workflow.add_node("receipt_analysis_start", self.receipt_analysis_start)
        workflow.add_node("tools", make_tool_node(messages_key="messages", tools=self.get_tools()))

        # edges
        workflow.add_edge(START, "receipt_analysis_start")
        workflow.add_edge("receipt_analysis_start", "tools")
        workflow.add_edge("tools", END)

        # workflow.add_edge("tools", "receipt_analysis_start")
        # workflow.add_conditional_edges("receipt_analysis_start", tools_condition)
        # workflow.add_edge("tools", END)

        return workflow
