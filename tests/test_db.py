from sqlalchemy import text

from app.database.session import SessionLocal


def test_database_connection():
    db = SessionLocal()

    try:
        db.execute(text("SELECT 1"))
    finally:
        db.close()