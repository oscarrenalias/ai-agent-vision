#!/usr/bin/env python3
"""
Command-line interface for AI Agent Vision

This script provides a text-based interface for interacting with the MainGraph
LangGraph implementation. It allows users to input messages, process them through
the graph, and displays the responses.

Usage:
    python cli.py [--debug] [--fulldebug]

Commands:
    /help           - Display help information
    /upload <path>  - Set image path for receipt processing
    /save [file]    - Save conversation to file (default: conversation.json)
    /load [file]    - Load conversation from file (default: conversation.json)
    /clear          - Clear conversation history
    /debug          - Toggle debug mode for application code
    /fulldebug      - Toggle full debug mode (includes external libraries)
    /loglevel <level> - Set log level (DEBUG, INFO, WARNING, ERROR)
    /state          - Display full state object (for debugging)
    /exit or /quit  - Exit the application
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table

from agents.maingraph import GlobalState, MainGraph

# Load environment variables
load_dotenv(verbose=True)

# Initialize rich console for better output formatting
console = Console()


def print_header():
    """Print application header with formatting"""
    console.print(
        Panel.fit(
            "[bold green]AI Agent Vision CLI[/bold green]\n"
            "[italic]Type /help for available commands, /exit to quit[/italic]",
            border_style="blue",
        )
    )


def print_help():
    """Print help information about available commands"""
    help_table = Table(title="Available Commands")
    help_table.add_column("Command", style="cyan")
    help_table.add_column("Description", style="green")

    commands = [
        ("/help", "Display this help information"),
        ("/upload <path>", "Set image path for receipt processing"),
        ("/save [file]", "Save conversation to JSON file (default: conversation.json)"),
        ("/load [file]", "Load conversation from JSON file (default: conversation.json)"),
        ("/clear", "Clear conversation history"),
        ("/debug", "Toggle debug mode for application code"),
        ("/fulldebug", "Toggle full debug mode (includes external libraries like LangGraph)"),
        ("/loglevel <level>", "Set log level (DEBUG, INFO, WARNING, ERROR)"),
        ("/state", "Display full state object (for debugging)"),
        ("/exit or /quit", "Exit application"),
    ]

    for cmd, desc in commands:
        help_table.add_row(cmd, desc)

    console.print(help_table)


def save_conversation(state: GlobalState, filename: str = "conversation.json"):
    """Save conversation history to a JSON file"""
    try:
        with open(filename, "w") as f:
            json.dump(state["messages"], f, indent=2)
        return True
    except Exception as e:
        console.print(f"[bold red]Error saving conversation: {str(e)}[/bold red]")
        return False


def load_conversation(filename: str = "conversation.json") -> List:
    """Load conversation history from a JSON file"""
    try:
        if not os.path.exists(filename):
            console.print(f"[bold yellow]File not found: {filename}[/bold yellow]")
            return []

        with open(filename, "r") as f:
            messages = json.load(f)
        return messages
    except Exception as e:
        console.print(f"[bold red]Error loading conversation: {str(e)}[/bold red]")
        return []


def format_message(message: Dict[str, Any]) -> str:
    """Format a message for display"""
    role = message.get("role", "unknown")
    content = message.get("content", "")

    if role == "human":
        return f"[bold blue]You: [/bold blue] {content}"
    elif role == "assistant":
        return f"[bold green]AI: [/bold green] {content}"
    else:
        return f"[bold yellow]{role}: [/bold yellow] {content}"


def display_state_info(state: GlobalState, debug_mode: bool):
    """Display additional information from the state"""
    if state.get("last_receipt"):
        console.print("[bold yellow][Receipt processed successfully][/bold yellow]")

        if debug_mode:
            receipt = state.get("last_receipt")
            receipt_table = Table(title="Receipt Details")
            receipt_table.add_column("Item", style="cyan")
            receipt_table.add_column("Price", style="green")

            if hasattr(receipt, "items") and receipt.items:
                for item in receipt.items:
                    receipt_table.add_row(item.name, f"${item.price:.2f}")  # noqa: E231
                console.print(receipt_table)

    if state.get("last_meal_plan"):
        console.print("[bold yellow][Meal plan created successfully][/bold yellow]")

        if debug_mode and state.get("last_meal_plan"):
            console.print(Panel(Markdown(str(state.get("last_meal_plan"))), title="Meal Plan", border_style="green"))

    if debug_mode:
        console.print("[bold yellow]Debug State:[/bold yellow]")
        # Print only key state information to avoid overwhelming output
        debug_info = {
            "has_items_lookup": state.get("items_lookup") is not None,
            "has_image_path": state.get("image_file_path") is not None,
            "messages_count": len(state.get("messages", [])),
        }
        console.print(debug_info)


def display_full_state(state: GlobalState):
    """Display the complete state object for debugging"""
    console.print("[bold yellow]Full State Object:[/bold yellow]")

    # Create a panel for the state content
    state_panel = Panel(
        Pretty(state, max_depth=4, indent_guides=True, expand_all=True),
        title="[bold]State Contents[/bold]",
        border_style="yellow",
    )

    console.print(state_panel)


def setup_logging(debug_mode=False, full_debug=False):
    """Configure basic console logging

    Args:
        debug_mode: Enable debug logging for application code
        full_debug: Enable debug logging for all libraries (LangGraph, LangChain, etc.)
    """
    # Set the log level based on debug mode
    log_level = logging.DEBUG if debug_mode else logging.INFO

    # Remove any existing handlers to avoid duplicates
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    # Set specific logger levels for libraries we care about
    if full_debug:
        # In full debug mode, set everything to DEBUG
        logging.getLogger("langgraph").setLevel(logging.DEBUG)
        logging.getLogger("langchain").setLevel(logging.DEBUG)
    else:
        # In normal mode, keep external libraries at INFO level regardless of app debug state
        logging.getLogger("langgraph").setLevel(logging.INFO)
        logging.getLogger("langchain").setLevel(logging.INFO)

    logging.info(
        "Logging configured with level: %s (Full debug: %s)", "DEBUG" if debug_mode else "INFO", "ON" if full_debug else "OFF"
    )


async def main():
    """Main CLI application"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="AI Agent Vision CLI")
    parser.add_argument("--debug", action="store_true", help="Start in debug mode")
    parser.add_argument("--fulldebug", action="store_true", help="Start in full debug mode (includes external libraries)")
    args = parser.parse_args()

    # Set up logging
    setup_logging(debug_mode=args.debug, full_debug=args.fulldebug)

    # Create a checkpointer to save state between interactions
    checkpointer = MemorySaver()

    # Initialize the graph with a config
    config = {"configurable": {"thread_id": 1}}

    console.print("[bold yellow]Initializing AI Agent Vision...[/bold yellow]")
    graph = MainGraph(config=config).as_subgraph().compile(checkpointer=checkpointer)

    # Initialize the state with an empty message list
    state = GlobalState.make_instance()

    # Initialize command session with history
    command_completer = WordCompleter(
        ["/help", "/upload", "/save", "/load", "/clear", "/debug", "/fulldebug", "/loglevel", "/state", "/exit", "/quit"]
    )
    session = PromptSession(
        history=FileHistory(".chat_history"), auto_suggest=AutoSuggestFromHistory(), completer=command_completer
    )

    # Track debug mode
    debug_mode = args.debug
    full_debug_mode = args.fulldebug

    # Setup logging
    setup_logging(debug_mode=debug_mode, full_debug=full_debug_mode)

    print_header()
    if debug_mode:
        console.print("[bold yellow]Debug mode is ON[/bold yellow]")
    if full_debug_mode:
        console.print("[bold yellow]Full debug mode is ON (including external libraries)[/bold yellow]")

    # Main interaction loop
    while True:
        try:
            # Get user input with command completion
            console.print("[bold blue]You: [/bold blue]")
            user_input = await session.prompt_async("> ")

            # Handle empty input
            if not user_input.strip():
                continue

            # Process commands
            if user_input.startswith("/"):
                cmd_parts = user_input.split(maxsplit=1)
                command = cmd_parts[0].lower()
                args = cmd_parts[1] if len(cmd_parts) > 1 else ""

                # Help command
                if command == "/help":
                    print_help()
                    continue

                # Exit commands
                elif command in ["/exit", "/quit"]:
                    console.print("[bold green]Exiting AI Agent Vision. Goodbye![/bold green]")
                    break

                # Upload command for setting receipt image path
                elif command == "/upload":
                    if not args:
                        console.print("[bold red]Please specify a file path.[/bold red]")
                        continue

                    # Expand user path if needed
                    # path = os.path.expanduser(args)
                    # path = ""
                    # if not os.path.exists(path):
                    #    console.print(f"[bold red]File not found: {path}[/bold red]")
                    #    continue

                    path = args
                    state["image_file_path"] = path
                    console.print(f"[bold green]Image path set to: {path}[/bold green]")
                    continue

                # Save conversation command
                elif command == "/save":
                    filename = args if args else "conversation.json"
                    if save_conversation(state, filename):
                        console.print(f"[bold green]Conversation saved to {filename}[/bold green]")
                    continue

                # Load conversation command
                elif command == "/load":
                    filename = args if args else "conversation.json"
                    messages = load_conversation(filename)
                    if messages:
                        state["messages"] = messages
                        console.print(f"[bold green]Loaded {len(messages)} messages from {filename}[/bold green]")

                        # Display last few messages for context
                        if messages:
                            console.print("[bold yellow]Last message:[/bold yellow]")
                            console.print(format_message(messages[-1]))
                    continue

                # Clear conversation command
                elif command == "/clear":
                    state["messages"] = []
                    console.print("[bold green]Conversation history cleared[/bold green]")
                    continue

                # Debug mode toggle
                elif command == "/debug":
                    debug_mode = not debug_mode
                    console.print(f"[bold yellow]Debug mode: {'ON' if debug_mode else 'OFF'}[/bold yellow]")
                    # Update logging level when debug mode changes
                    setup_logging(debug_mode=debug_mode, full_debug=full_debug_mode)
                    continue

                # Full debug mode toggle (includes external libraries)
                elif command == "/fulldebug":
                    full_debug_mode = not full_debug_mode
                    console.print(f"[bold yellow]Full debug mode: {'ON' if full_debug_mode else 'OFF'}[/bold yellow]")
                    if full_debug_mode:
                        console.print(
                            "[bold yellow]Warning: This will produce a lot of output from external libraries[/bold yellow]"
                        )
                    # Update logging configuration
                    setup_logging(debug_mode=debug_mode, full_debug=full_debug_mode)
                    continue

                # Set log level
                elif command == "/loglevel":
                    if not args:
                        console.print("[bold red]Please specify a log level (DEBUG, INFO, WARNING, ERROR).[/bold red]")
                        continue

                    level = args.strip().upper()
                    valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
                    if level not in valid_levels:
                        console.print(f"[bold red]Invalid log level. Use one of: {', '.join(valid_levels)}[/bold red]")
                        continue

                    # Set the log level
                    numeric_level = getattr(logging, level)
                    logging.getLogger().setLevel(numeric_level)
                    logging.getLogger("langgraph").setLevel(numeric_level)
                    logging.getLogger("langchain").setLevel(numeric_level)

                    console.print(f"[bold yellow]Log level set to: {level}[/bold yellow]")
                    continue

                # Display full state
                elif command == "/state":
                    display_full_state(state)
                    continue

                # Unknown command
                else:
                    console.print(f"[bold red]Unknown command: {command}[/bold red]")
                    continue

            # Regular message processing
            # Add the user's message to the state
            state["messages"].append({"role": "human", "content": user_input})

            # Display "thinking" indicator
            with console.status("[bold green]Thinking...[/bold green]"):
                # Process user input through the graph
                logging.info("Processing user input: %s", user_input)
                result = await graph.ainvoke(state, config=config)
                logging.info("Finished processing user input")

            # Update the state with the result
            state = result

            # Display the AI's response (last message)can
            if state["messages"] and len(state["messages"]) > 0:
                last_message = state["messages"][-1]
                console.print("[bold yellow]=== 🤖 AI response ===[/bold yellow]")
                if last_message.type == "ai":
                    console.print(Markdown(last_message.content))
                elif last_message.type == "tools":
                    console.print("[bold yellow]Tool call. Not implemented yet.[/bold yellow]")
                else:
                    console.print("[bold yellow][No response][/bold yellow]")
                console.print("\n")

            # Display additional state information
            display_state_info(state, debug_mode)

        except KeyboardInterrupt:
            console.print("\n[bold yellow]Interrupted. Type /exit to quit.[/bold yellow]")
            continue

        except EOFError:
            console.print("\n[bold green]Exiting AI Agent Vision. Goodbye![/bold green]")
            break

        except Exception as e:
            console.print(f"[bold red]Error: {str(e)}[/bold red]")
            import traceback

            console.print(traceback.format_exc())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold green]Exiting AI Agent Vision. Goodbye![/bold green]")
        sys.exit(0)


# Entry point for script setup
def entry_point():
    """
    Entry point for pyproject.toml scripts.
    This function is called when running 'ai-agent-vision-cli' command.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[bold green]Exiting AI Agent Vision. Goodbye![/bold green]")
        sys.exit(0)
