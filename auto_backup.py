"""Entrypoint backup MySQL terjadwal untuk Windows Task Scheduler."""

from __future__ import annotations

import logging
from pathlib import Path

from export_db import BACKUP_DIR, backup_database

LOG_PATH = Path(BACKUP_DIR) / "backup.log"


def main() -> int:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )
    try:
        output = backup_database(retention=15)
    except Exception:
        logging.exception("Backup database terjadwal gagal.")
        return 1
    logging.info("Backup database berhasil: %s", output.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())