from dotenv import load_dotenv
load_dotenv()
from src.utils.notion import get_notion_client, get_database_id
import json

def get_db_schema():
    notion = get_notion_client()
    db_id = get_database_id()
    
    url = f"https://api.notion.com/v1/databases/{db_id}"
    headers = {
        "Authorization": f"Bearer {notion.options.auth}",
        "Notion-Version": "2022-06-28"
    }
    import httpx
    resp = httpx.get(url, headers=headers)
    db = resp.json()
    
    status_property = db.get("properties", {}).get("Status", {})
    print(json.dumps(status_property, indent=2))

if __name__ == "__main__":
    get_db_schema()
