"""Backup MySQL/MariaDB tanpa shell dan tanpa password di command line."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "backups"
load_dotenv(BASE_DIR / ".env")

MYSQLDUMP_CANDIDATES = (
    Path(r"C:\Program Files\MariaDB 12.2\bin\mysqldump.exe"),
    Path(r"C:\Program Files\MariaDB 11.4\bin\mysqldump.exe"),
    Path(r"C:\Program Files\MariaDB 11.2\bin\mysqldump.exe"),
    Path(r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"),
    Path(r"C:\xampp\mysql\bin\mysqldump.exe"),
)


def find_mysqldump() -> str | None:
    executable = shutil.which("mysqldump")
    if executable:
        return executable
    for candidate in MYSQLDUMP_CANDIDATES:
        if candidate.is_file():
            return str(candidate)
    return None


def _prune_backups(directory: Path, database: str, retention: int) -> None:
    if retention < 1:
        raise ValueError("Retention minimal satu file.")
    backups = sorted(
        directory.glob(f"backup_{database}_*.sql"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for old_path in backups[retention:]:
        old_path.unlink()


def backup_database(output_dir: Path = BACKUP_DIR, retention: int = 15) -> Path:
    """Buat dump atomik dan simpan maksimal sejumlah *retention* backup."""
    executable = find_mysqldump()
    if not executable:
        raise RuntimeError("mysqldump tidak ditemukan. Instal MySQL/MariaDB client terlebih dahulu.")

    host = os.getenv("MYSQL_HOST", "127.0.0.1")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    database = os.getenv("MYSQL_DB", "db_ais_systems")
    if not all((host, port, user, database)):
        raise RuntimeError("Konfigurasi MYSQL_HOST, MYSQL_PORT, MYSQL_USER, dan MYSQL_DB wajib diisi.")

    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = output_dir / f"backup_{database}_{timestamp}.sql"
    temporary_path = final_path.with_suffix(".sql.tmp")

    command = [
        executable,
        "--skip-ssl",
        "--single-transaction",
        "--quick",
        "--host",
        host,
        "--port",
        str(port),
        "--user",
        user,
        database,
    ]
    child_environment = os.environ.copy()
    if password:
        child_environment["MYSQL_PWD"] = password

    try:
        with temporary_path.open("wb") as output:
            result = subprocess.run(
                command,
                stdout=output,
                stderr=subprocess.PIPE,
                env=child_environment,
                check=False,
            )
        if result.returncode != 0:
            detail = result.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"mysqldump gagal (exit {result.returncode}): {detail}")
        if not temporary_path.is_file() or temporary_path.stat().st_size == 0:
            raise RuntimeError("mysqldump menghasilkan file kosong.")
        temporary_path.replace(final_path)
        _prune_backups(output_dir, database, retention)
        return final_path
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup database MySQL/MariaDB SF_WEB.")
    parser.add_argument("--check", action="store_true", help="Cek ketersediaan mysqldump saja.")
    parser.add_argument("--retention", type=int, default=15, help="Jumlah backup yang disimpan.")
    args = parser.parse_args()

    if args.check:
        executable = find_mysqldump()
        print("MYSQLDUMP_OK" if executable else "MYSQLDUMP_NOT_FOUND")
        return 0 if executable else 1

    try:
        output = backup_database(retention=args.retention)
    except Exception as exc:
        print(f"[GAGAL] Backup database: {exc}")
        return 1
    print(f"[SUKSES] Backup database dibuat: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())