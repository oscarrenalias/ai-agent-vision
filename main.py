from langgraph.graph import Graph
from agents import ItemClassifier, PersistData, ReceiptState, ReceiptAnalyzer
from langgraph.graph import StateGraph, START, END
import logging

class MainAgent:
    def __init__(self):
        # configure logging for everyone
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(funcName)s] %(message)s"
        )

    def run(self):
        # Initialize agents
        receipt_analyzer_agent = ReceiptAnalyzer()
        item_classifier_agent = ItemClassifier()
        persist_data_agent = PersistData()

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
        receipt_state = ReceiptState()
        graph.invoke(receipt_state)

#
# Run the main agent
#
main_agent = MainAgent()
main_agent.run()