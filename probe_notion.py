from dotenv import load_dotenv
load_dotenv()
from src.utils.notion import get_notion_client, update_page_properties
import httpx

def probe():
    notion = get_notion_client()
    page_id = "2e513529-6404-8023-8892-f2b1398bfd7a"
    
    fields = {
        "Engagement Score": {"number": 10},
        "Viral Potential": {"rich_text": [{"text": {"content": "Test"}}]},
        "Post Draft": {"rich_text": [{"text": {"content": "Test"}}]},
        "Status": {"status": {"name": "Drafted"}}
    }
    
    for name, payload in fields.items():
        print(f"Testing field: {name}...")
        res = update_page_properties(notion, page_id, {name: payload})
        if res:
            print(f"  SUCCESS: {name}")
        else:
            print(f"  FAILED: {name}")

if __name__ == "__main__":
    probe()
