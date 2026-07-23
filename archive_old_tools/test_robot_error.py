import os
from google import genai
from engine.db_tools import query_sqlite, query_mysql, SCHEMA_PROMPT

# Read API Key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GOOGLE_API_KEY="):
                api_key = line.split("=", 1)[1].strip()

client_gemini = genai.Client(api_key=api_key)

try:
    base_prompt = "Tugas: Kamu adalah neng Ais, AI Asisten dari Sukabumi Flasher. Kamu membantu memantau operasional toko. Jawab singkat, ramah, dan suportif layaknya asisten cerdas.\n"
    system_instruction = base_prompt + SCHEMA_PROMPT
    
    chat = client_gemini.chats.create(
        model='gemini-flash-latest',
        config={
            "tools": [query_sqlite, query_mysql],
            "system_instruction": system_instruction,
            "temperature": 0.2
        }
    )
    
    print("Sending message...")
    user_text = "Tolong cek berapa uang kas utama saat ini di database?"
    response = chat.send_message(user_text)
    print("Response text:", response.text)
    print("DONE")
except Exception as e:
    print(f"[ROBOT AIS ERROR]: {e}")
