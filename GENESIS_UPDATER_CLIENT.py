"""Updater manual SF_WEB tanpa shell command interpolation."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def run_command(command: list[str], label: str) -> bool:
    """Run a fixed argument list and show a concise result."""
    print(f"[RUNNING] {label}")
    try:
        result = subprocess.run(
            command,
            cwd=BASE_DIR,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        print(f"[ERROR] {detail.strip()}")
        return False
    if result.stdout.strip():
        print(result.stdout.strip())
    return True


def find_database_update() -> Path | None:
    candidates = (BASE_DIR / "FIX_DATABASE.py", BASE_DIR / "update SF" / "FIX_DATABASE.py")
    return next((path for path in candidates if path.is_file()), None)


def update_system(with_database: bool = False) -> int:
    print("=" * 50)
    print(" AIS GENESIS - AUTO UPDATER CLIENT ")
    print("=" * 50)

    git = shutil.which("git")
    if not git:
        print("[ERROR] Git tidak ditemukan pada PATH.")
        return 1
    if not run_command([git, "pull", "--ff-only", "origin", "main"], "git pull --ff-only origin main"):
        print("Pembaruan kode gagal; file database tidak disentuh.")
        return 1

    if with_database:
        database_script = find_database_update()
        if not database_script:
            print("[WARNING] Skrip pembaruan database tidak ditemukan; langkah dilewati.")
        elif not run_command([sys.executable, str(database_script)], database_script.name):
            return 1
    else:
        print("Pembaruan database dilewati. Gunakan --with-database hanya setelah backup diverifikasi.")

    print("Pembaruan sistem selesai. Silakan jalankan kembali app_v2.py.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Perbarui SF_WEB dari branch main.")
    parser.add_argument(
        "--with-database",
        action="store_true",
        help="Jalankan skrip pembaruan database setelah git pull berhasil.",
    )
    return update_system(with_database=parser.parse_args().with_database)


if __name__ == "__main__":
    raise SystemExit(main())