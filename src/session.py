"""Session manager for the Strategic Roundtable."""

from agents.coach_agents import DalioAgent, WeaverAgent, NavalAgent
from agents.facilitator import FacilitatorAgent
from typing import Dict, List
from openai import OpenAI

client = OpenAI()


class RoundtableSession:
    """Interactive session manager for the Strategic Roundtable."""
    
    def __init__(self):
        self.coach_agents = {
            "Dalio": DalioAgent(),
            "Weaver": WeaverAgent(),
            "Naval": NavalAgent()
        }
        self.facilitator_agent = FacilitatorAgent()
        self.coach_threads = {}
        self.facilitator_thread = None
        self.conversation_history = []
        
    def initialize_session(self, memo_text: str):
        """Initialize a new session with the user's memo."""
        # Create threads for each agent
        for coach_name in self.coach_agents:
            self.coach_threads[coach_name] = client.beta.threads.create()
            
            # Add the memo to each coach's thread
            client.beta.threads.messages.create(
                thread_id=self.coach_threads[coach_name].id,
                role="user",
                content=f"User Memo:\n{memo_text}"
            )
        
        # Create facilitator thread
        self.facilitator_thread = client.beta.threads.create()
        
        # Add memo to facilitator thread
        client.beta.threads.messages.create(
            thread_id=self.facilitator_thread.id,
            role="user",
            content=f"User Memo:\n{memo_text}"
        )
    
    def run_introspection_turn(self):
        """Run a single turn of the introspection conversation.
        
        Returns:
            Dictionary with selected questions, prompt, and coach responses
        """
        # 1. Get questions from all coaches
        coach_responses = {}
        for coach_name, agent in self.coach_agents.items():
            print(f"Getting questions from {coach_name}...")
            coach_responses[coach_name] = agent.process_thread(
                self.coach_threads[coach_name].id, 
                "introspection"
            )
        
        # 2. Have facilitator select best questions
        print("Facilitator selecting best questions...")
        selection = self.facilitator_agent.select_best_questions(
            self.facilitator_thread.id,
            coach_responses
        )
        
        # 3. Return selection to be presented to user
        return {
            "questions": selection["selected_questions"],
            "prompt": selection["user_prompt"],
            "coach_responses": coach_responses
        }
    
    def process_user_response(self, user_response: str, asked_questions: list):
        """Process the user's response and update context for all agents.
        
        Args:
            user_response: The user's response to questions
            asked_questions: The questions that were asked
        """
        # 1. Have facilitator process the response
        context_update = self.facilitator_agent.process_user_response(
            self.facilitator_thread.id,
            user_response,
            asked_questions
        )
        
        # 2. Update all coach threads with the user's response and context
        for coach_name, thread_id in self.coach_threads.items():
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=f"User's response to previous questions:\n\n{user_response}\n\n"
                        f"Context for your next questions:\n{context_update}"
            )
        
        # 3. Add to conversation history
        self.conversation_history.append({
            "questions": asked_questions,
            "user_response": user_response
        })
    
    def get_messages(self, limit: int = 10) -> List[Dict]:
        """Get the messages from the thread.
        
        Args:
            limit: The maximum number of messages to retrieve
            
        Returns:
            A list of message dictionaries
        """
        if not self.facilitator_thread:
            return []
        
        messages = client.beta.threads.messages.list(
            thread_id=self.facilitator_thread.id,
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