
from datetime import datetime, timezone

from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from pydantic import BaseModel, EmailStr, Field
from fastapi import APIRouter, HTTPException, Depends

from app.database.connection import get_database
from app.auth.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def public_user(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }

@router.post("/register")
def register(data: RegisterRequest):
    db = get_database()
    users = db["users"]

    email = str(data.email).strip().lower()

    if users.find_one({"email": email}):
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists"
        )

    user = {
        "name": data.name.strip(),
        "email": email,
        "password_hash": hash_password(data.password),
        "role": "student",
        "created_at": datetime.now(timezone.utc)
    }

    try:
        result = users.insert_one(user)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists"
        )

    user["_id"] = result.inserted_id

    token = create_access_token(str(result.inserted_id), "student")

    return {
        "message": "Student registered successfully",
        "access_token": token,
        "token_type": "bearer",
        "user": public_user(user)
    }

@router.post("/login")
def login(data: LoginRequest):
    db = get_database()
    users = db["users"]

    email = str(data.email).strip().lower()
    user = users.find_one({"email": email})

    if not user or not verify_password(
        data.password,
        user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )

    token = create_access_token(
        str(user["_id"]),
        user["role"]
    )

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": public_user(user)
    }

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    db = get_database()

    try:
        user = db["users"].find_one(
            {"_id": ObjectId(current_user["user_id"])}
        )
    except Exception:
        user = None

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": public_user(user)}