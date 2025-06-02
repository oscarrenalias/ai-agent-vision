# AI Agent Vision

[![Latest Release Build](https://github.com/oscarrenalias/ai-agent-vision/actions/workflows/release.yml/badge.svg)](https://github.com/oscarrenalias/ai-agent-vision/actions/workflows/release.yml)

This is a personal project to create an AI-based assistant to manage everything around groceries at home:

- Scanning of groceries receipts, including item extraction
- Recipe management
- Meal planning and shopping list generation (in progress)

Includes backend components to run the agents as well as an agentic user interface built on CopilotKit.

# Technologies

The application consists of three components:

- A Python based backend running the agents, built on top of [LangChain](https://www.langchain.com/), [LangGraph](https://langgraph.dev/), and [CopilotKit](https://www.copilotkit.ai/) for agentic UI generation.
- A frontend built on [Next.js](https://nextjs.org/), with CopilotKit taking care of agentic user interface capabilities
- MongoDb as the database.

Additionally, the application uses OpenAI models for its functionality. It does not support any other AI provider at the moment. Please note that you will need an OpenAI API key to run the application, for which an OpenAI account is required at https://platform.openai.com as well as some credit to be loaded.

# Deployment

The application is packaged as Docker containers as well as a matching Docker Compose file, which are provided as part of GitHub releases for every CI build: https://github.com/oscarrenalias/ai-agent-vision/releases.

The application is designed to be deployed to a Raspberry Pi 5 (versions 4 won't work as Mongo versions 5 or higher won't work on Raspberry Pi 4) using a .deb package, avialable as part of each release. This is the preferred method for deployment (works for me, at least)

See [the deploy folder](deploy/README.md) for more information on deploying the application to Raspberry Pi OS.

# Development

Please refer to the corresponding documentation:

- [Backend](backend/README.md)
- [UI](ui/README.md)
