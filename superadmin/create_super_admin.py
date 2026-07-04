from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_super_admin():
    db: Session = SessionLocal()

    # Check if Super Admin already exists
    existing_user = (
        db.query(User)
        .filter(User.email == "cantechadmin@cantechnologies.co.in")
        .first()
    )

    if existing_user:
        print("Super Admin already exists.")
        return

    super_admin = User(
        name="CanTechAdmin",
        username="cantechadmin",
        email="cantechadmin@cantechnologies.co.in",
        hashed_password=pwd_context.hash("Cantechinsight@2026"),
        role="SUPER_ADMIN",
        is_active=True
    )

    db.add(super_admin)
    db.commit()

    print("Super Admin created successfully.")


if __name__ == "__main__":
    create_super_admin()