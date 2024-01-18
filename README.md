## Older project to chat with custom gpt bots

The project runs on flask and tailwind.
To install and run, create a venv and install the requirements.txt file.

### project description

Users should be able to describe and customize their own gpt's with the formula manager.
A "Formula" is a sheet that describes the behavior and instructs GPT to act according to the formula.

before using, it's important to add your own openai api code in the following file: openai_logic.py
change the api code where it says

``` openai.api_key = "xX-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" ```
