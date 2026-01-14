from dotenv import load_dotenv
load_dotenv()
from src.utils.notion import get_notion_client, get_database_id
import json

def find_shortlisted():
    notion = get_notion_client()
    db_id = get_database_id()
    
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {notion.options.auth}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    import httpx
    
    # Try searching for records with Status='Shortlisted' AND Channel='LinkedIn'
    body = {
        "filter": {
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
        },
        "page_size": 10
    }
    
    resp = httpx.post(url, headers=headers, json=body)
    data = resp.json()
    
    results = data.get("results", [])
    print(f"Found {len(results)} records with Status='Shortlisted'")
    
    if results:
        for r in results:
            props = r.get("properties", {})
            name = "".join([t.get("plain_text", "") for t in props.get("Content Name", {}).get("title", [])])
            channels = [c.get("name") for c in props.get("Channel", {}).get("multi_select", [])]
            print(f"  - {name} | Channels: {channels}")

if __name__ == "__main__":
    find_shortlisted()
