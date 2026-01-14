import os
from pathlib import Path
from rich.console import Console
from src.utils.notion import get_notion_client, get_database_id, update_page_properties, fetch_page_content, fetch_linkedin_shortlisted_ideas
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

def run_insight_agent():
    """
    Main function for the Insight Agent (Angle Generator).
    """
    console.print("[bold cyan]Starting Insight Agent (Angle Generator)...[/bold cyan]")
    
    # 1. Setup Clients
    try:
        notion = get_notion_client()
        db_id = get_database_id()
        llm = get_llm_client()
    except Exception as e:
        console.print(f"[bold red]Setup failed: {e}[/bold red]")
        return

    if not llm:
         console.print("[bold red]LLM Client failed to initialize.[/bold red]")
         return

    # 2. Load Prompts and Blueprint
    blueprint = load_file_content("MASTER_BLUEPRINT.md")
    agent_prompt = load_file_content("prompts/insight_agent.md")
    
    if not blueprint or not agent_prompt:
        console.print("[red]Critical resources missing (Blueprint or Prompt).[/red]")
        return

    # 3. Fetch Linkedin Shortlisted Ideas
    ideas = fetch_linkedin_shortlisted_ideas(notion, db_id)
    if not ideas:
        console.print("No shortlisted LinkedIn ideas found to process.")
        return

    console.print(f"Found {len(ideas)} shortlisted LinkedIn ideas.")

    # Fetch Resonance Context once for all ideas
    resonance_context = get_resonance_context()

    # 4. Process Each Idea
    for page in ideas:
        page_id = page["id"]
        
        # Extract Title and Notes
        props = page.get("properties", {})
        title_prop = props.get("Content Name", {}).get("title", [])
        notes_prop = props.get("Notes", {}).get("rich_text", [])
        
        if not title_prop:
            continue
            
        idea_title = "".join([t.get("plain_text", "") for t in title_prop])
        
        # Fetch Notes (Property + Page Body)
        notes_prop_text = "".join([t.get("plain_text", "") for t in notes_prop])
        page_body_text = fetch_page_content(notion, page_id)
        
        combined_notes = f"Property Notes: {notes_prop_text}\nPage Content: {page_body_text}" if notes_prop_text else page_body_text
        
        console.print(f"Generating angles for: [italic]{idea_title}[/italic]")
        
        # 5. Generate Angles
        full_system_prompt = f"""
        {agent_prompt}
        
        *** REFERENCE MATERIAL: MASTER BLUEPRINT ***
        {blueprint}

        *** STYLE GUIDE: WINNING FORMULA ***
        {resonance_context}
        """
        
        user_input = f"""
        Topic: {idea_title}
        Input Notes:
        {combined_notes}
        """
        
        model = os.getenv("INSIGHT_MODEL", "gpt-4o")
        generated_content = generate_completion(llm, full_system_prompt + "\n\n" + user_input, model=model)
        
        if not generated_content:
            console.print(f"[red]Failed to generate angles for '{idea_title}'[/red]")
            continue
            
        console.print("[dim]Angles generated. Parsing and updating Notion...[/dim]")

        # 6. Parse and Update Notion
        # Extract Angle 1, Angle 2, Angle 3
        # Format expected: === ANGLE 1 === ... === ANGLE 2 === ... === ANGLE 3 ===
        
        angles = {"Angle 1": "", "Angle 2": "", "Angle 3": ""}
        
        try:
            if "=== ANGLE 1 ===" in generated_content:
                parts = generated_content.split("=== ANGLE 1 ===")
                if len(parts) > 1:
                    angle_1_block = parts[1].split("=== ANGLE 2 ===")[0].strip()
                    angles["Angle 1"] = angle_1_block
            
            if "=== ANGLE 2 ===" in generated_content:
                parts = generated_content.split("=== ANGLE 2 ===")
                if len(parts) > 1:
                    angle_2_block = parts[1].split("=== ANGLE 3 ===")[0].strip()
                    angles["Angle 2"] = angle_2_block
                    
            if "=== ANGLE 3 ===" in generated_content:
                parts = generated_content.split("=== ANGLE 3 ===")
                if len(parts) > 1:
                    angle_3_block = parts[1].strip()
                    angles["Angle 3"] = angle_3_block
        except Exception as parse_error:
            console.print(f"[yellow]Warning: Parsing might have been partial: {parse_error}[/yellow]")

        # Update Notion
        notion_props = {}
        for key, val in angles.items():
            if val:
                notion_props[key] = {
                    "rich_text": [{"text": {"content": val[:2000]}}]
                }
        
        if notion_props:
            # Add status update to "Insights"
            notion_props["Status"] = {"status": {"name": "Insights"}}
            try:
                update_page_properties(notion, page_id, notion_props)
                console.print(f"[green]Updated Notion angles and status for '{idea_title}'[/green]")
            except Exception as e:
                console.print(f"[red]Failed to update Notion properties: {e}[/red]")
        else:
            console.print(f"[yellow]No angles extracted for '{idea_title}'[/yellow]")

    console.print("[bold cyan]Insight Agent Completed.[/bold cyan]")
