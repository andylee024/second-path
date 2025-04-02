"""Session management for the Strategic Roundtable."""

from typing import Dict, Literal, Optional
from models import CareerMemo
from agents.facilitator import FacilitatorAgent
from agents.coach_agents import DalioAgent, WeaverAgent, NavalAgent
import time
from openai import OpenAI

Mode = Literal["introspection", "memo"]
client = OpenAI()

class RoundtableSession:
    """Manages a roundtable session with coaches and facilitator."""
    
    def __init__(self, memo: CareerMemo):
        """Initialize the session.
        
        Args:
            memo: The user's career memo
        """
        self.memo = memo
        self.facilitator = FacilitatorAgent()
        self.coaches = [
            DalioAgent(),
            WeaverAgent(),
            NavalAgent()
        ]
        
        # Initialize threads for each agent
        self.facilitator.create_thread()
        for coach in self.coaches:
            coach.create_thread()
    
    def _get_last_response(self, agent, run) -> str:
        """Get the last response from an agent after a run completes.
        
        Args:
            agent: The agent whose response we want
            run: The run object from the assistant
            
        Returns:
            The last response text
        """
        # Wait for run to complete
        while run.status in ["queued", "in_progress"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=agent.thread.id,
                run_id=run.id
            )
        
        if run.status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=agent.thread.id,
                order="desc",
                limit=1
            )
            return messages.data[0].content[0].text.value
        else:
            raise Exception(f"Run failed with status: {run.status}")
    
    def run_turn(self, mode: Mode, user_response: Optional[str] = None) -> Dict:
        """Run a single turn of the session.
        
        Args:
            mode: The current mode ("introspection" or "memo")
            user_response: The user's response to previous questions (optional)
            
        Returns:
            Dictionary containing the current state and next steps
        """
        if mode == "introspection":
            return self._run_introspection_turn(user_response)
        else:
            return self._run_memo_turn(user_response)
    
    def _run_introspection_turn(self, user_response: Optional[str] = None) -> Dict:
        """Run a turn in introspection mode.
        
        Args:
            user_response: The user's response to previous questions (optional)
            
        Returns:
            Dictionary containing the current state and next steps
        """
        # Step 1: Facilitator analyzes the memo
        self.facilitator.add_message(f"Please analyze this career memo and identify areas that need improvement:\n\n{self.memo.content}")
        facilitator_analysis = self.facilitator.run_assistant()
        
        # Step 2: Get questions from each coach based on facilitator's analysis
        coach_responses = []
        for coach in self.coaches:
            coach.add_message(f"""Here is a career memo:
            
{self.memo.content}

The facilitator has identified these areas for improvement: 
{facilitator_analysis}
                            
Based on this analysis, what questions would you ask to help strengthen these areas?""")
            
            coach_questions = coach.run_assistant()
            coach_responses.append({
                "coach": coach.name,
                "questions": coach_questions
            })
        
        return {
            "current_memo": self.memo,
            "facilitator_analysis": facilitator_analysis,
            "coach_responses": coach_responses
        }
    
    def _run_memo_turn(self, user_response: Optional[str] = None) -> Dict:
        """Run a turn in memo mode.
        
        Args:
            user_response: The user's response to previous questions (optional)
            
        Returns:
            Dictionary containing the current state and next steps
        """
        prompt = f"Please help draft an updated career memo based on this current version:\n\n{self.memo}"
        if user_response:
            prompt += f"\n\nUser's Response:\n{user_response}"
            
        self.facilitator.add_message(prompt)
        facilitator_response = self.facilitator.run_assistant()
        
        # Update the memo content with the facilitator's response
        self.memo.content = facilitator_response
        
        return {
            "current_memo": self.memo,
            "facilitator_response": facilitator_response
        }