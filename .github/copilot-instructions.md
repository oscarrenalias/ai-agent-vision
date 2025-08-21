# Overview

## Backend
- This is a Python project that uses uv for dependency management. Please use ```uv add``` or ```uv pip install``` to add dependencies. Do NOT create or maintain a requirements.txt
- Key Python libraries in use are LangChain and LangGraph

## UI
- The UI is a web app build using Next.js and TypeScript

# LangChain & LangGraph

Keep the following in mind:

- When using ChatPromptTemplate, use its invoke method to resolve the template and provide the dict object with the necessary values. Do not use to_messages(), to_string() or anything like that.

# Coding Guidelines

Always conform to the coding guidelines defined here:

## Functions
- Ensure functions are small and perform a single task.
- Avoid flag arguments and side effects.
- Each function should operate at a single level of abstraction.

## Single Responsibility Principle
- Each class or function should have only one reason to change.
- Separate concerns and encapsulate responsibilities appropriately.
- Clean Formatting

## Formatting
- Use consistent indentation and spacing.
- Separate code blocks with new lines where needed for readability.

## Avoid Duplication
- Extract common logic into functions or classes.
- DRY – Don’t Repeat Yourself.
- Code Smells to Flag

## Code smells
Be on the lookout for the following, and avoid the following if possible:
- Long functions
- Large classes
- Deep nesting
- Long parameter lists
- Magic numbers or strings
- Inconsistent naming

# Other 

- If you create code to quickly test a feature, do not leave these files in the repository when the feature has been implemented. Either delete them, or convert them to a test case (python or ui)
