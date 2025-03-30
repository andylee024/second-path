"""Facilitator agent implementation for the Strategic Roundtable."""

from .base import BaseAgent, FacilitatorResponse
from prompts.system_prompts import FACILITATOR_PROMPT
from openai import OpenAI
import json
import time

client = OpenAI()


class FacilitatorAgent(BaseAgent):
    """Facilitator agent implementation."""
    
    def __init__(self):
        """Initialize the facilitator agent."""
        super().__init__(
            name="Facilitator",
            system_prompt=FACILITATOR_PROMPT
        )
        # Reinitialize with facilitator-specific tools
        self._initialize_facilitator_assistant()
    
    def _initialize_facilitator_assistant(self):
        """Initialize the OpenAI Assistant with facilitator-specific tools."""
        tool_schema = {
            "type": "function",
            "function": {
                "name": "provide_synthesis",
                "description": "Provide a synthesis of the coaches' responses",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "common_themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Common themes across the coach responses"
                        },
                        "key_tensions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key tensions or contradictions between coach perspectives"
                        },
                        "synthesis": {
                            "type": "string",
                            "description": "A cohesive synthesis of the coaches' perspectives"
                        },
                        "next_steps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Suggested next steps for the user"
                        }
                    },
                    "required": ["common_themes", "key_tensions", "synthesis", "next_steps"]
                }
            }
        }
        
        self.assistant = client.beta.assistants.create(
            name=self.name,
            instructions=self.system_prompt,
            model="gpt-4o",
            tools=[tool_schema]
        )
    
    def process_thread(self, thread_id: str) -> FacilitatorResponse:
        """Process the thread with the facilitator.
        
        Args:
            thread_id: The ID of the thread to process
            
        Returns:
            The facilitator's response
        """
        # Add a message instructing the facilitator
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content="Please synthesize the coaches' responses and provide a cohesive summary."
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant.id
        )
        
        # Wait for the run to complete
        while run.status in ["queued", "in_progress"]:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
        
        # Check for function calling
        if run.status == "requires_action" and run.required_action.type == "submit_tool_outputs":
            tool_call = run.required_action.submit_tool_outputs.tool_calls[0]
            
            # Get the function call results
            response_data = json.loads(tool_call.function.arguments)
            
            # Submit the function call result
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=[{
                    "tool_call_id": tool_call.id,
                    "output": json.dumps({"status": "success"})
                }]
            )
            
            # Wait for the run to complete
            while True:
                run = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if run.status not in ["queued", "in_progress", "requires_action"]:
                    break
                time.sleep(1)
            
            # Create the response
            return FacilitatorResponse(
                common_themes=response_data.get("common_themes", []),
                key_tensions=response_data.get("key_tensions", []),
                synthesis=response_data.get("synthesis", ""),
                next_steps=response_data.get("next_steps", [])
            )
        
        # If no function calling, try to extract information from the message
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value
                
                # Very basic parsing attempt
                common_themes = []
                key_tensions = []
                synthesis = content
                next_steps = []
                
                # Extract sections if they exist
                if "COMMON THEMES:" in content:
                    themes_section = content.split("COMMON THEMES:", 1)[1].split("KEY TENSIONS:", 1)[0]
                    common_themes = [line.strip().lstrip("- ") for line in themes_section.split("\n") if line.strip()]
                
                if "KEY TENSIONS:" in content:
                    tensions_section = content.split("KEY TENSIONS:", 1)[1].split("SYNTHESIS:", 1)[0]
                    key_tensions = [line.strip().lstrip("- ") for line in tensions_section.split("\n") if line.strip()]
                
                if "SYNTHESIS:" in content:
                    synthesis = content.split("SYNTHESIS:", 1)[1].split("NEXT STEPS:", 1)[0].strip()
                
                if "NEXT STEPS:" in content:
                    steps_section = content.split("NEXT STEPS:", 1)[1]
                    next_steps = [line.strip().lstrip("- ") for line in steps_section.split("\n") if line.strip()]
                
                return FacilitatorResponse(
                    common_themes=common_themes,
                    key_tensions=key_tensions,
                    synthesis=synthesis,
                    next_steps=next_steps
                )
        
        # Fallback for any errors
        return FacilitatorResponse(
            common_themes=["Failed to extract themes"],
            key_tensions=["Failed to extract tensions"],
            synthesis="Failed to generate synthesis",
            next_steps=["Review the raw coach responses"]
        ) 