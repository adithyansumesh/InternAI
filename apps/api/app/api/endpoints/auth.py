from fastapi import APIRouter, Depends, HTTPException, status
from supabase_client import supabase
from app.models.schemas import UserCreate, UserLogin, UserOut, Token
from app.core.config import settings
from app.core.logger import get_logger
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

router = APIRouter()
logger = get_logger(__name__)

    
def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate):
    try:
        # Check if user exists
        existing = supabase.table("users").select("id").eq("email", user.email).execute()
        if existing.data:
             raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = get_password_hash(user.password)
        
        # Insert new user with specific requested fields
        response = supabase.table("users").insert({
            "name": user.name,
            "email": user.email,
            "hashed_password": hashed_password
        }).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
            
        return {"message": "User created"}
        
    except Exception as e:
        print(f"Signup error: {e}")
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

@router.post("/login")
def login(user: UserLogin):
    try:
        response = supabase.table("users").select("*").eq("email", user.email).execute()
        db_user = response.data[0] if response.data else None
        
        if not db_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
            
        is_valid = verify_password(user.password, db_user["hashed_password"])
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
            
        return {
            "message": "Login successful",
            "user_id": db_user["id"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")
