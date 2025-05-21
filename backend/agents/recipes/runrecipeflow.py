"""
This script demonstrates how to use the RecipeFlow agent to extract recipes from a given URL.
"""

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from agents.recipes.recipeflow import RecipeFlow

load_dotenv(verbose=True)
graph = RecipeFlow().as_subgraph().compile(checkpointer=MemorySaver())
config = {"configurable": {"thread_id": 1}}

# Inputs to simulate
inputs = [
    # first test site
    {"messages": ""},
    Command(resume="https://breaddad.com/easy-banana-bread-recipe/"),
    # second test site
    {"messages": ""},
    Command(
        resume="https://www.bettycrocker.com/recipes/traditional-beef-stroganoff-recipe/c17a904f-a8f6-48ae-bedb-5b301a8ea317"
    ),
    # third test site
    {"messages": ""},
    Command(resume="https://www.bbcgoodfood.com/recipes/easy-vegetable-lasagne"),
]

for input in inputs:
    events = graph.stream(input, config, stream_mode="values")
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()


def print_recipe(recipe):
    if recipe is not None:
        print(f"Name: {recipe['name']}")
        # loop through ingredients list
        print("Ingredients:")
        for ingredient in recipe["ingredients"]:
            print(f"- {ingredient}")
        # loop through steps
        print("Steps:")
        for step in recipe["steps"]:
            print(f"- {step}")
    else:
        print("No recipe was provided.")
