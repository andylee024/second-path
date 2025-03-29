import json
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from engine import AgentEngine
from agents.base import Strategy

console = Console()

def display_memo(memo: Dict[str, Any]):
    """Display the user's memo in a formatted way."""
    console.print(Panel(
        f"[bold]Name:[/bold] {memo['name']}\n"
        f"[bold]Background:[/bold] {memo['background']}\n"
        f"[bold]Goal:[/bold] {memo['goal']}\n"
        f"[bold]Uncertainties:[/bold]\n" + 
        "\n".join(f"- {u}" for u in memo['uncertainties']) + "\n"
        f"[bold]Energy Signals:[/bold]\n" +
        "\n".join(f"- {s}" for s in memo['energy_signals']),
        title="Your Career Memo",
        border_style="blue"
    ))

def display_strategy(strategy: Strategy):
    """Display a strategy in a formatted way."""
    console.print(Panel(
        f"[bold]Advisor:[/bold] {strategy.advisor}\n"
        f"[bold]Desired Outcome:[/bold] {strategy.outcome}\n"
        f"[bold]Rationale:[/bold] {strategy.rationale}\n"
        f"[bold]Action Plan:[/bold] {strategy.plan}\n"
        f"[bold]Experiments:[/bold]\n" +
        "\n".join(f"- {e}" for e in strategy.experiments) + "\n"
        f"[bold]Uncertainties:[/bold]\n" +
        "\n".join(f"- {u}" for u in strategy.uncertainties),
        title=f"{strategy.advisor}'s Strategy",
        border_style="green"
    ))

def main():
    # Load the memo
    try:
        with open("data/memo.json", "r") as f:
            memo = json.load(f)
    except FileNotFoundError:
        console.print("[red]Error: memo.json not found in data directory[/red]")
        return

    # Initialize the engine
    engine = AgentEngine()

    # Display welcome message
    console.print(Panel(
        "[bold blue]Welcome to 2nd Path – Strategic Council[/bold blue]\n"
        "Your advisors will analyze your memo and provide strategic recommendations.",
        border_style="blue"
    ))

    # Display the memo
    display_memo(memo)

    # Generate strategies
    console.print("\n[bold]Generating strategies from your advisors...[/bold]")
    strategies = engine.generate_all_strategies(memo)

    # Review and accept/reject strategies
    accepted_strategies = {}
    for name, strategy in strategies.items():
        display_strategy(strategy)
        response = Prompt.ask(
            f"\nDo you want to accept {name}'s strategy?",
            choices=["y", "n", "tweak"],
            default="n"
        )
        
        if response == "y":
            accepted_strategies[name] = strategy
        elif response == "tweak":
            # TODO: Implement strategy tweaking
            console.print("[yellow]Strategy tweaking not yet implemented[/yellow]")
            if Confirm.ask("Accept the original strategy?"):
                accepted_strategies[name] = strategy

    # Combine accepted strategies
    if accepted_strategies:
        console.print("\n[bold]Generating composite strategy...[/bold]")
        composite = engine.combine_strategies(accepted_strategies)
        display_strategy(composite)
        
        # Save the composite strategy
        with open("data/composite_strategy.json", "w") as f:
            json.dump(composite.dict(), f, indent=2)
        console.print("[green]Composite strategy saved to data/composite_strategy.json[/green]")
    else:
        console.print("[red]No strategies were accepted. No composite strategy generated.[/red]")

if __name__ == "__main__":
    main() 