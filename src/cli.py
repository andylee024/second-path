"""Command-line interface for the Strategic Roundtable."""

import argparse
import sys
import os
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from session import RoundtableSession
from utils import ensure_api_key, create_directory_if_not_exists

console = Console()


def display_memo(memo_text: str):
    """Display the user's memo in a formatted panel.
    
    Args:
        memo_text: The text of the user's memo
    """
    console.print(Panel(
        memo_text,
        title="Your Career Memo",
        border_style="blue"
    ))


def display_coach_response(response, show_reasoning=True):
    """Display a coach's response in a formatted panel.
    
    Args:
        response: The coach's response
        show_reasoning: Whether to show the reasoning
    """
    content = "\n".join(response.output)
    
    if show_reasoning and response.reasoning:
        content += f"\n\n[dim]Reasoning: {response.reasoning}[/dim]"
    
    console.print(Panel(
        content,
        title=f"{response.agent}'s Questions",
        border_style="green"
    ))


def display_facilitator_response(response):
    """Display the facilitator's response in a formatted panel.
    
    Args:
        response: The facilitator's response
    """
    # Create a table for common themes and tensions
    themes_table = Table(title="Key Insights")
    themes_table.add_column("Common Themes", style="green")
    themes_table.add_column("Key Tensions", style="yellow")
    
    # Fill the table with themes and tensions
    max_rows = max(len(response.common_themes), len(response.key_tensions))
    for i in range(max_rows):
        theme = response.common_themes[i] if i < len(response.common_themes) else ""
        tension = response.key_tensions[i] if i < len(response.key_tensions) else ""
        themes_table.add_row(theme, tension)
    
    # Create a panel for the synthesis
    synthesis_panel = Panel(
        response.synthesis,
        title="Synthesis",
        border_style="blue"
    )
    
    # Create a panel for next steps
    next_steps = "\n".join([f"• {step}" for step in response.next_steps])
    next_steps_panel = Panel(
        next_steps,
        title="Next Steps",
        border_style="green"
    )
    
    # Display everything
    console.print(themes_table)
    console.print(synthesis_panel)
    console.print(next_steps_panel)


def load_memo(file_path: str) -> str:
    """Load the memo from a file.
    
    Args:
        file_path: The path to the memo file
        
    Returns:
        The contents of the memo file
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        console.print(f"[red]Error: Memo file not found at {file_path}[/red]")
        sys.exit(1)


def save_results(results: Dict[str, Any], file_path: str):
    """Save the results to a file.
    
    Args:
        results: The results to save
        file_path: The path to save the results to
    """
    import json
    
    # Convert responses to dictionaries
    serializable_results = {
        "coaches": {
            name: response.dict() for name, response in results["coaches"].items()
        },
        "facilitator": results["facilitator"].dict()
    }
    
    with open(file_path, "w") as f:
        json.dump(serializable_results, f, indent=2)
    
    console.print(f"[green]Results saved to {file_path}[/green]")


def run_introspection_session(memo_text: str, max_turns=3, show_reasoning=True):
    """Run an interactive introspection session."""
    # Initialize session
    session = RoundtableSession()
    session.initialize_session(memo_text)
    
    # Display intro
    console.print(Panel(
        "Welcome to the Strategic Roundtable Introspection Session.\n"
        "Our coaches will ask you thoughtful questions to help you gain clarity.",
        title="Introspection Session",
        border_style="blue"
    ))
    
    # Run conversation turns
    for turn in range(max_turns):
        console.print(f"\n[bold]===== Turn {turn+1} of {max_turns} =====[/bold]")
        
        # Get questions for this turn
        with console.status("[bold green]Coaches are thinking...[/bold green]"):
            turn_result = session.run_introspection_turn()
        
        # Display all coach questions first
        console.print("\n[bold]All Coach Questions:[/bold]")
        for coach_name, response in turn_result["coach_responses"].items():
            display_coach_response(response, show_reasoning)
        
        # Now display the facilitator's selected questions
        console.print("\n[bold]Facilitator's Selected Questions:[/bold]")
        console.print(Panel(
            turn_result["prompt"],
            title="Facilitator",
            border_style="blue"
        ))
        
        # For each selected question
        selected_questions = []
        for q in turn_result["questions"]:
            console.print(f"[bold]{q['coach']}[/bold]: {q['question']}")
            selected_questions.append(q)
        
        # Get user response
        user_response = Prompt.ask("\n[bold cyan]Your response[/bold cyan]")
        
        # Process the response
        with console.status("[bold green]Processing your response...[/bold green]"):
            session.process_user_response(user_response, selected_questions)
        
        # Check if user wants to continue
        if turn < max_turns - 1:
            if not Confirm.ask("[yellow]Continue to next round?[/yellow]"):
                break
    
    # Final message
    console.print(Panel(
        "Thank you for participating in this introspection session.\n"
        "I hope these questions have helped you gain clarity.",
        title="Session Complete",
        border_style="green"
    ))


def main():
    """Run the Strategic Roundtable CLI."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Strategic Roundtable Advisor")
    parser.add_argument("--memo", "-m", type=str, default="/Users/andylee/Projects/second-path/data/memo.txt", help="Path to memo file")
    parser.add_argument("--hide-reasoning", action="store_true", help="Hide agent reasoning")
    parser.add_argument("--output", "-o", type=str, help="Path to save results")
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
    memo_text = load_memo(args.memo)
    
    # Display the memo
    display_memo(memo_text)
    
    # Confirm to continue
    if not Confirm.ask("\nReady to begin the introspection session?"):
        return
    
    # Run interactive introspection session
    run_introspection_session(memo_text, args.turns, not args.hide_reasoning)


if __name__ == "__main__":
    main() 