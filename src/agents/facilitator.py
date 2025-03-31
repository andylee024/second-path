"""Facilitator agent implementation for the Strategic Roundtable."""

from .base import BaseAgent, FacilitatorResponse
from prompts.system_prompts import FACILITATOR_PROMPT
from openai import OpenAI
import json
import time

client = OpenAI()


class FacilitatorAgent(BaseAgent):
    """Facilitator agent for managing the introspection dialogue."""
    
    def __init__(self):
        """Initialize the facilitator agent."""
        super().__init__(
            name="Facilitator",
            system_prompt=FACILITATOR_PROMPT
        )
        # Reinitialize with facilitator-specific tools
        self._initialize_facilitator_assistant()
    
    def _initialize_facilitator_assistant(self):
        """Initialize with tools for managing introspection dialogue."""
        select_questions_schema = {
            "type": "function",
            "function": {
                "name": "select_questions",
                "description": "Select the most relevant questions to ask the user",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "selected_questions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "question": {"type": "string"},
                                    "coach": {"type": "string"},
                                    "reasoning": {"type": "string"}
                                }
                            },
                            "description": "1-2 selected questions from coaches"
                        },
                        "user_prompt": {
                            "type": "string",
                            "description": "An empathetic message to present questions to the user"
                        },
                        "selection_rationale": {
                            "type": "string",
                            "description": "Why these questions were selected"
                        }
                    },
                    "required": ["selected_questions", "user_prompt", "selection_rationale"]
                }
            }
        }
        
        process_response_schema = {
            "type": "function",
            "function": {
                "name": "process_user_response",
                "description": "Process the user's response to questions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "insights": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Key insights from the user's response"
                        },
                        "guidance": {
                            "type": "string",
                            "description": "Guidance for coaches on what to ask next"
                        },
                        "areas_to_explore": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Areas that should be explored further"
                        }
                    },
                    "required": ["guidance"]
                }
            }
        }
        
        synthesis_schema = {
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
            tools=[select_questions_schema, process_response_schema, synthesis_schema]
        )
    
    def select_best_questions(self, thread_id: str, coach_questions: dict) -> dict:
        """Select the best 1-2 questions from coaches to ask the user.
        
        Args:
            thread_id: The ID of the facilitator thread
            coach_questions: Dictionary of coach names to their questions
            
        Returns:
            Dictionary with selected questions and user prompt
        """
        # Add all coach questions to the thread
        question_content = "Here are the questions from each coach:\n\n"
        
        for coach_name, response in coach_questions.items():
            question_content += f"### {coach_name}'s Questions:\n"
            for output in response.output:
                question_content += f"- {output}\n"
            question_content += f"Reasoning: {response.reasoning}\n\n"
        
        # Add instruction to select best questions
        question_content += "\n\nPlease select 1-2 most relevant questions for the user based on their context and current needs."
        
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question_content
        )
        
        # Run the assistant to select questions
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
            
            # Return the selected questions and prompt
            return {
                "selected_questions": response_data.get("selected_questions", []),
                "user_prompt": response_data.get("user_prompt", "Please reflect on these questions:"),
                "selection_rationale": response_data.get("selection_rationale", "")
            }
        
        # If function calling fails, try basic message extraction
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        
        # Fallback implementation if function calling doesn't work
        for message in messages.data:
            if message.role == "assistant":
                content = message.content[0].text.value
                
                # Extract questions using simple parsing
                selected_questions = []
                user_prompt = "Please reflect on these questions:"
                selection_rationale = "These questions were selected based on relevance to your situation."
                
                # Very basic parsing attempt
                if "SELECTED QUESTIONS:" in content:
                    questions_section = content.split("SELECTED QUESTIONS:", 1)[1].split("USER PROMPT:", 1)[0]
                    lines = [line.strip() for line in questions_section.split('\n') if line.strip()]
                    
                    for line in lines:
                        if line.startswith("-") or line.startswith("*"):
                            parts = line[1:].strip().split("(", 1)
                            if len(parts) > 1:
                                question = parts[0].strip()
                                coach = parts[1].split(")", 1)[0].strip()
                                selected_questions.append({
                                    "question": question,
                                    "coach": coach,
                                    "reasoning": "Selected by facilitator"
                                })
                
                if "USER PROMPT:" in content:
                    user_prompt = content.split("USER PROMPT:", 1)[1].split("RATIONALE:", 1)[0].strip()
                
                if "RATIONALE:" in content:
                    selection_rationale = content.split("RATIONALE:", 1)[1].strip()
                
                return {
                    "selected_questions": selected_questions,
                    "user_prompt": user_prompt,
                    "selection_rationale": selection_rationale
                }
        
        # Last resort fallback
        return {
            "selected_questions": [
                {
                    "question": "What aspects of your memo would you like to explore further?",
                    "coach": "Facilitator",
                    "reasoning": "General exploration question"
                }
            ],
            "user_prompt": "It seems our coaches have some thoughts to share. What aspects of your situation would you like to explore further?",
            "selection_rationale": "Fallback question when coach selection process fails"
        }
    
    def process_user_response(self, thread_id: str, user_response: str, 
                             selected_questions: list) -> str:
        """Process the user's response and prepare context for coaches.
        
        Args:
            thread_id: The ID of the facilitator thread
            user_response: The user's response to questions
            selected_questions: The questions that were asked
            
        Returns:
            Context update for coaches
        """
        # Add user response to thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"User has responded to the questions:\n\n{user_response}\n\nPlease analyze this response and provide context that would help coaches ask better follow-up questions."
        )
        
        # Run the assistant to analyze response
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
            
            # Format the guidance
            guidance = response_data.get("guidance", "")
            insights = response_data.get("insights", [])
            areas_to_explore = response_data.get("areas_to_explore", [])
            
            formatted_guidance = f"GUIDANCE FOR NEXT QUESTIONS:\n{guidance}\n\n"
            
            if insights:
                formatted_guidance += "KEY INSIGHTS FROM USER:\n"
                for insight in insights:
                    formatted_guidance += f"- {insight}\n"
                formatted_guidance += "\n"
            
            if areas_to_explore:
                formatted_guidance += "AREAS TO EXPLORE FURTHER:\n"
                for area in areas_to_explore:
                    formatted_guidance += f"- {area}\n"
            
            return formatted_guidance
        
        # Get the assistant's analysis
        messages = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc",
            limit=1
        )
        
        for message in messages.data:
            if message.role == "assistant":
                return message.content[0].text.value
        
        # Fallback if analysis fails
        return f"The user responded to the following questions: {', '.join([q['question'] for q in selected_questions])}. Please provide follow-up questions that build on their response."
    
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