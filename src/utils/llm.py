import os
from openai import OpenAI
from rich.console import Console

console = Console()

def get_llm_client():
    """
    Returns an authenticated OpenAI client.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[bold red]Error: OPENAI_API_KEY not found in .env[/bold red]")
        return None # Return None to handle gracefully or raise error
    return OpenAI(api_key=api_key)

def generate_completion(client, prompt, model="gpt-4o"):
    """
    Generates a completion using the LLM.
    """
    if not client:
         raise ValueError("LLM Client not initialized")
         
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[bold red]LLM Error: {e}[/bold red]")
        return None
