#!/usr/bin/env python3
import openai
import os
import sys
import time
import readline
from pygments import highlight
from pygments.lexers import guess_lexer
from pygments.formatters import TerminalFormatter
from pygments.token import (Token, Comment, Keyword, Name, String, Number)
import colorama

# custom color scheme
COLOR_SCHEME = {
    Token: ('gray', 'gray'),
    Comment: ('magenta', 'brightmagenta'),
    Keyword: ('blue', '**'),
    Keyword.Type: ('green', '*brightgreen*'),
    Name.Builtin: ('cyan', 'brightblue'),
    Name.Function: ('blue', 'brightblue'),
    Name.Class: ('_green_', 'brightblue'),
    Name.Decorator: ('magenta', 'brightmagenta'),
    Name.Variable: ('blue', 'brightblue'),
    String: ('yellow', 'brightyellow'),
    Number: ('blue', 'brightyellow')
}

# Init colors
colorama.init()

openai.api_key = os.getenv("OPENAI_API_KEY")

# Check if the OpenAI API key is present
if not openai.api_key:
    print("OpenAI API key not found. "
          "Please set the OPENAI_API_KEY environment variable.")
    sys.exit()


def colorize_code(code):
    """Syntax highlighting"""
    lexer = guess_lexer(code)
    formatter = TerminalFormatter(bg='dark', colorscheme=COLOR_SCHEME)
    return highlight(code, lexer, formatter)


def emulate_typing(message):
    """Print message letter by letter"""
    for ch in message:
        print(ch, end='', flush=True)
        time.sleep(0.002)
    print(flush=True)


def process_file(user_input):
    """Process content with a file"""
    if isinstance(user_input, list):
        user_input = ' '.join(user_input)

    file_mentions = [word for word in user_input.split()
                     if os.path.isfile(word)]
    if file_mentions:
        for file_mention in file_mentions:
            with open(file_mention, 'r') as file:
                file_content = file.read()
                user_input = user_input.replace(
                    file_mention, file_content).strip()
    return user_input


def print_chatgpt_response(answer):
    """Print ChatGPT answer"""
    print(colorama.Fore.YELLOW + 'ChatGPT: ' +
          colorama.Style.RESET_ALL, end='')
    parse_answer = answer.split('```')
    if len(parse_answer) > 1:
        emulate_typing(parse_answer[0].strip()[:-1])
        for chunk in parse_answer[1:]:
            if chunk.strip():
                code = '\n'.join(chunk.split('\n')[1:])
                highlight_code = colorize_code(code)
                if code.strip():
                    emulate_typing(highlight_code.strip())
            else:
                emulate_typing('\n' + chunk.strip())
    else:
        emulate_typing(answer.strip())


messages = [{
    'role': 'system',
    'content': 'You are a helpful assistant.'
}]

if __name__ == "__main__":
    # Main loop
    file_processed = False

    while True:
        try:
            # non-interactive mode
            if not file_processed and len(sys.argv) > 1:
                question = process_file(sys.argv[1:])
                file_processed = True
            else:
                # Get user input in interactive mode
                user_input = input(colorama.Fore.CYAN +
                                   'You: ' + colorama.Style.RESET_ALL)
                question = process_file(user_input)

            # Check for exit command
            if question.lower() == 'quit' or question.lower() == 'exit':
                break

            # Add user message to the conversation
            messages.append({
                'role': 'user',
                'content': question
            })

            # OpenAI API response
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            # Extract text from response
            answer = response.choices[0].message.content

            # Add ChatGPT message to the conversation
            messages.append({
                'role': 'assistant',
                'content': answer
            })

            print_chatgpt_response(answer)

        # Catch OpenAI API errors
        except openai.error.RateLimitError as e:
            print(colorama.Fore.YELLOW +
                  f"ChatGPT: Rate limit reached - {e}" +
                  colorama.Style.RESET_ALL)
            print("Please try again in 20s.")
            time.sleep(20)
            break

        except openai.error.OpenAIError as e:
            print(colorama.Fore.YELLOW +
                  f"ChatGPT: An error occurred - {e}" +
                  colorama.Style.RESET_ALL)

        except Exception as e:
            print(
                colorama.Fore.YELLOW + "ChatGPT: I'm busy, only 3 requests "
                "per minute are allowed for free account, please ask your "
                "question again in 20 seconds" + colorama.Style.RESET_ALL)
            time.sleep(20)
            break
