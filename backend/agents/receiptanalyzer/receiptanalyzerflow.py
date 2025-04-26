import logging

from langgraph.graph import END, START, StateGraph

from agents.receiptanalyzer.itemclassifier import ItemClassifier
from agents.receiptanalyzer.persistdata import PersistData
from agents.receiptanalyzer.receiptanalyzer import ReceiptAnalyzer
from agents.receiptanalyzer.receiptstate import ReceiptState
from common.datastore import get_data_store

"""
This is the top-level agent that defines the graph and manages the flow of events
and data between nodes.
"""

logger = logging.getLogger(__name__)


class ReceiptAnalyzerFlow:
    def __init__(self):
        self.receipt_analyzer_agent = ReceiptAnalyzer()
        self.item_classifier_agent = ItemClassifier()
        self.data_store = get_data_store()
        self.persist_data_agent = PersistData(self.data_store)

    def analyze_receipt(self, state: ReceiptState) -> ReceiptState:
        return self.receipt_analyzer_agent.run(state)

    def classify_items(self, state: ReceiptState) -> ReceiptState:
        return self.item_classifier_agent.run(state)

    def persist_data(self, state: ReceiptState) -> ReceiptState:
        return self.persist_data_agent.run(state)

    def as_subgraph(self):
        workflow = StateGraph(state_schema=ReceiptState)
        workflow.add_node("analyze_receipt", self.analyze_receipt)
        workflow.add_node("classify_items", self.classify_items)
        workflow.add_node("persist_data", self.persist_data)
        workflow.add_edge(START, "analyze_receipt")
        workflow.add_edge("analyze_receipt", "classify_items")
        workflow.add_edge("classify_items", "persist_data")
        workflow.add_edge("persist_data", END)
        return workflow

    # Optionally keep the run method for direct use
    def run(self, receipt_image_path: str):
        graph = self.as_subgraph().compile()
        receipt_state = ReceiptState(receipt_image_path=receipt_image_path)
        response = graph.invoke(receipt_state)
        return response
