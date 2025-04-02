"""Command-line interface for the Strategic Roundtable."""

import argparse
import sys
import os
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from session import RoundtableSession, Mode
from utils import ensure_api_key, create_directory_if_not_exists
from models import CareerMemo

console = Console()


def display_memo(memo: CareerMemo):
    """Display the user's memo in a formatted panel."""
    console.print(Panel(memo.content, title="Your Career Memo", border_style="blue"))


def run_session(memo: CareerMemo, max_turns=3):
    """Run an interactive session with both introspection and memo modes."""
    # Initialize session with memo
    session = RoundtableSession(memo)
    current_mode: Mode = "introspection"
    user_response = None
    
    # Display intro
    console.print(Panel(
        "Welcome to the Strategic Roundtable Session.\n"
        "You can switch between introspection mode (for coach questions) and memo mode (for updated drafts) at any time.",
        title="Session Start",
        border_style="blue"
    ))
    
    # Run conversation turns
    turn = 0
    while turn < max_turns:
        console.print(f"\n[bold]===== Turn {turn+1} of {max_turns} =====[/bold]")
        console.print(f"[dim]Current Mode: {current_mode.title()}[/dim]")
        
        # Get updates for this turn
        with console.status("[bold green]Processing...[/bold green]"):
            try:
                turn_result = session.run_turn(mode=current_mode, user_response=user_response)
                
                # Display current memo
                display_memo(turn_result["current_memo"])
                
                if current_mode == "introspection":
                    # Display facilitator analysis
                    console.print(Panel(
                        turn_result["facilitator_analysis"],
                        title="Facilitator's Analysis",
                        border_style="red"
                    ))
                    
                    # Display coach questions
                    for response in turn_result["coach_responses"]:
                        console.print(Panel(
                            response["questions"],
                            title=f"Questions from {response['coach']}",
                            border_style="yellow"
                        ))
                else:
                    # Display facilitator's response in memo mode
                    console.print(Panel(
                        turn_result["facilitator_response"],
                        title="Facilitator's Updated Memo",
                        border_style="green"
                    ))
            
            except Exception as e:
                console.print(f"[bold red]Error: {str(e)}[/bold red]")
                console.print("[red]Attempting to continue...[/red]")
        
        # Get user response
        user_response = Prompt.ask("\n[bold cyan]Your response[/bold cyan]")
        
        # Ask about mode switching
        if turn < max_turns - 1:
            mode_choice = Prompt.ask(
                "\n[bold yellow]What would you like to do next?[/bold yellow]",
                choices=["continue", "switch_mode", "end"],
                default="continue"
            )
            
            if mode_choice == "switch_mode":
                current_mode = "memo" if current_mode == "introspection" else "introspection"
                console.print(f"\n[green]Switched to {current_mode.title()} Mode[/green]")
            elif mode_choice == "end":
                break
        
        turn += 1
    
    # Final message
    console.print(Panel(
        "Thank you for participating in this session.\n"
        "I hope this has helped you gain clarity on your career direction.",
        title="Session Complete",
        border_style="green"
    ))


def load_memo(file_path: str) -> CareerMemo:
    """Load the memo from a file."""
    try:
        with open(file_path, "r") as f:
            content = f.read()
            # Just load the raw content without parsing
            return CareerMemo(
                content=content,
                northstar="",
                narrative="",
                problems="",
                root_cause="",
                outcomes="",
                strategy="",
                experiments=""
            )
    except FileNotFoundError:
        console.print(f"[red]Error: Memo file not found at {file_path}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error loading memo: {str(e)}[/red]")
        console.print("[yellow]Using empty memo...[/yellow]")
        return CareerMemo(
            content="",
            northstar="", narrative="", problems="", 
            root_cause="", outcomes="", strategy="", experiments=""
        )


def main():
    """Run the Strategic Roundtable CLI."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Strategic Roundtable Advisor")
    parser.add_argument("--memo", "-m", type=str, default="/Users/andylee/Projects/second-path/data/memo.txt", help="Path to memo file")
    parser.add_argument("--turns", "-t", type=int, default=3, help="Number of turns for introspection")
    args = parser.parse_args()
    
    # Ensure API key is set
    ensure_api_key()
    
    # Ensure data directory exists
    create_directory_if_not_exists("data")
    
    # Display welcome message
    console.print(Panel(
        "[bold blue]Strategic Roundtable Advisor[/bold blue]\n"
        "A council of expert advisors will help you reflect on your career memo.",
        border_style="blue"
    ))
    
    # Load the memo
    memo = load_memo(args.memo)
    
    # Display the memo
    display_memo(memo)
    
    # Confirm to continue
    if not Confirm.ask("\nReady to begin the session?"):
        return
    
    # Run interactive session
    run_session(memo, args.turns)


if __name__ == "__main__":
    main() 