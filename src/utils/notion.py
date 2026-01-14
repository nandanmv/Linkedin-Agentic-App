import os
from notion_client import Client
from rich.console import Console

console = Console()

def get_notion_client():
    """
    Returns an authenticated Notion client.
    """
    notion_api_key = os.getenv("NOTION_API_KEY")
    if not notion_api_key:
        console.print("[bold red]Error: NOTION_API_KEY not found in .env[/bold red]")
        raise ValueError("NOTION_API_KEY not set")
    return Client(auth=notion_api_key)

def format_uuid(id_str):
    """
    Ensures the ID is formatted as a UUID (8-4-4-4-12) and cleans URL params.
    """
    if not id_str:
        return ""
        
    # Strip URL params if present
    if "?" in id_str:
        id_str = id_str.split("?")[0]
        
    # Handle full URL input (e.g. https://notion.so/user/ID)
    if "/" in id_str:
        id_str = id_str.split("/")[-1]

    # Clean non-hex chars (just in case)
    import re
    id_str = re.sub(r'[^a-fA-F0-9]', '', id_str)

    if len(id_str) == 32:
        return f"{id_str[:8]}-{id_str[8:12]}-{id_str[12:16]}-{id_str[16:20]}-{id_str[20:]}"
        
    return id_str

def get_database_id():
    """
    Returns the Notion Database ID from environment variables.
    """
    database_id = os.getenv("NOTION_DATABASE_ID")
    if not database_id:
        console.print("[bold red]Error: NOTION_DATABASE_ID not found in .env[/bold red]")
        raise ValueError("NOTION_DATABASE_ID not set")
    
    clean_id = format_uuid(database_id)
    # console.print(f"Debug ID: {repr(clean_id)}")
    return clean_id

import httpx

def fetch_all_pages(client, database_id, filter_criteria):
    """
    Helper to fetch all pages matching a filter, handling pagination.
    """
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {client.options.auth}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    
    all_results = []
    has_more = True
    start_cursor = None
    
    while has_more:
        body = {
            "filter": filter_criteria,
            "page_size": 100
        }
        if start_cursor:
            body["start_cursor"] = start_cursor
            
        try:
            resp = httpx.post(url, headers=headers, json=body, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            
            results = data.get("results", [])
            all_results.extend(results)
            
            has_more = data.get("has_more", False)
            start_cursor = data.get("next_cursor")
            
        except Exception as e:
            console.print(f"[bold red]Notion API Error:[/bold red] {e}")
            break
            
    return all_results

def fetch_new_ideas(client, database_id):
    """
    Fetches pages with Status='New'.
    """
    return fetch_all_pages(client, database_id, {
        "property": "Status",
        "status": {
            "equals": "New"
        }
    })

def fetch_shortlisted_ideas(client, database_id):
    """
    Fetches pages with Status='Shortlisted'.
    """
    return fetch_all_pages(client, database_id, {
        "property": "Status",
        "status": {
            "equals": "Shortlisted"
        }
    })

def fetch_linkedin_shortlisted_ideas(client, database_id):
    """
    Fetches pages with Status='Shortlisted' AND Channel='Linkedin'.
    """
    return fetch_all_pages(client, database_id, {
        "and": [
            {
                "property": "Status",
                "status": {
                    "equals": "Shortlisted"
                }
            },
            {
                "property": "Channel",
                "multi_select": {
                    "contains": "LinkedIn"
                }
            }
        ]
    })

def fetch_drafted_ideas(client, database_id):
    """
    Fetches pages with Status='Drafted'.
    """
    return fetch_all_pages(client, database_id, {
        "property": "Status",
        "status": {
            "equals": "Drafted"
        }
    })

def update_page_properties(client, page_id, properties):
    """
    Updates a Notion page with the given properties.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {client.options.auth}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    try:
        resp = httpx.patch(url, headers=headers, json={"properties": properties}, timeout=30.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        console.print(f"[bold red]Notion Update Error:[/bold red] {e}")
        return None

def fetch_page_content(client, page_id):
    """
    Fetches all blocks (content) from a Notion page and extracts plain text.
    """
    try:
        blocks = client.blocks.children.list(block_id=page_id).get("results", [])
        text_content = []
        
        for block in blocks:
            # Check different block types for text content
            block_type = block.get("type", "")
            rich_text = []
            
            if block_type in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item", "numbered_list_item", "quote"]:
                rich_text = block.get(block_type, {}).get("rich_text", [])
            elif block_type == "to_do":
                rich_text = block.get("to_do", {}).get("rich_text", [])
            
            if rich_text:
                plain_text = "".join([t.get("plain_text", "") for t in rich_text])
                if plain_text.strip():
                    text_content.append(plain_text)
        
        return "\n".join(text_content)
    except Exception as e:
        console.print(f"[red]Error fetching page content for {page_id}: {e}[/red]")
        return ""

def update_page_content(client, page_id, content_text):
    """
    Appends text content to a Notion page.
    """
    # Note: Notion API appending blocks is slightly complex.
    # For now we will just use the properties for 'Post Draft' as requested in the plan.
    # If the user wants it in the page body, we can add that later.
    pass
