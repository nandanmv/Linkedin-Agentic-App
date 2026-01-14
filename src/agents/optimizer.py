import os
from pathlib import Path
from rich.console import Console
from src.utils.notion import get_notion_client, get_database_id, fetch_drafted_ideas, update_page_properties
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

def run_optimizer():
    """
    Main function for the Draft Evaluator Agent.
    """
    console.print("[bold magenta]Starting Draft Evaluator...[/bold magenta]")
    
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

    # 2. Load Prompts
    scoring_prompt = load_file_content("prompts/scoring_agent.md")
    
    if not scoring_prompt:
        console.print("[red]Critical resources missing (Scoring Prompt).[/red]")
        return

    # 3. Fetch Drafted Ideas
    # Ideas that are 'Drafted' but maybe don't have a score yet?
    # We can filter locally if needed, but fetch_drafted_ideas gets all 'Drafted'.
    ideas = fetch_drafted_ideas(notion, db_id)
    if not ideas:
        console.print("No drafted ideas found to optimize.")
        return

    console.print(f"Found {len(ideas)} drafted ideas.")

    # 4. Process Each Idea
    for page in ideas:
        page_id = page["id"]
        
        # Check if already scored?
        props = page.get("properties", {})
        existing_score = props.get("Engagement Score", {}).get("number")
        
        if existing_score is not None:
             console.print(f"Skipping page {page_id}: Already scored ({existing_score}).")
             continue
        
        # Extract Post Draft
        post_draft_prop = props.get("Post Draft", {}).get("rich_text", [])
        if not post_draft_prop:
            console.print(f"Skipping page {page_id}: No Post Draft found.")
            continue
            
        draft_text = "".join([t.get("plain_text", "") for t in post_draft_prop])
        title_prop = props.get("Content Name", {}).get("title", [])
        title_text = "".join([t.get("plain_text", "") for t in title_prop]) if title_prop else "Untitled"

        console.print(f"Scoring draft for: [italic]{title_text}[/italic]")

        # Fetch Resonance Context
        resonance_context = get_resonance_context()

        # 5. Score Draft
        full_system_prompt = f"""
        {scoring_prompt}
        
        *** BENCHMARK: WINNING FORMULA ***
        {resonance_context}

        Score the draft based on how well it executes the specific Hook Strategies and Emotional Drivers defined above.

        ADDITIONALLY:
        Provide output in a machine parseable format at the end.
        Final Line format: JSON_RESULT: {{"score": 45, "potential": "High", "viral": "High"}}
        """
        
        user_input = f"""
        Score this LinkedIn post:
        {draft_text}
        """
        
        model = os.getenv("OPTIMIZER_MODEL", "gpt-4o")
        analysis = generate_completion(llm, full_system_prompt + "\n\n" + user_input, model=model)
        
        if not analysis:
            console.print(f"[red]Failed to score draft for '{title_text}'[/red]")
            continue
            
        # Parse Score
        score = 0
        viral_potential = "Low"
        
        import json
        import re
        
        match = re.search(r'JSON_RESULT: ({.*})', analysis)
        if match:
            try:
                data = json.loads(match.group(1))
                score = data.get("score", 0)
                viral_potential = data.get("viral", "Low")
            except:
                pass
        else:
            # Fallback parsing
            if "Overall Score:" in analysis:
                try:
                    score_line = [l for l in analysis.splitlines() if "Overall Score:" in l][0]
                    # Overall Score: 38/50
                    score_part = score_line.split(":")[1].split("/")[0].strip()
                    score = int(score_part)
                except:
                    pass
            if score >= 35:
                viral_potential = "High"
            elif score >= 25:
                viral_potential = "Moderate"

        console.print(f"Score: [bold]{score}[/bold] | Potential: {viral_potential}")

        # 6. Update Notion
        # We append the analysis to the Post Draft.
        
        # Aggressive cleaning and truncation to prevent 400 errors
        def sanitize(t):
             return "".join(c for c in str(t) if c >= " " or c in "\n\t")[:1900]
        
        clean_analysis = sanitize(analysis)
        clean_viral = sanitize(viral_potential)[:100]
        
        try:
            update_page_properties(notion, page_id, {
                "Engagement Score": {"number": int(score)},
                "Viral Potential": {
                    "rich_text": [{"text": {"content": clean_viral}}]
                },
                "Post Draft Feedback": {
                     "rich_text": [{"text": {"content": clean_analysis}}]
                }
            })
            console.print(f"Updated Notion page for '{title_text}'")
        except Exception as e:
             console.print(f"[red]Failed to update Notion: {e}[/red]")

    console.print("[bold magenta]Draft Evaluator Completed.[/bold magenta]")
