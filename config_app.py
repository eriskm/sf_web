"""Validasi konfigurasi runtime tanpa mengubah source code."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
REQUIRED_VARIABLES = (
    "FLASK_SECRET_KEY",
    "MYSQL_HOST",
    "MYSQL_USER",
    "MYSQL_DB",
)
RECOMMENDED_VARIABLES = ("MYSQL_PASSWORD", "ALLOWED_TELEGRAM_IDS")


def validate_environment():
    load_dotenv(BASE_DIR / ".env")
    missing = [name for name in REQUIRED_VARIABLES if not os.getenv(name, "").strip()]
    recommended_missing = [
        name for name in RECOMMENDED_VARIABLES if not os.getenv(name, "").strip()
    ]
    errors = []
    secret = os.getenv("FLASK_SECRET_KEY", "").strip()
    if secret and (len(secret) < 32 or secret.lower().startswith("ganti-")):
        errors.append("FLASK_SECRET_KEY harus acak dan minimal 32 karakter.")
    return missing, recommended_missing, errors


def main() -> int:
    missing, recommended_missing, errors = validate_environment()
    if missing:
        errors.append("Konfigurasi wajib belum diisi: " + ", ".join(missing))
    if errors:
        for message in errors:
            print("[ERROR] " + message)
        return 1
    print("Konfigurasi wajib tersedia.")
    if recommended_missing:
        print("[PERINGATAN] Konfigurasi yang disarankan belum diisi: " + ", ".join(recommended_missing))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())