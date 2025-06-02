"""
This script demonstrates how to use the RecipeFlow agent to extract recipes from a given URL.
"""

import asyncio

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

from agents.shoppinglist.shoppinglistflow import ShoppingListFlow

load_dotenv(verbose=True)
graph = ShoppingListFlow().as_subgraph().compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": 1}}

# Inputs to simulate
inputs = [
    {"messages": "I'd like to plan a shopping list for the week, can you help? Make sure the recipes are for 5 people."},
    {"messages": "Let's start with Monday. I want to have pasta for dinner. No need to plan lunch."},
    {
        "messages": "This is good, can you please save it to the meal plan? Let's move on to Tuesday next. I would like to have beef stroganoff for dinner."
    },
    {"messages": "Yes, that's good, please add it."},
    {"messages": "Can you also add the following items to the shopping list: toilet paper, milk and eggs?"},
]


async def main():
    for input in inputs:
        async for event in graph.astream(input, config, stream_mode="values"):
            if "messages" in event:
                event["messages"][-1].pretty_print()


if __name__ == "__main__":
    asyncio.run(main())
