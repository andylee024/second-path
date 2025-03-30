from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
import time

class ChatSession:
    def __init__(self, advisor):
        """Initialize a chat session with the advisor."""
        self.advisor = advisor
        self.console = Console()
        
    def display_memo(self, memo_text):
        """Display the user's memo in a formatted way."""
        self.console.print(Panel(
            memo_text,
            title="Your Career Memo",
            border_style="blue"
        ))
    
    def run_chat_loop(self, memo_text, num_turns=5):
        """Run the main chat loop for a specified number of turns."""
        # Display welcome message
        self.console.print(Panel(
            "[bold blue]Welcome to 2nd Path – Ray Dalio Advisor[/bold blue]\n"
            "Ray will engage in a conversation to help develop your strategic plan.",
            border_style="blue"
        ))
        
        # Display the memo
        self.display_memo(memo_text)
        
        # Start conversation with the memo
        self.console.print("\n[bold]Starting conversation with Ray Dalio...[/bold]")
        with self.console.status("[bold green]Ray is thinking...[/bold green]", spinner="dots"):
            response = self.advisor.start_conversation(memo_text)
        self.console.print(f"\n[bold green]Ray:[/bold green] {response}")
        
        # Main conversation loop
        for turn in range(num_turns):
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "bye"]:
                self.console.print("[yellow]Ending conversation...[/yellow]")
                break
                
            # Get response from advisor
            with self.console.status("[bold green]Ray is thinking...[/bold green]", spinner="dots"):
                response = self.advisor.send_message(user_input)
            self.console.print(f"\n[bold green]Ray:[/bold green] {response}")
            
            # After several turns, ask if user wants to continue or generate plan
            if turn == num_turns - 2:  # Second to last turn
                self.console.print("\n[yellow]We'll generate your strategic plan after one more exchange.[/yellow]")
        
        return True 