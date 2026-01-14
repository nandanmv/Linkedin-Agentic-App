from dotenv import load_dotenv
load_dotenv()
from src.utils.notion import get_notion_client, get_database_id
import json

def inspect_db():
    notion = get_notion_client()
    db_id = get_database_id()
    
    # Get database schema
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = {
        "Authorization": f"Bearer {notion.options.auth}",
        "Notion-Version": "2022-06-28"
    }
    import httpx
    resp = httpx.get(url, headers=headers)
    db = resp.json()
    
    print("=== DATABASE PROPERTIES ===")
    for name, prop in db.get("properties", {}).items():
        print(f"Property: {name} | Type: {prop['type']}")

if __name__ == "__main__":
    inspect_db()
