from agents.base import BaseAgent
from prompts.system_prompts import DALIO

class DalioAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Dalio",
            style="Principles & Systems Thinking",
            system_prompt=DALIO
        ) 