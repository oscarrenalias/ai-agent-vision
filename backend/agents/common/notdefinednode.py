import logging


def not_defined_node(state: dict):
    """
    A placeholder node that does nothing. This is used to indicate that a node is not defined or not implemented.
    """
    logging.getLogger(__name__).info(f"NotDefinedNode run invoked with state: {state}")

    return state
