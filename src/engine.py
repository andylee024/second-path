from typing import Dict, Any
from agents.naval import NavalAgent
from agents.dalio import DalioAgent
from agents.weaver import WeaverAgent
from agents.base import Strategy

class AgentEngine:
    def __init__(self):
        self.agents = [
            # NavalAgent(),
            DalioAgent(),
            # WeaverAgent()
        ]

    def generate_all_strategies(self, memo: Dict[str, Any]) -> Dict[str, Strategy]:
        """Generate strategies from all agents based on the memo."""
        strategies = {}
        for agent in self.agents:
            try:
                strategies[agent.name] = agent.generate_strategy(memo)
            except Exception as e:
                print(f"Error generating strategy for {agent.name}: {str(e)}")
                continue
        return strategies

    def combine_strategies(self, accepted_strategies: Dict[str, Strategy]) -> Strategy:
        """Combine accepted strategies into a composite strategy."""
        # TODO: Implement strategy combination logic
        # For now, return the first accepted strategy
        if not accepted_strategies:
            raise ValueError("No strategies to combine")
        return list(accepted_strategies.values())[0] 