import base64
import logging
from datetime import UTC, datetime
from pprint import pformat

# from copilotkit.langchain import copilotkit_customize_config
# from copilotkit.langgraph import copilotkit_customize_config, copilotkit_emit_message
from copilotkit.langgraph import copilotkit_emit_message
from langchain.chains import TransformChain
from langchain.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig, chain
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

# from agents.common import make_tool_node
from agents.models import OpenAIModel
from agents.receiptanalyzer.receiptanalyzerprompt import ReceiptAnalyzerPrompt
from agents.receiptanalyzer.receiptstate import Receipt, ReceiptState
from common.datastore import get_data_store
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
    data_store = get_data_store()
    metadata = {"timestamp": datetime.now(UTC).isoformat()}
    success = data_store.save_receipt(receipt.model_dump_json(), metadata)

    return {"success": success}


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
        pass

    def get_tools(self):
        return [receipt_analyzer_tool, persist_receipt_tool]

    def receipt_analysis(self, state: ReceiptState, config: RunnableConfig) -> dict:
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
                    """
                ),
                (
                    "human",
                    "When calling the receipt_analyzer_tool tool, please provide the following value for the image path: {receipt_image_path}",
                ),
            ]
        )

        # modifiedConfig = copilotkit_customize_config(
        #    config,
        #    emit_messages=False,
        # )

        tools = [receipt_analyzer_tool]
        model = OpenAIModel(openai_model="gpt-4o").get_model().bind_tools(tools, tool_choice="receipt_analyzer_tool")

        prompt = prompt_template.invoke({"receipt_image_path": state["receipt_image_path"]})
        response = model.invoke(prompt)

        # response should have tool_calls
        if hasattr(response, "tool_calls") and len(response.tool_calls) == 1:
            # and it should be the receipt_analyzer_tool
            if response.tool_calls[0]["name"] != "receipt_analyzer_tool":
                error_msg = f"Tool call is not receipt_analyzer_tool: {response.tool_calls[0]}"
                raise ValueError(error_msg)

            messages = []
            tool_call = response.tool_calls[0]
            tool = tools[0]
            tool_msg = tool.invoke(tool_call["args"])
            logger.debug(f"Tool call {tool_call['name']}, result: {tool_msg}")
            messages.append(
                ToolMessage(content="Receipt analyzed successfully", artifact=tool_msg, tool_call_id=tool_call["id"])
            )
        else:
            raise ValueError(f"Response from receipt_analysis node did not have tool_calls: {response}")

        return {"messages": messages, "receipt": tool_msg}

    def persist_receipt(self, state: ReceiptState, config: RunnableConfig) -> dict:
        logger.debug("persisting_receipt")

        if "receipt" not in state:
            logger.warning("No receipt data found in state")
            return state

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content="""
                    You are using a tool to persist a JSON structure with a grocecies receipt to a database. This is your only task.
                    by using the use the persist_receipt_tool to save data to the database.
                    """
                ),
                ("human", "{receipt}"),
            ]
        )

        tools = [persist_receipt_tool]
        prompt = prompt_template.invoke({"receipt": state["receipt"]})
        model = OpenAIModel(openai_model="gpt-4o").get_model().bind_tools(tools, tool_choice="persist_receipt_tool")
        response = model.invoke(prompt)

        # response should have tool_calls, and only one tool call
        if hasattr(response, "tool_calls") and len(response.tool_calls) == 1:
            # and it should be the persist_receipt_tool
            if response.tool_calls[0]["name"] != "persist_receipt_tool":
                error_msg = f"Tool call is not persist_receipt_tool: {response.tool_calls[0]}"
                raise ValueError(error_msg)

            messages = []
            tool_call = response.tool_calls[0]
            tool = tools[0]
            tool_msg = tool.invoke(tool_call["args"])
            logger.debug(f"Tool call {tool_call['name']}, result: {tool_msg}")
            messages.append(ToolMessage(content=tool_msg, tool_call_id=tool_call["id"]))
            messages.append(AIMessage(content="Receipt persisted successfully"))

        else:
            raise ValueError(f"Error processing tool calls in persist_receipt: {response}")

        return {"messages": messages}

    def as_subgraph(self):
        workflow = StateGraph(state_schema=ReceiptState)

        # nodes
        workflow.add_node("receipt_analysis", self.receipt_analysis)
        workflow.add_node("persist_receipt", self.persist_receipt)

        workflow.add_edge(START, "receipt_analysis")
        workflow.add_edge("receipt_analysis", "persist_receipt")
        workflow.add_edge("persist_receipt", END)

        return workflow
