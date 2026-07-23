import os
from google import genai

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    # Read from .env
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY="):
                api_key = line.split("=", 1)[1].strip()

client = genai.Client(api_key=api_key)

def query_sqlite(sql: str) -> str:
    """Run SELECT on SQLite and return results."""
    return f"SIMULATED RESULTS FOR: {sql}"

try:
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config={
            "tools": [query_sqlite],
            "system_instruction": "You are a helpful assistant. Use tools if necessary.",
        }
    )
    res = chat.send_message("What is in the table users? Execute a query to find out.")
    print("Response text:", res.text)
    print("Function calls (if any):", res.function_calls)
except Exception as e:
    print(f"Error: {e}")
