"""Asisten terminal lokal berbasis Ollama, tanpa eksekusi perintah sistem."""

from __future__ import annotations

import os

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434/api/generate")
MODEL_NAME = os.getenv("OLLAMA_ASSISTANT_MODEL", "qwen2.5:1.5b")
MAX_PROMPT_LENGTH = 2_000


def nanya_ollama(prompt: str) -> str:
    """Kirim pertanyaan ke model lokal dan kembalikan jawaban teks saja."""
    question = (prompt or "").strip()
    if not question:
        return "Pertanyaan masih kosong."
    if len(question) > MAX_PROMPT_LENGTH:
        return f"Pertanyaan terlalu panjang (maksimal {MAX_PROMPT_LENGTH} karakter)."

    system_prompt = (
        "Anda adalah asisten operasional Sukabumi Flasher. "
        "Jawab dalam Bahasa Indonesia secara ringkas dan aman. "
        "Jangan menghasilkan atau menjalankan perintah shell, PowerShell, SQL mutasi, "
        "atau instruksi yang dapat mengubah sistem."
    )
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{system_prompt}\n\nPengguna: {question}\nAsisten:",
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=(5, 60))
        response.raise_for_status()
        answer = str(response.json().get("response") or "").strip()
        return answer or "Model lokal tidak mengembalikan jawaban."
    except (requests.RequestException, ValueError):
        return "Asisten lokal tidak dapat dihubungi. Pastikan Ollama sedang berjalan."


def main() -> None:
    print("=" * 50)
    print(" ASISTEN LOKAL SUKABUMI (MODE CHAT AMAN) ")
    print("=" * 50)
    print(f"Menggunakan model: {MODEL_NAME}")
    print("Asisten ini tidak dapat menjalankan perintah sistem.")
    print("Ketik 'keluar' untuk berhenti.\n")

    while True:
        try:
            user_input = input("Tanya apa, Bro? > ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if user_input.strip().lower() in {"keluar", "exit", "quit"}:
            break
        if user_input.strip():
            print(nanya_ollama(user_input))


if __name__ == "__main__":
    main()