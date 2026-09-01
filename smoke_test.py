"""Smoke test GET read-only untuk route utama SF_WEB."""

from __future__ import annotations

from jinja2 import StrictUndefined
import pymysql

from app_v2 import create_app
from extensions import get_db

CORE_ROUTES = (
    "/dashboard",
    "/input_baru",
    "/preview",
    "/beban",
    "/users",
    "/engine",
    "/preview-header",
    "/preview-teknisi",
)


def main() -> int:
    app = create_app()
    app.config.update(TESTING=True, PROPAGATE_EXCEPTIONS=True)
    app.jinja_env.undefined = StrictUndefined
    client = app.test_client()

    checks = [("/", 200)]
    with client.session_transaction() as session:
        session.update(
            user="admin",
            role="admin",
            user_id=1,
            nama="Admin Smoke Test",
            permissions=["servis", "pembayaran", "tutup_buku"],
        )

    checks.extend((route, 200) for route in CORE_ROUTES)
    try:
        with app.app_context():
            row = get_db().execute("SELECT id FROM servis ORDER BY id DESC LIMIT 1").fetchone()
            service_id = row["id"] if row else None
    except pymysql.MySQLError:
        print("DATABASE_UNAVAILABLE: MySQL/MariaDB tidak dapat dihubungi.")
        return 2
    if service_id is not None:
        checks.extend(
            (route, 200)
            for route in (
                f"/detail/{service_id}",
                f"/bayar/{service_id}",
                f"/cetak_nota/{service_id}",
                f"/nota_bridge/{service_id}",
            )
        )

    failures = []
    for route, expected in checks:
        response = client.get(route)
        print(f"{route}: {response.status_code}")
        if response.status_code != expected:
            failures.append((route, response.status_code, expected))

    if failures:
        for route, actual, expected in failures:
            print(f"GAGAL {route}: mendapat {actual}, seharusnya {expected}")
        return 1
    print(f"SMOKE_GET_OK={len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())