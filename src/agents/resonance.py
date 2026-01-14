import os
import hashlib
import json
import time
from pathlib import Path
from rich.console import Console
from pypdf import PdfReader
from src.utils.llm import get_llm_client, generate_completion

console = Console()

CACHE_FILE = Path(".resonance_cache.json")
POSTS_DIR = Path("My posts")

def calculate_file_hash(file_path):
    """
    Calculates MD5 hash of a file efficiently.
    """
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read(65536)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(65536)
    return hasher.hexdigest()

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file.
    """
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        console.print(f"[red]Error reading PDF {file_path}: {e}[/red]")
        return ""

def load_file_content(filename):
    """
    Loads content from a file in the project directory.
    To be used for loading prompts.
    """
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent.parent
    file_path = root_dir / filename
    if not file_path.exists():
        return ""
    with open(file_path, "r") as f:
        return f.read()

def get_resonance_context(force_refresh=False):
    """
    Main entry point. Returns the "Winning Formula" theme summary.
    Checks for file updates and re-analyzes if necessary or if no cache exists.
    """
    
    # 1. Identify Target Files
    # We look for PDF files in "My posts" directory
    target_files = list(POSTS_DIR.glob("*.pdf"))
    if not target_files:
        console.print("[yellow]No PDF files found in 'My posts'. Returning empty context.[/yellow]")
        return ""

    # 2. Check Cache
    cache = {}
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r") as f:
                cache = json.load(f)
        except Exception as e:
            console.print(f"[red]Corrupt cache, resetting: {e}[/red]")

    current_state = {}
    needs_update = force_refresh
    combined_text = ""

    # 3. Detect Changes
    for file_path in target_files:
        file_hash = calculate_file_hash(file_path)
        current_state[str(file_path)] = file_hash
        
        # If this file is new or changed, we need a refresh
        if str(file_path) not in cache.get("files", {}) or cache["files"][str(file_path)] != file_hash:
            needs_update = True
            console.print(f"[yellow]Detected change in: {file_path}[/yellow]")
            
        # We need the text anyway if we are updating
        if needs_update:
            combined_text += f"\n--- FILE: {file_path.name} ---\n"
            combined_text += extract_text_from_pdf(file_path)

    # If cache exists and is valid (no needs_update), return cached theme
    if not needs_update and "theme_summary" in cache:
        # console.print("[green]Using cached Resonance Context.[/green]")
        return cache["theme_summary"]

    console.print("[bold cyan]Analyzing Resonance Files...[/bold cyan]")

    # 4. Run Analysis
    llm = get_llm_client()
    if not llm:
        console.print("[red]LLM Client not initialized.[/red]")
        return ""

    prompt_template = load_file_content("prompts/resonance_agent.md")
    if not prompt_template:
        console.print("[red]Resonance Agent Prompt not found.[/red]")
        return ""

    full_prompt = f"""
    {prompt_template}
    
    *** INPUT TEXT FROM SUCCESSFUL POSTS ***
    {combined_text[:100000]} 
    # Truncated to prevent context overflow if massive, though 100k chars is ~25k tokens. 
    # Adjust based on model limits.
    """

    # Use a high-quality model for this analysis
    model = os.getenv("RESONANCE_MODEL", "gpt-4o") 
    theme_summary = generate_completion(llm, full_prompt, model=model)

    if not theme_summary:
        console.print("[red]Failed to generate resonance summary.[/red]")
        return ""

    # 5. Update Cache
    new_cache = {
        "files": current_state,
        "theme_summary": theme_summary,
        "last_updated": time.time()
    }
    
    with open(CACHE_FILE, "w") as f:
        json.dump(new_cache, f, indent=2)

    console.print("[bold green]Resonance Analysis Updated & Cached.[/bold green]")
    return theme_summary

def run_resonance_agent():
    """
    CLI Command to manually run the agent and view the output.
    """
    console.print("[bold cyan]Running Resonance Agent...[/bold cyan]")
    context = get_resonance_context(force_refresh=False)
    console.print("\n[bold]Current Winning Formula:[/bold]\n")
    console.print(context)
