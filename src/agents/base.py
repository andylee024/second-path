from typing import Dict, Any
from openai import OpenAI

client = OpenAI()
from pydantic import BaseModel

class Strategy(BaseModel):
    advisor: str
    outcome: str
    rationale: str
    plan: str
    experiments: list[str]
    uncertainties: list[str]

class BaseAgent:
    def __init__(self, name: str, style: str, system_prompt: str):
        self.name = name
        self.style = style
        self.system_prompt = system_prompt

    def generate_strategy(self, memo: Dict[str, Any]) -> Strategy:
        """Generate a strategy based on the user's memo."""
        try:
            response = client.chat.completions.create(model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Here is the user's memo:\n{memo}"}
            ],
            temperature=0.7,
            max_tokens=1000)

            # Parse the response into a structured format
            content = response.choices[0].message.content
            # TODO: Add proper parsing logic here
            # For now, we'll create a basic structure
            return Strategy(
                advisor=self.name,
                outcome="Sample outcome",
                rationale="Sample rationale",
                plan="Sample plan",
                experiments=["Sample experiment"],
                uncertainties=["Sample uncertainty"]
            )

        except Exception as e:
            print(f"Error generating strategy for {self.name}: {str(e)}")
            raise 