General things to keep in mind:

- Always update requirements.txt if new libraries are added through a change. Please remind the user to run pip to install the new libraries.

LangChain and LangGraph things to keep in mind:

- When using ChatPromptTemplate, use its invoke method to resolve the template and provide the dict object with the necessary values. Do not use to_messages(), to_string() or anything like that.
