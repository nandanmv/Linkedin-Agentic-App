import os
from pathlib import Path
from rich.console import Console
from src.utils.notion import get_notion_client, get_database_id, fetch_shortlisted_ideas, update_page_properties
from src.utils.llm import get_llm_client, generate_completion
from src.agents.resonance import get_resonance_context

console = Console()

def load_file_content(filename):
    """
    Loads content from a file in the project directory.
    """
    # Assuming main.py is in the root, and we are running from root.
    # We can also search relative to this file.
    # Current file is src/agents/generator.py
    # Root is ../../
    
    current_dir = Path(__file__).parent
    root_dir = current_dir.parent.parent
    
    file_path = root_dir / filename
    if not file_path.exists():
        console.print(f"[red]Warning: File not found: {file_path}[/red]")
        return ""
    
    with open(file_path, "r") as f:
        return f.read()

def run_generator():
    """
    Main function for the Post Generator Agent.
    """
    console.print("[bold green]Starting Post Generator...[/bold green]")
    
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
    agent_prompt = load_file_content("prompts/generation_agent.md")
    
    if not blueprint or not agent_prompt:
        console.print("[red]Critical resources missing (Blueprint or Prompt).[/red]")
        return

    # 3. Fetch Shortlisted Ideas
    ideas = fetch_shortlisted_ideas(notion, db_id)
    if not ideas:
        console.print("No shortlisted ideas found to generate.")
        return

    console.print(f"Found {len(ideas)} shortlisted ideas.")

    # 4. Process Each Idea
    for page in ideas:
        page_id = page["id"]
        
        # Extract Title and Notes
        props = page.get("properties", {})
        title_prop = props.get("Content Name", {}).get("title", [])
        notes_prop = props.get("Notes", {}).get("rich_text", [])
        
        if not title_prop:
            continue
            
        idea_text = "".join([t.get("plain_text", "") for t in title_prop])
        
        # 4. Fetch Notes (Property + Page Body)
        # Existing property-based notes
        notes_prop_text = "".join([t.get("plain_text", "") for t in notes_prop])
        
        # New: Fetch content from the page body (blocks)
        from src.utils.notion import fetch_page_content
        page_body_text = fetch_page_content(notion, page_id)
        
        # Combine them
        notes_text = f"Property Notes: {notes_prop_text}\nPage Content: {page_body_text}" if notes_prop_text else page_body_text
        
        console.print(f"Generating post for: [italic]{idea_text}[/italic]")
        
        # Fetch Resonance Context
        resonance_context = get_resonance_context()

        # 5. Generate Post
        full_system_prompt = f"""
        {agent_prompt}
        
        *** REFERENCE MATERIAL: MASTER BLUEPRINT ***
        {blueprint}

        *** STYLE GUIDE: WINNING FORMULA ***
        {resonance_context}

        Ensure the generated post strictly mimics one of the Discovered Archetypes and uses a proven Hook Strategy from the context above.
        """
        
        user_input = f"""
        Generate a LinkedIn post from these rough notes:
        Topic: {idea_text}
        Notes: {notes_text}
        """
        
        model = os.getenv("GENERATOR_MODEL", "gpt-4o")
        generated_content = generate_completion(llm, full_system_prompt + "\n\n" + user_input, model=model)
        
        if not generated_content:
            console.print(f"[red]Failed to generate content for '{idea_text}'[/red]")
            continue
            
        console.print("[dim]Content generated.[/dim]")

        # 6. Update Notion
        # We need to extract the raw post text if possible, but the prompt returns metadata too.
        # Ideally we'd parse it, but for now we'll store the whole thing or just the text.
        # The prompt says: "Your Output: === GENERATED LINKEDIN POST === ... "
        # We can try to extract just the post part.
        
        post_draft = generated_content
        if "=== GENERATED LINKEDIN POST ===" in generated_content:
            parts = generated_content.split("=== GENERATED LINKEDIN POST ===")
            if len(parts) > 1:
                # typically follows by === POST METADATA ===
                post_part = parts[1].split("=== POST METADATA ===")[0]
                post_draft = post_part.strip()
        
        try:
            update_page_properties(notion, page_id, {
                "Post Draft": {
                    "rich_text": [
                        {"text": {"content": post_draft[:2000]}} # Notion limit 2000 chars per block usually, but rich_text property can hold more? 
                        # Actually rich_text property limit is 2000 characters per text object. If longer, need to split.
                        # For simplicity, let's truncate or split.
                    ]
                },
                "Status": {"status": {"name": "Drafted"}}
            })
            console.print(f"Updated Notion page for '{idea_text}' -> Drafted")
        except Exception as e:
             console.print(f"[red]Failed to update Notion: {e}[/red]")

    console.print("[bold green]Post Generator Completed.[/bold green]")
