from agents.base import BaseAgent
from prompts.system_prompts import DALIO

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

class DalioAgent(BaseAgent):
    def __init__(self):
        # Read the markdown file containing Dalio's principles
        # dalio_principles_content = read_markdown_file('/Users/andylee/Projects/second-path/src/prompts/dalio_prompt.md')
        
        # Use the content as the system prompt
        super().__init__(
            name="Dalio",
            style="Principles & Systems Thinking",
            system_prompt=DALIO
        ) 