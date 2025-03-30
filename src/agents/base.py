"""Base agent classes and response models for Strategic Roundtable."""

from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time
import json

client = OpenAI()

class AgentResponse(BaseModel):
    """Base response model for all agents."""
    agent: str
    mode: str
    output: List[str]
    reasoning: str


class IntrospectionResponse(AgentResponse):
    """Response model for introspection mode."""
    questions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of questions with reasoning"
    )


class AnalysisResponse(AgentResponse):
    """Response model for analysis mode."""
    key_insight: str
    recommendation: str
    explanation: str
    potential_barriers: List[str]


class FacilitatorResponse(BaseModel):
    """Response model for facilitator."""
    common_themes: List[str]
    key_tensions: List[str]
    synthesis: str
    next_steps: List[str]


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
        self.assistant = None
        self._initialize_assistant()
    
    def _initialize_assistant(self):
        """Initialize the OpenAI Assistant for this agent."""
        tool_schema = {
            "type": "function",
            "function": {
                "name": "provide_response",
                "description": "Provide a structured response based on the current mode",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "output": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "The main output (questions or recommendations)"
                        },
                        "reasoning": {
                            "type": "string",
                            "description": "Your reasoning behind the output"
                        }
                    },
                    "required": ["output", "reasoning"]
                }
            }
        }
        
        self.assistant = client.beta.assistants.create(
            name=self.name,
            instructions=self.system_prompt,
            model="gpt-4o",
            tools=[tool_schema]
        )
    
    def _get_mode_prompt(self, mode: str) -> str:
        """Get the appropriate prompt for the given mode."""
        from prompts.system_prompts import INTROSPECTION_MODE, ANALYSIS_MODE
        
        if mode == "introspection":
            return INTROSPECTION_MODE
        elif mode == "analysis":
            return ANALYSIS_MODE
        else:
            raise ValueError(f"Unknown mode: {mode}")
    
    def process_thread(self, thread_id: str, mode: str) -> AgentResponse:
        """Process the thread with this agent.
        
        Args:
            thread_id: The ID of the thread to process
            mode: The mode to operate in (introspection or analysis)
            
        Returns:
            The agent's response
        """
        # Add a message instructing the agent on the mode
        mode_prompt = self._get_mode_prompt(mode)
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"Please respond as {self.name} in {mode} mode.\n\n{mode_prompt}"
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
            return AgentResponse(
                agent=self.name,
                mode=mode,
                output=response_data.get("output", []),
                reasoning=response_data.get("reasoning", "")
            )
        
        # If no function calling, try to extract structured data from the message
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value
                # Basic extraction attempt
                output = []
                reasoning = ""
                
                # Very basic parsing - production code would need better handling
                if "REASONING:" in content:
                    parts = content.split("REASONING:", 1)
                    output_text = parts[0].strip()
                    reasoning = parts[1].strip() if len(parts) > 1 else ""
                    output = [line.strip() for line in output_text.split('\n') if line.strip()]
                else:
                    # Just use the whole message as output
                    output = [content]
                
                return AgentResponse(
                    agent=self.name,
                    mode=mode,
                    output=output,
                    reasoning=reasoning
                )
        
        # Fallback for any errors
        return AgentResponse(
            agent=self.name,
            mode=mode,
            output=["Failed to generate a proper response."],
            reasoning="Error in processing the thread."
        ) 