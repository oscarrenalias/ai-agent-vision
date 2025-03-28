import logging
from langgraph.graph import Graph
from agents import ItemClassifier, PersistData, ReceiptState, ReceiptAnalyzer
from langgraph.graph import StateGraph, START, END
from common.datastore import get_data_store

"""
This is the top-level agent that defines the graph and manages the flow of events
and data between nodes.
"""
class Orchestrator:
    def __init__(self):
        # configure logging for everyone
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
        )

    def run(self, receipt_image_path: str):
        
        # Initialize nodes
        receipt_analyzer_agent = ReceiptAnalyzer()
        item_classifier_agent = ItemClassifier()

        
        data_store = get_data_store()
        persist_data_agent = PersistData(data_store)

        # Define a Langchain graph
        workflow = Graph()

        # Add nodes for each agent
        workflow.add_node("analyze_receipt", receipt_analyzer_agent.run)
        workflow.add_node("classify_items", item_classifier_agent.run)
        workflow.add_node("persist_data", persist_data_agent.run)

        # Set up edges
        workflow.add_edge(START, "analyze_receipt")
        workflow.add_edge('analyze_receipt', 'classify_items')
        workflow.add_edge('classify_items', 'persist_data')
        workflow.add_edge('persist_data', END)

        # compile the graph
        graph = workflow.compile()

        # Initialize the state
        receipt_state = ReceiptState(
            receipt_image_path=receipt_image_path,
        )
        response = graph.invoke(receipt_state)

        return(response)