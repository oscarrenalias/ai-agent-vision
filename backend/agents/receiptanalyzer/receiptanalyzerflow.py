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

Usage:

```python
from agents.receiptanalyzer.receiptanalyzerflow import ReceiptAnalyzerFlow
flow = ReceiptAnalyzerFlow()
state = flow.run(receipt_image_path="../data/samples/receipt_sample_1_small.jpg")
```
"""

logger = logging.getLogger(__name__)


class ReceiptAnalyzerFlow:
    def __init__(self):
        pass

    def as_subgraph(self):
        workflow = StateGraph(state_schema=ReceiptState)
        workflow.add_node("analyze_receipt", ReceiptAnalyzer().run)
        workflow.add_node("classify_items", ItemClassifier().run)
        workflow.add_node("persist_data", PersistData(get_data_store()).run)

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
