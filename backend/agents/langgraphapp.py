from agents.maingraph import MainGraph

"""
This file is used as the entry point for running the application in the LangGraph
platform or in the local LangGraph environement (LangGraph Studio).

First, deploy the langgraph CLI:

```
pip install -U langgraph[inmem]
```

Next, deploy the app:

```
langgrahp dev
```
"""

import logging

from common.logging import configure_logging

# set things up
configure_logging(logging.DEBUG)
logger = logging.getLogger(__name__)

main_graph = MainGraph().as_subgraph().compile()
