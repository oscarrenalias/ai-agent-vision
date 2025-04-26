# Overview

The vision is that this application no longer has a user interface, but that it is fully based on an agentic
approach where functionality is triggered via chat.

## Agent flow

```mermaid
graph TD
    Start([User input]) --> QuestionClassifier{What do you want to do?}
    QuestionClassifier -- Upload receipt --> ProcessReceipt[Upload new receipt]
    QuestionClassifier -- General questons --> Chat[Chat]
    QuestionClassifier -- "Meal planning" --> MealPlanner[Plan meals for the week]
    Chat -- General questions --> Chat[Chat]

    ProcessReceipt --> ProcessReceipt_ExtractItems[Extract items from receipt, including amounts, price, loyalty discounts, and other]
    ProcessReceipt_ExtractItems --> ProcessReceipt_ClassifyItems[Classify items in the receipt according to taxonomy]
    ProcessReceipt_ClassifyItems --> ProcessReceipt_Store[Store receipt in the database for querying later]
    ProcessReceipt_Store --> Start

    MealPlanner --> MealPlanner_Preferences[What do you fancy this week?]
    MealPlanner_Preferences --> MealPlanner_SearchRecipes[Find suitable recipes]
    MealPlanner_SearchRecipes --> MealPlanner_BuildMenu[Build a menu for the week]
    MealPlanner_BuildMenu --> MealPlanner_GenerateShoppingList[Generate shopping list according to menu]
    MealPlanner_GenerateShoppingList --> Start
```
