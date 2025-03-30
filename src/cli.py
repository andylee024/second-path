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
        title=f"{response.agent}'s {response.mode.capitalize()} Response",
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


def main():
    """Run the Strategic Roundtable CLI."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Strategic Roundtable Advisor")
    parser.add_argument("--memo", "-m", type=str, default="/Users/andylee/Projects/second-path/data/memo.txt", help="Path to memo file")
    parser.add_argument("--mode", type=str, choices=["introspection", "analysis"], default="introspection", help="Mode to operate in")
    parser.add_argument("--hide-reasoning", action="store_true", help="Hide agent reasoning")
    parser.add_argument("--output", "-o", type=str, help="Path to save results")
    args = parser.parse_args()
    
    # Ensure API key is set
    ensure_api_key()
    
    # Ensure data directory exists
    create_directory_if_not_exists("data")
    
    # Display welcome message
    console.print(Panel(
        "[bold blue]Strategic Roundtable Advisor[/bold blue]\n"
        "A council of expert advisors will analyze your career memo and provide insights.",
        border_style="blue"
    ))
    
    # Load the memo
    memo_text = load_memo(args.memo)
    
    # Display the memo
    display_memo(memo_text)
    
    # Confirm mode
    console.print(f"\nOperating in [bold]{args.mode}[/bold] mode.")
    if not Confirm.ask("Continue?"):
        return
    
    # Start the session
    session = RoundtableSession()
    with console.status("[bold green]Working with your career council...[/bold green]", spinner="dots"):
        results = session.start_session(memo_text, args.mode)
    
    # Display coach responses
    console.print("\n[bold]Coach Responses:[/bold]")
    for name, response in results["coaches"].items():
        display_coach_response(response, not args.hide_reasoning)
    
    # Display facilitator response
    console.print("\n[bold]Facilitator Synthesis:[/bold]")
    display_facilitator_response(results["facilitator"])
    
    # Save results if requested
    if args.output:
        save_results(results, args.output)
    elif Confirm.ask("\nWould you like to save the results?"):
        output_path = Prompt.ask("Enter output path", default="data/roundtable_results.json")
        save_results(results, output_path)


if __name__ == "__main__":
    main() 