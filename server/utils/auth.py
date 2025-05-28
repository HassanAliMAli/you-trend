import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from server.crud import user as user_crud
from server.utils import database
from server.models.user import User as UserModel

from server.schemas.user import TokenData

load_dotenv()

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

if not SECRET_KEY:
    SECRET_KEY = "a_very_secret_key_that_should_be_in_env_for_dev_only"
    print("Warning: SECRET_KEY not found in .env. Using a default DEVELOPMENT key. Please set a strong SECRET_KEY in your .env file for production.")
if not isinstance(ACCESS_TOKEN_EXPIRE_MINUTES, int):
    try:
        ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)
    except ValueError:
        print(f"Warning: Invalid ACCESS_TOKEN_EXPIRE_MINUTES value '{ACCESS_TOKEN_EXPIRE_MINUTES}'. Defaulting to 30 minutes.")
        ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password: str, hashed_password_db: bytes) -> bool:
    """Verifies a plain password against a hashed password from the database (stored as bytes)."""
    return pwd_context.verify(plain_password, hashed_password_db)

def get_password_hash(password: str) -> bytes:
    """Hashes a password and returns it as bytes, suitable for storing in UserModel.hashed_password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token_payload(token: str) -> Optional[dict]:
    """Decodes the token and returns the payload if valid, else None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

import bcrypt

def get_password_hash_bytes(password: str) -> bytes:
    """Hashes password using bcrypt, returns bytes, matching UserModel.set_password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password_with_bytes_hash(plain_password: str, hashed_password_bytes: bytes) -> bool:
    """Verifies plain password against a bcrypt bytes hash, matching UserModel.check_password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)

# We need to define oauth2_scheme_optional for get_current_user_optional
# This will make the Authorization header optional for endpoints using it.
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/users/token", auto_error=False)

# New function for optional user authentication
async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(database.get_db)
) -> Optional[UserModel]:
    if not token:
        return None
    try:
        payload = decode_token_payload(token)
        if payload is None:
            return None
        username: str = payload.get("sub")
        if username is None:
            return None
        user = user_crud.get_user_by_username(db, username=username)
        return user
    except Exception:
        return None 