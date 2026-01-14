import os
from pathlib import Path
from rich.console import Console
from src.utils.notion import get_notion_client, get_database_id, fetch_new_ideas, update_page_properties, fetch_page_content
from src.utils.llm import get_llm_client, generate_completion
from src.agents.resonance import get_resonance_context

console = Console()

def load_file_content(filename):
    """
    Loads content from a file in the project directory.
    """
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent.parent
    
    file_path = root_dir / filename
    if not file_path.exists():
        console.print(f"[red]Warning: File not found: {file_path}[/red]")
        return ""
    
    with open(file_path, "r") as f:
        return f.read()

def run_evaluator():
    """
    Main function for the Idea Evaluator Agent.
    """
    console.print("[bold blue]Starting Idea Evaluator...[/bold blue]")
    
    # 1. Setup Clients
    try:
        notion = get_notion_client()
        db_id = get_database_id()
        llm = get_llm_client()
    except Exception as e:
        console.print(f"[bold red]Setup failed: {e}[/bold red]")
        return

    if not llm:
         console.print("[bold red]LLM Client failed to initialize. Check API Key.[/bold red]")
         return

    # 2. Load Prompts
    agent_prompt = load_file_content("prompts/evaluation_agent.md")
    if not agent_prompt:
        console.print("[red]Evaluation Agent Prompt not found.[/red]")
        return

    # 3. Fetch New Ideas
    ideas = fetch_new_ideas(notion, db_id)
    if not ideas:
        console.print("No new ideas found in Notion.")
        return

    console.print(f"Found {len(ideas)} new ideas to evaluate.")
    
    # Fetch Resonance Context once
    resonance_context = get_resonance_context()

    # 4. Process Each Idea
    for page in ideas:
        page_id = page["id"]
        
        # Extract Title and Notes
        props = page.get("properties", {})
        
        # Check if already scored
        existing_score = props.get("Potential Score", {}).get("number")
        if existing_score is not None:
             # console.print(f"Skipping [italic]{page_id}[/italic]: Already scored ({existing_score}).")
             continue

        title_prop = props.get("Content Name", {}).get("title", [])
        notes_prop = props.get("Notes", {}).get("rich_text", [])
        
        if not title_prop:
            console.print(f"Skipping page {page_id}: No title found.")
            continue
            
        idea_title = "".join([t.get("plain_text", "") for t in title_prop])
        notes_prop_text = "".join([t.get("plain_text", "") for t in notes_prop])
        
        # Fetch content from the page body (blocks)
        page_body_text = fetch_page_content(notion, page_id)
        
        # Combine them
        combined_notes = f"Property Notes: {notes_prop_text}\nPage Content: {page_body_text}" if notes_prop_text else page_body_text
        
        console.print(f"Evaluating: [italic]{idea_title}[/italic]")

        # 5. Evaluate with LLM
        full_system_prompt = f"""
        {agent_prompt}
        
        *** WINNING FORMULA CONTEXT ***
        {resonance_context}
        """
        
        user_input = f"""
        Topic: {idea_title}
        Input Notes:
        {combined_notes}
        """
        
        model = os.getenv("EVALUATOR_MODEL", "gpt-4o")
        score_str = generate_completion(llm, full_system_prompt + "\n" + user_input, model=model)
        
        try:
            # Try to find a number in the response if it's not a pure number
            import re
            match = re.search(r'\d+', score_str.strip())
            if match:
                score = int(match.group())
            else:
                raise ValueError("No number found in score string")
        except (ValueError, AttributeError):
            console.print(f"[red]Failed to parse score for '{idea_title}': {score_str}[/red]")
            continue

        console.print(f"Score: [bold green]{score}[/bold green]")

        # 6. Update Notion
        try:
            update_page_properties(notion, page_id, {
                "Potential Score": {"number": score}
            })
            console.print(f"Updated Notion page for '{idea_title}'")
        except Exception as e:
             console.print(f"[red]Failed to update Notion: {e}[/red]")

    console.print("[bold blue]Idea Evaluator Completed.[/bold blue]")
