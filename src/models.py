"""Data models for the Strategic Roundtable."""

from pydantic import BaseModel, Field
from typing import List, Optional

class CareerMemo(BaseModel):
    """A structured career memo."""
    content: str = Field(..., description="Raw memo content")
    northstar: str = Field("", description="One-line maxed-out vision")
    narrative: str = Field("", description="Personal story and context")
    problems: str = Field("", description="Key problems to solve")
    root_cause: str = Field("", description="Analysis of problem origins")
    outcomes: str = Field("", description="Ambitious goals")
    strategy: str = Field("", description="Plan to solve problems")
    experiments: str = Field("", description="Concrete experiments to run")
    
    def to_text(self) -> str:
        """Convert the structured memo to a formatted text string."""
        return self.content

class Question(BaseModel):
    """A question from a coach."""
    text: str = Field(..., description="The question text")
    coach: str = Field(..., description="The coach asking the question")
    reasoning: str = Field(..., description="The coach's reasoning for asking this question")
