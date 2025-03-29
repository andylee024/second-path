from agents.base import BaseAgent
from prompts.system_prompts import NAVAL

class NavalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Naval",
            style="Leverage & Asymmetric Bets",
            system_prompt=NAVAL
        ) 