"""Facilitator agent for the Strategic Roundtable."""

from openai import OpenAI
from agents.base import BaseAgent
from models import CareerMemo
from prompts.system_prompts import FACILITATOR_PROMPT
import time

client = OpenAI()

class FacilitatorAgent(BaseAgent):
    """Facilitator agent that manages the memo refinement process."""
    
    def __init__(self):
        """Initialize the facilitator agent."""
        super().__init__(
            name="Facilitator",
            system_prompt=FACILITATOR_PROMPT
        )        
        self.thread = None
        self.assistant = self._create_assistant()
    
    def _create_assistant(self):
        """Create the OpenAI Assistant for this agent."""
        return client.beta.assistants.create(
            name=self.name,
            instructions=self.system_prompt,
            model="gpt-4"
        )
    
    def create_thread(self):
        """Create a new thread for this agent."""
        self.thread = client.beta.threads.create()
        return self.thread
    
    def add_message(self, content):
        """Add a message to the current thread."""
        if not self.thread:
            self.create_thread()
        
        return client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=content
        )
    
    def run_assistant(self):
        """Run the assistant on the current thread."""
        if not self.thread:
            raise ValueError("No thread exists. Create one first with create_thread()")
        
        run = client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )
        
        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
        
        # Get the last message
        if run.status == "completed":
            messages = client.beta.threads.messages.list(
                thread_id=self.thread.id,
                order="desc",
                limit=1
            )
            return messages.data[0].content[0].text.value
        else:
            return f"Error: Run failed with status {run.status}"
