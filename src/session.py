"""Session manager for the Strategic Roundtable."""

from agents.coach_agents import DalioAgent, WeaverAgent, NavalAgent
from agents.facilitator import FacilitatorAgent
from agents.base import AgentResponse
from typing import Dict, List, Optional
from openai import OpenAI
import time

client = OpenAI()


class RoundtableSession:
    """Manages a session of the Strategic Roundtable."""
    
    def __init__(self):
        """Initialize a new session."""
        self.thread = None
        self.dalio_agent = DalioAgent()
        self.weaver_agent = WeaverAgent()
        self.naval_agent = NavalAgent()
        self.facilitator_agent = FacilitatorAgent()
        self.coach_responses = {}
        self.facilitator_response = None
    
    def start_session(self, memo_text: str, mode: str):
        """Start a new session.
        
        Args:
            memo_text: The user's memo
            mode: The mode to operate in (introspection or analysis)
        """
        self.thread = client.beta.threads.create()
        
        # Add the memo to the thread
        client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=f"User Memo:\n{memo_text}"
        )
        
        # Process with each coach
        print(f"Processing with Ray Dalio in {mode} mode...")
        self.coach_responses["Dalio"] = self.dalio_agent.process_thread(self.thread.id, mode)
        
        print(f"Processing with Graham Weaver in {mode} mode...")
        self.coach_responses["Weaver"] = self.weaver_agent.process_thread(self.thread.id, mode)
        
        print(f"Processing with Naval Ravikant in {mode} mode...")
        self.coach_responses["Naval"] = self.naval_agent.process_thread(self.thread.id, mode)
        
        # Process with facilitator
        print("Synthesizing responses with facilitator...")
        self.facilitator_response = self.facilitator_agent.process_thread(self.thread.id)
        
        return {
            "coaches": self.coach_responses,
            "facilitator": self.facilitator_response
        }
    
    def get_messages(self, limit: int = 10) -> List[Dict]:
        """Get the messages from the thread.
        
        Args:
            limit: The maximum number of messages to retrieve
            
        Returns:
            A list of message dictionaries
        """
        if not self.thread:
            return []
        
        messages = client.beta.threads.messages.list(
            thread_id=self.thread.id,
            order="desc",
            limit=limit
        )
        
        return [
            {
                "role": message.role,
                "content": message.content[0].text.value if message.content else "",
                "created_at": message.created_at
            }
            for message in messages.data
        ] 