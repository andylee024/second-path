"""Base agent class for Strategic Roundtable."""

from openai import OpenAI
import time

client = OpenAI()

class BaseAgent:
    """Base class for all strategic roundtable agents."""
    
    def __init__(self, name: str, system_prompt: str):
        """Initialize a new agent.
        
        Args:
            name: The name of the agent
            system_prompt: The system prompt for the agent
        """
        self.name = name
        self.system_prompt = system_prompt
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
        
        # Create a run
        run = client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )
        
        # Wait for completion
        while True:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            
            if run.status == "completed":
                # Get the last message from the assistant
                messages = client.beta.threads.messages.list(
                    thread_id=self.thread.id,
                    order="desc",
                    limit=1
                )
                
                if messages.data and messages.data[0].role == "assistant":
                    if hasattr(messages.data[0].content[0], 'text'):
                        return messages.data[0].content[0].text.value
                    else:
                        return "Error: Response has no text content"
                else:
                    return "No response from assistant"
            
            elif run.status == "requires_action":
                # Handle function calls by submitting empty outputs
                tool_calls = run.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    # Add a tool output with an empty result
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": "{\"result\": \"success\"}"
                    })
                
                # Submit the empty outputs
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                
                # Continue waiting
                continue
            
            elif run.status in ["failed", "expired", "cancelled"]:
                return f"Error: Run failed with status {run.status}"
            
            # Still in progress
            elif run.status in ["queued", "in_progress"]:
                continue
            
            # Unknown status
            else:
                return f"Error: Unknown run status {run.status}" 