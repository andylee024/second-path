from agents.base import BaseAgent
from prompts.system_prompts import WEAVER

class WeaverAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Weaver",
            style="Systems & Complexity",
            system_prompt=WEAVER
        ) 