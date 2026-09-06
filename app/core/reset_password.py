from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.models.user import User
from app.core.security import hash_password


EMAIL = "vijay@example.com"
NEW_PASSWORD = "Admin123"


db: Session = SessionLocal()

try:
    user = db.query(User).filter(User.email == EMAIL).first()

    if not user:
        print(f"User not found: {EMAIL}")
    else:
        user.hashed_password = hash_password(NEW_PASSWORD)
        db.commit()
        print(f"Password reset successfully for {EMAIL}")

finally:
    db.close()