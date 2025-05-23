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
    # first test site -- url provided, no body
    {"messages": "", "recipe": None, "recipe_content": None},
    Command(resume="https://breaddad.com/easy-banana-bread-recipe/"),
    # second test site -- same as first
    {"messages": "", "recipe": None, "recipe_content": None},
    Command(
        resume="https://www.bettycrocker.com/recipes/traditional-beef-stroganoff-recipe/c17a904f-a8f6-48ae-bedb-5b301a8ea317"
    ),
    # third case -- we provide a receipt in the body
    {
        "recipe": None,
        "recipe_content": None,
        "messages": """
Ingredients
1/2 cup melted unsalted butter or vegetable oil, plus more for greasing pan
1 3/4 cups flour
1 cup toasted pecans, chopped
1/2 cup granulated sugar
1 teaspoon baking soda
1 teaspoon ground cinnamon
Fine salt
1/4 teaspoon freshly grated nutmeg
2 large eggs, lightly beaten
1/4 cup buttermilk, sour cream or yogurt
1/2 cup light brown sugar, lightly packed
1 teaspoon pure vanilla extract
4 soft, very ripe, darkly speckled medium bananas, mashed (about 1 1/2 cups)

Method

Got one or two overripe bananas? Throw them into a resealable plastic bag and freeze them. (They'll keep up to a month.) When you have enough, use them to make this easy banana bread. Just bring them to room temperature, then peel and mash. The bread is even better the next day.

Preheat the oven to 175°C. Lightly butter one 9-by-5-inch loaf pan.

Whisk together the flour, pecans, granulated sugar, baking soda, cinnamon, 1/2 teaspoon salt and nutmeg in a large bowl. Whisk together the eggs, melted butter, buttermilk, brown sugar and vanilla in a medium bowl; stir in the mashed bananas. Fold the banana mixture into the flour mixture until just combined (it's OK if there are some lumps).

Pour the batter into the buttered pan and lightly tap the pan on the counter to evenly distribute the batter. Bake until browned and a toothpick inserted into the center comes out completely clean, about 1 hour. Let the bread cool for 10 minutes in the pan, then turn out onto a rack to cool completely.

Copyright 2013 Television Food Network, G. P. All rights reserved.
""",
    },
]

# Inputs to simulate
inputs_recipe_body = [
    {
        "messages": """
Ingredients
1/2 cup melted unsalted butter or vegetable oil, plus more for greasing pan
1 3/4 cups flour
1 cup toasted pecans, chopped
1/2 cup granulated sugar
1 teaspoon baking soda
1 teaspoon ground cinnamon
Fine salt
1/4 teaspoon freshly grated nutmeg
2 large eggs, lightly beaten
1/4 cup buttermilk, sour cream or yogurt
1/2 cup light brown sugar, lightly packed
1 teaspoon pure vanilla extract
4 soft, very ripe, darkly speckled medium bananas, mashed (about 1 1/2 cups)

Method

Got one or two overripe bananas? Throw them into a resealable plastic bag and freeze them. (They'll keep up to a month.) When you have enough, use them to make this easy banana bread. Just bring them to room temperature, then peel and mash. The bread is even better the next day.

Preheat the oven to 175°C. Lightly butter one 9-by-5-inch loaf pan.

Whisk together the flour, pecans, granulated sugar, baking soda, cinnamon, 1/2 teaspoon salt and nutmeg in a large bowl. Whisk together the eggs, melted butter, buttermilk, brown sugar and vanilla in a medium bowl; stir in the mashed bananas. Fold the banana mixture into the flour mixture until just combined (it's OK if there are some lumps).

Pour the batter into the buttered pan and lightly tap the pan on the counter to evenly distribute the batter. Bake until browned and a toothpick inserted into the center comes out completely clean, about 1 hour. Let the bread cool for 10 minutes in the pan, then turn out onto a rack to cool completely.

Copyright 2013 Television Food Network, G. P. All rights reserved.
"""
    }
]


def print_recipe(recipe):
    print("========== RECIPE OBJECT ============")
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


for input in inputs:
    events = graph.stream(input, config, stream_mode="values")
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
            if event.get("recipe") is not None:
                if isinstance(event.get("recipe"), dict):
                    print_recipe(event.get("recipe"))
