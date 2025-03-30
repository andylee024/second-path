from rich.console import Console
from rich.panel import Panel
import json
from agent.dalio_assistant import StrategicPlan

def generate_and_display_plan(advisor, output_path=None):
    """Generate the strategic plan and display it."""
    console = Console()
    
    console.print("\n[bold]✅ Generating your strategic plan based on our conversation...[/bold]")
    
    # Generate the plan
    with console.status("[bold green]Ray is formulating your strategic plan...[/bold green]", spinner="dots"):
        plan = advisor.generate_strategic_plan()
    
    if not plan:
        console.print("[red]Failed to generate strategic plan.[/red]")
        return None
    
    # Display the plan
    display_strategic_plan(plan)
    
    # Save the plan if output path is provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(plan.model_dump(), f, indent=2)
        console.print(f"[green]Strategic plan saved to {output_path}[/green]")
    
    return plan

def display_strategic_plan(plan: StrategicPlan):
    """Display the strategic plan in a formatted way."""
    console = Console()
    
    console.print(Panel(
        f"[bold]Advisor:[/bold] {plan.advisor}\n\n"
        f"[bold]Desired Outcome:[/bold]\n{plan.outcome}\n\n"
        f"[bold]Rationale:[/bold]\n{plan.rationale}\n\n"
        f"[bold]Action Plan:[/bold]\n{plan.plan}\n\n"
        f"[bold]Experiments:[/bold]\n" +
        "\n".join(f"- {e}" for e in plan.experiments) + "\n\n"
        f"[bold]Uncertainties:[/bold]\n" +
        "\n".join(f"- {u}" for u in plan.uncertainties),
        title="Your Strategic Plan",
        border_style="green"
    )) 