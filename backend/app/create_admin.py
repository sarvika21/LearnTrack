
from getpass import getpass
from datetime import datetime, timezone

from app.database.connection import connect_database
from app.auth.security import hash_password

def create_admin():
    db = connect_database()
    users = db["users"]

    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()

    if users.find_one({"email": email}):
        print("An account with this email already exists.")
        return

    password = getpass("Admin password (minimum 8 characters): ")

    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    confirm = getpass("Confirm password: ")

    if password != confirm:
        print("Passwords do not match.")
        return

    users.insert_one({
        "name": name,
        "email": email,
        "password_hash": hash_password(password),
        "role": "admin",
        "created_at": datetime.now(timezone.utc)
    })

    print("Admin account created successfully!")

if __name__ == "__main__":
    create_admin()  