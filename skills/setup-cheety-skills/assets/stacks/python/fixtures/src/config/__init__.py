import os

EINSTELLUNGEN = {
    "datenbank": os.environ.get("DATABASE_URL", ""),
    "frist_tage": 14,
}
