#!/usr/bin/env python3
import argparse
import asyncio
import atexit
import os
import re
import sys

from openai import AsyncOpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from rich import print
from rich.console import Console
from rich.syntax import Syntax

messages = [{"role": "system", "content": "You are a helpful assistant."}]

# Path to the history file
HISTORY_FILE = os.path.expanduser("~/.chatgpt_terminal_history")


def delete_history():
    """Delete the history file."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


async def format_response(content, typing_delay=0.05):
    """Format the response to handle code blocks with rich and simulate typing."""
    code_block_pattern = re.compile(r"```(.*?)\n(.*?)```", re.DOTALL)
    parts = code_block_pattern.split(content)
    console = Console()

    formatted_parts = []

    for i, part in enumerate(parts):
        if i % 3 == 0:
            # Regular text
            formatted_parts.append(("text", part))
        elif i % 3 == 1:
            # Language identifier (part of the triple backticks)
            lang = part.strip()
        else:
            # Code block
            code = part.strip()
            syntax = Syntax(code, lang, theme="native")
            formatted_parts.append(("syntax", syntax))

    for kind, part in formatted_parts:
        if kind == "syntax":
            console.print(part)
        else:
            # Simulate typing for regular text
            for char in part:
                print(char, end="", flush=True)
                await asyncio.sleep(0.01)


async def fetch_response(client, model, messages):

    loading = True

    async def display_loading():
        """Display loading animation with three dots in a cycle."""
        while loading:
            for i in range(1, 6):
                sys.stdout.write("." * i + "\b" * i)
                sys.stdout.flush()
                await asyncio.sleep(0.5)
                if not loading:
                    break
            sys.stdout.write("     \b\b\b\b\b")  # Clear the dots
            sys.stdout.flush()

    try:
        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
        )

        assistant_message = {"role": "assistant", "content": ""}

        # Start loading animation
        loading_task = asyncio.create_task(display_loading())
        sys.stdout.write("\033[1;33mChatGPT: \033[0m")
        sys.stdout.flush()

        async for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            assistant_message["content"] += content

        # Stop loading animation
        loading = False
        await loading_task

        # Append the assistant's response to the messages
        messages.append(assistant_message)

        # Format and print the response
        await format_response(assistant_message["content"])
        print()

    except Exception as e:
        print(f"An error occurred: {e}")


def extract_file_content_from_prompt(prompt_text):
    """Extract file references and replace them with their content."""
    # Match file names or paths in the prompt
    file_pattern = re.compile(
        r"\b\S+\.\w+\b"
    )  # Match words with extensions like `.py`, `.txt`, etc.
    matches = file_pattern.findall(prompt_text)

    for match in matches:
        if os.path.isfile(match):
            try:
                with open(match, "r") as file:
                    file_content = file.read()
                    # Add file content to the prompt
                    prompt_text = prompt_text.replace(
                        match, f"\n[File {match}]\n{file_content}\n"
                    )
            except Exception as e:
                print(f"[bold red]Error reading {match}:[/bold red] {e}")

    return prompt_text


async def main(prompt_text=None):
    # Ensure the API key is set
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print(
            "[bold red]Error:[/bold red] Please set the OPENAI_API_KEY environment variable."
        )
        return

    # Initialize the asynchronous OpenAI client
    client = AsyncOpenAI(api_key=api_key)

    # Create a console object for rich output
    console = Console()

    # Define the style for the prompt
    style = Style.from_dict({"prompt": "ansicyan"})

    if not prompt_text:
        # Create a PromptSession for multi-line input
        session = PromptSession(history=FileHistory(HISTORY_FILE), style=style)

        # Define key bindings for multi-line input
        bindings = KeyBindings()

        @bindings.add("tab")
        def _(event):
            buffer = event.app.current_buffer
            buffer.insert_text("\n")

        @bindings.add("enter")
        def _(event):
            buffer = event.app.current_buffer
            buffer.validate_and_handle()

        # Prompt to be sent to the model in interactive mode
        prompt_text = await session.prompt_async(
            [("class:prompt", "You: ")],
            multiline=True,
            key_bindings=bindings,
            wrap_lines=True,
        )

    # Extract and expand file content from the prompt
    expanded_prompt = extract_file_content_from_prompt(prompt_text)

    # Add user message to the conversation
    messages.append({"role": "user", "content": expanded_prompt})

    # Fetch and print response from OpenAI
    await fetch_response(client, "gpt-4", messages)


def run_async_function(async_fn, *args, **kwargs):
    """Helper function to run an async function."""
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(async_fn(*args, **kwargs))
    else:
        return loop.run_until_complete(async_fn(*args, **kwargs))


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Chat with OpenAI's GPT-4 from the terminal"
    )
    parser.add_argument("-p", "--prompt", type=str, help="Prompt to send to the model")
    parser.add_argument(
        "positional_prompt", nargs="*", help="Positional prompt to send to the model"
    )

    args = parser.parse_args()

    # Combine optional and positional prompts
    prompt_text = args.prompt or " ".join(args.positional_prompt)

    while True:
        try:
            run_async_function(main, prompt_text=prompt_text)
            if prompt_text:
                break  # Exit after processing the provided prompt in non-interactive mode
            prompt_text = None  # Reset prompt for interactive mode
        except KeyboardInterrupt:
            # Handle Ctrl+C or other interrupt signals
            delete_history()
            print("\n[bold red]Exiting...[/bold red]")
            break
