<picture> <source media="(prefers-color-scheme: dark)" srcset="https://i.imgur.com/6IyfFHr.png"> <source media="(prefers-color-scheme: light)" srcset="https://i.imgur.com/6IyfFHr.png"> <img alt="README image" src="https://i.imgur.com/6IyfFHr.png"> </picture>

# TermGPT

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)

## About <a name = "about"></a>

TermGPT is a python program that allows you to use chatgpt from your terminal

**Current(Not Limited To) features includes:**
- Syntax Highlighting And Formatting
- Persistent Conversation i.e It remembers previous chat just like in chatgpt
- Works In [Interactive](#interactive) And [Non-interactive](#non-interactive) Mode
- In Interactive Mode, It Can Recognize And Expand Files/File_paths When Passed In Prompt


## Getting Started <a name = "getting_started"></a>

To set up the project for use, follow these steps:

### Prerequisites

Ensure you have the following prerequisites installed:

- Python 3.x
- OPENAI_API_KEY
  - Retrieve your API key from [OpenAI](https://platform.openai.com/account/api-keys)


### Installing

Follow these steps to get program running:

1. Clone the repository to root directory:
   ```
   git clone https://github.com/Hordunlarmy/TermGPT ~/TermGPT && cd ~/TermGPT
   ```

2. Change permission mode
    ```
    chmod +x termgpt.py
    chmod +x chatgpt
    ```

3. Install dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

4. Set OPENAI_API_KEY environment variable
    ```
    echo "export OPENAI_API_KEY=<your token>" >> ~/.bashrc
    source ~/.bashrc

    ```
    replace ```<your token>``` with your openai token
    replace ~/.bashrc with your shell config path only if not using bash

5. Add script to directory in your PATH
    ```
    sudo mv chatgpt /usr/bin/
    ```
 
### Usage <a name = "usage"></a>

Here are instructions on how to use the system:

#### Interactive Mode <a name = "interactive"></a>

* run ```chatgpt``` 
  * pass file in prompt usage
  ![file usage git](https://i.imgur.com/9sOR7rX.gif)

* ```exit``` or ```quit``` to leave

#### Non-Interactive Mode <a name = "non-interactive"></a>

* ```chatgpt "prompt" "file"```
  * example ```chatgpt "what is a more polite way to write this" test1.txt```
