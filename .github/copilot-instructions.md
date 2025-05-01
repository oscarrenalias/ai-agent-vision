# Overview

This is a LangChain and LangGraph project. When asked about Python issues and topics, keep this in mind to provide answers in the context of these two libraries.

# General things to keep in mind

- Always make the necessary changes to requirements.txt if new Python libraries are added to the project through code that you generate. This file, requirements.txt, is the name of the file in this project that is run with pip to install the required libraries. Please also remind the user to run pip to install the new libraries.

# LangChain and LangGraph things to keep in mind

- When using prompt template classes such as ChatPromptTemplate, use its invoke method to resolve the template and provide the dict object with the necessary values. Do not use to_messages(), to_string() or anything of the sort.
