"""Utilities for the Strategic Roundtable."""

import os
from rich.console import Console
import time

console = Console()

def ensure_api_key():
    """Check if OpenAI API key is set in environment."""
    if not os.environ.get("OPENAI_API_KEY"):
        console.print("[red]Error: OPENAI_API_KEY environment variable not set.[/red]")
        api_key = console.input("[yellow]Enter your OpenAI API key: [/yellow]")
        os.environ["OPENAI_API_KEY"] = api_key
        console.print("[green]API key set for this session.[/green]")

def create_directory_if_not_exists(directory):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        console.print(f"[green]Created directory: {directory}[/green]") 