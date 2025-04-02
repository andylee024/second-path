"""Coach agent implementations for the Strategic Roundtable."""

from .base import BaseAgent
from prompts.dalio_prompt import DALIO_PROMPT
from prompts.weaver_prompt import WEAVER_PROMPT
from prompts.naval_prompt import NAVAL_PROMPT

class DalioAgent(BaseAgent):
    """Ray Dalio coach agent implementation."""
    
    def __init__(self):
        """Initialize the Ray Dalio agent."""
        super().__init__(
            name="Ray Dalio",
            system_prompt=DALIO_PROMPT
        )


class WeaverAgent(BaseAgent):
    """Graham Weaver coach agent implementation."""
    
    def __init__(self):
        """Initialize the Graham Weaver agent."""
        super().__init__(
            name="Graham Weaver",
            system_prompt=WEAVER_PROMPT
        )


class NavalAgent(BaseAgent):
    """Naval Ravikant coach agent implementation."""
    
    def __init__(self):
        """Initialize the Naval Ravikant agent."""
        super().__init__(
            name="Naval Ravikant",
            system_prompt=NAVAL_PROMPT
        ) 