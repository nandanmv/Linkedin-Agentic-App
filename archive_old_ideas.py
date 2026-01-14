import os
from rich.console import Console
from dotenv import load_dotenv
from src.utils.notion import get_notion_client, get_database_id, fetch_all_pages, update_page_properties

# Load environment variables
load_dotenv()

console = Console()

def archive_old_status():
    """
    Fetches ideas with status 'Old' and updates them to 'Archived'.
    """
    console.print("[bold yellow]Starting Status Archival (Old -> Archived)...[/bold yellow]")

    # 1. Setup Clients
    try:
        notion = get_notion_client()
        db_id = get_database_id()
    except Exception as e:
        console.print(f"[bold red]Setup failed: {e}[/bold red]")
        return

    # 2. Fetch Pages with Status = "Old"
    filter_criteria = {
        "property": "Status",
        "status": {
            "equals": "Old"
        }
    }

    try:
        ideas = fetch_all_pages(notion, db_id, filter_criteria)
    except Exception as e:
         console.print(f"[bold red]Failed to fetch pages: {e}[/bold red]")
         return

    if not ideas:
        console.print("No pages found with status 'Old'.")
        return

    console.print(f"Found {len(ideas)} pages to archive.")

    # 3. Process Each Page
    for page in ideas:
        page_id = page["id"]
        props = page.get("properties", {})
        title_prop = props.get("Content Name", {}).get("title", [])
        title_text = "".join([t.get("plain_text", "") for t in title_prop]) if title_prop else "Untitled"
        
        console.print(f"Archiving: [italic]{title_text}[/italic]")

        # 4. Update Status to "Archived"
        try:
            update_page_properties(notion, page_id, {
                "Status": {"status": {"name": "Archived"}}
            })
            console.print(f"[green]✓ Updated status to 'Archived'[/green]")
        except Exception as e:
             console.print(f"[red]✗ Failed to update: {e}[/red]")

    console.print("[bold green]Archival Process Completed.[/bold green]")

if __name__ == "__main__":
    archive_old_status()
