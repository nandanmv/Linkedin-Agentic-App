import typer
from rich.console import Console
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = typer.Typer(help="LinkedIn Agentic Application CLI")
console = Console()

@app.command()
def evaluate():
    """
    Invokes the Idea Evaluator Agent to score new ideas in Notion.
    """
    console.print("[bold blue]Running Idea Evaluator Agent...[/bold blue]")
    # TODO: Import and run evaluator logic
    from src.agents.evaluator import run_evaluator
    run_evaluator()

@app.command()
def generate():
    """
    Invokes the Post Generator Agent to create drafts for shortlisted ideas.
    """
    console.print("[bold green]Running Post Generator Agent...[/bold green]")
    # TODO: Import and run generator logic
    from src.agents.generator import run_generator
    run_generator()

@app.command()
def optimize():
    """
    Invokes the Draft Evaluator Agent to score and optimize drafted posts.
    """
    console.print("[bold magenta]Running Draft Evaluator/Optimizer Agent...[/bold magenta]")
    # TODO: Import and run optimizer logic
    from src.agents.optimizer import run_optimizer
    run_optimizer()

@app.command()
def insight():
    """
    Invokes the Insight Agent to generate 3 high-performing angles from notions.
    """
    console.print("[bold cyan]Running Insight Agent...[/bold cyan]")
    from src.agents.insight import run_insight_agent
    run_insight_agent()

@app.command()
def all():
    """
    Runs all agents in sequence: Evaluate -> Generate -> Optimize.
    """
    console.print("[bold yellow]Running All Agents Sequence...[/bold yellow]")
    evaluate()
    generate()
    optimize()

@app.command()
def resonance():
    """
    Analyzes 'My posts' to extract and cache the 'Winning Formula'.
    """
    # TODO: Import and run resonance logic
    from src.agents.resonance import run_resonance_agent
    run_resonance_agent()

if __name__ == "__main__":
    app()
