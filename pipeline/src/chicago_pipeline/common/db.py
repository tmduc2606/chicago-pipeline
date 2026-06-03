import os
from typing import Any

from sqlalchemy import create_engine, text


def get_engine() -> Any:
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "chicago")
    user = os.getenv("POSTGRES_USER", "chicago")
    password = os.getenv("POSTGRES_PASSWORD", "change_me_local")
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"
    return create_engine(url)


def check_connection() -> bool:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
