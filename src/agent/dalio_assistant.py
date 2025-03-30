from openai import OpenAI
import json
import os
from pydantic import BaseModel
from typing import List, Optional

class StrategicPlan(BaseModel):
    advisor: str
    outcome: str
    rationale: str
    plan: str
    experiments: List[str]
    uncertainties: List[str]

class DalioAdvisor:
    def __init__(self, system_prompt):
        """Initialize the Ray Dalio advisor assistant."""
        self.client = OpenAI()
        self.assistant = self._create_assistant(system_prompt)
        self.thread = None
    
    def _create_assistant(self, system_prompt):
        """Create or retrieve the Ray Dalio assistant."""
        return self.client.beta.assistants.create(
            name="Ray Dalio Career Advisor",
            instructions=system_prompt,
            model="gpt-4o",
            tools=[{"type": "function", "function": {
                "name": "generate_strategic_plan",
                "description": "Generate a structured strategic plan based on the conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "advisor": {"type": "string"},
                        "outcome": {"type": "string"},
                        "rationale": {"type": "string"},
                        "plan": {"type": "string"},
                        "experiments": {"type": "array", "items": {"type": "string"}},
                        "uncertainties": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["advisor", "outcome", "rationale", "plan", "experiments", "uncertainties"]
                }
            }}]
        )
    
    def start_conversation(self, memo_text):
        """Start a new conversation thread with the user's memo."""
        self.thread = self.client.beta.threads.create()
        
        # Add the memo as the first message in the thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=f"User Memo:\n{memo_text}"
        )
        
        # Get initial response from Dalio
        return self.get_response()
    
    def send_message(self, message):
        """Send a user message to the thread and get the response."""
        if not self.thread:
            raise ValueError("No active thread. Call start_conversation() first.")
        
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=message
        )
        
        return self.get_response()
    
    def get_response(self):
        """Run the assistant and get its response."""
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )
        
        # Poll for completion
        while run.status in ["queued", "in_progress"]:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
        
        # Get the most recent assistant message
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id,
            order="desc",
            limit=1
        )
        
        for message in messages.data:
            if message.role == "assistant":
                return message.content[0].text.value
        
        return "No response received."
    
    def generate_strategic_plan(self) -> Optional[StrategicPlan]:
        """Generate a final strategic plan based on the conversation."""
        if not self.thread:
            raise ValueError("No active thread. Call start_conversation() first.")
            
        # Send a message to trigger the strategic plan generation
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content="Based on our conversation, could you please generate a comprehensive strategic plan for me?"
        )
        
        # Create a run with a function call
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
            instructions="Please generate a strategic plan using the generate_strategic_plan function."
        )
        
        # Poll for completion
        completed = False
        while not completed:
            run = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            
            if run.status == "completed":
                completed = True
            elif run.status == "requires_action" and run.required_action.type == "submit_tool_outputs":
                tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
                
                # Submit the function call result
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread.id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": json.dumps({"status": "success"})
                    }]
                )
                
                # Get the function call arguments and parse into StrategicPlan
                plan_data = json.loads(tool_call.function.arguments)
                return StrategicPlan(**plan_data)
            elif run.status == "failed":
                print("Run failed:", run.last_error)
                return None
        
        # If we get here, check messages for a final plan
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id,
            order="desc",
            limit=5
        )
        
        # Try to extract plan from messages
        for message in messages.data:
            if message.role == "assistant":
                try:
                    content = message.content[0].text.value
                    # Very basic attempt to extract JSON if no function call succeeded
                    if "{" in content and "}" in content:
                        json_str = content[content.find("{"):content.rfind("}")+1]
                        plan_data = json.loads(json_str)
                        return StrategicPlan(**plan_data)
                except Exception as e:
                    print(f"Failed to parse plan from message: {e}")
        
        return None 