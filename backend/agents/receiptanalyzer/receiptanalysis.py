import base64
import logging
from datetime import UTC, datetime
from pprint import pformat

from copilotkit.langgraph import copilotkit_customize_config, copilotkit_emit_message
from langchain.chains import TransformChain
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig, chain
from langgraph.graph import START, StateGraph
from langgraph.types import Command, interrupt
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

# from agents.common import make_tool_node
from agents.models import OpenAIModel
from agents.receiptanalyzer.receiptanalyzerprompt import ReceiptAnalyzerPrompt
from agents.receiptanalyzer.receiptstate import Receipt, ReceiptState
from common.repository_factory import get_receipt_repository
from common.server.utils import get_uploads_folder

logger = logging.getLogger(__name__)


@tool
def receipt_analyzer_tool(image_path: str) -> Receipt:
    """
    Analyze a receipt file (image or PDF) and return the extracted information.

    Input parameters:
    - image_path (str): The path to the receipt file (image or PDF).

    Returns:
    - Receipt: An object containing the extracted information from the receipt in JSON format.
    """
    logger.info(f"receipt_analyzer_tool called: {image_path}")

    # Detect file type and use appropriate chain
    if is_pdf_file(image_path):
        logger.info(f"Processing PDF file: {image_path}")
        chain = setup_pdf_chain()
    else:
        logger.info(f"Processing image file: {image_path}")
        chain = setup_chain()

    response = chain.invoke({"receipt_image_path": image_path})
    logger.debug("response = " + pformat(response, indent=2))

    import json

    return json.dumps(response)


@tool
def persist_receipt_tool(receipt: Receipt) -> dict:
    """
    Persist the receipt data to a database or file.

    Input parameters:
    - receipt (Receipt): The receipt data to be persisted.

    Returns:
    - dict: A dictionary containing the status of the persistence operation.
    """
    logger.info(f"persist_receipt_tool called: {receipt}")

    # Convert receipt data to JSON string and save it to the data store
    receipt_repo = get_receipt_repository()
    metadata = {"timestamp": datetime.now(UTC).isoformat()}
    success = receipt_repo.save_receipt(receipt.model_dump_json(), metadata)

    return {"success": success}


def setup_chain():
    """Setup processing chain for image files."""
    extraction_model = OpenAIModel(use_cache=True).get_model()
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


def setup_pdf_chain():
    """Setup processing chain for PDF files."""
    extraction_model = OpenAIModel(use_cache=True).get_model()
    prompt = ReceiptAnalyzerPrompt()
    parser = JsonOutputParser(pydantic_object=Receipt)

    extract_pdf_chain = TransformChain(
        input_variables=["receipt_image_path"],
        output_variables=["text"],
        transform=extract_pdf_text,
    )

    # build custom chain that processes text only (no image)
    @chain
    def pdf_model_chain(inputs: dict) -> dict:
        msg = extraction_model.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt.template},
                        {"type": "text", "text": parser.get_format_instructions()},
                        {"type": "text", "text": f"Receipt text content: \n{inputs['text']}"},
                    ]
                )
            ]
        )
        return msg.content

    return extract_pdf_chain | pdf_model_chain | parser


def load_image(path: dict) -> dict:
    def encode_image(path):
        with open(path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    image_base64 = encode_image(path["receipt_image_path"].strip())
    return {"image": image_base64}


def extract_pdf_text(path: dict) -> dict:
    """Extract text from PDF file with layout preservation."""
    pdf_path = path["receipt_image_path"].strip()

    # Configure layout analysis parameters for better text extraction
    laparams = LAParams(line_margin=0.1, char_margin=2.0, word_margin=0.1)
    text = extract_text(pdf_path, laparams=laparams)

    # debug the extracted text
    logger.debug(f"Extracted text from PDF {pdf_path}: \n{text}")

    return {"text": text}


def is_pdf_file(file_path: str) -> bool:
    """Check if the file is a PDF based on extension."""
    return file_path.lower().endswith(".pdf")


class ReceiptAnalysisFlow:
    model: None

    def __init__(self):
        pass

    def get_tools(self):
        return [receipt_analyzer_tool, persist_receipt_tool]

    async def receipt_analysis_start(self, state: ReceiptState, config: RunnableConfig) -> dict:
        # this node is only here to handle the interrupt
        if state["receipt_image_path"] is None or state["receipt_image_path"].strip() == "":
            state["receipt_image_path"] = interrupt("Please provide an image with the receipt.")

        if state["receipt_image_path"].strip() == "__CANCEL__":
            # emit a message to the UI to indicate that the receipt is being processed,
            # and terminate the process
            state["messages"].append(AIMessage(content="Receipt processing cancelled"))
            await copilotkit_emit_message(config, "Receipt processing cancelled")
            return Command(goto="__end__", update={})

        return Command(goto="receipt_analysis", update=state)

    async def receipt_analysis(self, state: ReceiptState, config: RunnableConfig) -> dict:
        full_image_path = get_uploads_folder() / state["receipt_image_path"]
        state["receipt_image_path"] = str(full_image_path)

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are a grocery receipt analyzer. Your only task is to analyze the receipt image and save the data to the database.

                    To extract information from the receipt, use tool receipt_analyzer_tool tool and return the extracted information in JSON format.

                    If there is already a receipt in the messages, please use tool persist_receipt_tool to save the data to the database before
                    returning a summary of the receipt.

                    When the tool call to persist data to the database is complete, do not return the results of the tool calls in the response, but instead do a quick analysis
                    of the receipt including:
                    - the total amount of the receipt
                    - the number of items in the receipt
                    - the date of the receipt
                    - the store name
                    """
                ),
                (
                    "human",
                    "When calling the receipt_analyzer_tool tool, please provide the following value for the image path: {receipt_image_path}",
                ),
                ("placeholder", "{messages}"),
            ]
        )

        model = OpenAIModel(openai_model="gpt-4o", use_cache=True).get_model().bind_tools(self.get_tools())
        no_messages_config = copilotkit_customize_config(
            config, emit_intermediate_state=False, emit_messages=False, emit_tool_calls=True
        )
        prompt = prompt_template.invoke({"receipt_image_path": state["receipt_image_path"], "messages": state["messages"]})
        response = await model.ainvoke(prompt, config=no_messages_config)

        if response.tool_calls:
            # Emit a status message before processing tools
            await copilotkit_emit_message(config, "🔄 Analyzing receipt and extracting data...")
            return Command(goto="tool_node", update={"messages": response})

        # reset a key part of the state
        state["image_file_path"] = None

        return Command(goto="__end__", update={"messages": response})

    async def tool_node(self, state: ReceiptState, config: RunnableConfig) -> dict:
        # TODO: eventually we should use the tool node from langgraph
        tools_by_name = {tool.name: tool for tool in self.get_tools()}

        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]

            # Emit specific status messages based on the tool being called
            if tool_call["name"] == "receipt_analyzer_tool":
                await copilotkit_emit_message(config, "📊 Classifying receipt data...")
            elif tool_call["name"] == "persist_receipt_tool":
                await copilotkit_emit_message(config, "💾 Saving receipt to database...")

            tool_msg = tool.invoke(tool_call["args"])
            logger.debug(f"Tool call {tool_call['name']}, result: {tool_msg}")
            state["messages"].append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))

        return state

    def as_subgraph(self):
        workflow = StateGraph(state_schema=ReceiptState)

        # nodes
        workflow.add_node("receipt_analysis_start", self.receipt_analysis_start)
        workflow.add_node("receipt_analysis", self.receipt_analysis)
        workflow.add_node("tool_node", self.tool_node)

        # build the graph; end node as well as the next node from receipt_analysis_start is
        # defined within the logic of each node
        workflow.add_edge(START, "receipt_analysis_start")
        workflow.add_edge("tool_node", "receipt_analysis")

        return workflow
