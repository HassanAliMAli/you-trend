import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status

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
    # bcrypt expects the hashed password to be bytes.
    # Our UserModel.hashed_password is LargeBinary, so it comes as bytes from DB.
    return pwd_context.verify(plain_password, hashed_password_db)

def get_password_hash(password: str) -> bytes:
    """Hashes a password and returns it as bytes, suitable for storing in UserModel.hashed_password."""
    # pwd_context.hash returns a str. bcrypt.hashpw (used in UserModel) returns bytes.
    # To be consistent with UserModel.set_password and how verify_password expects bytes:
    # We should ensure this function returns bytes if it's to be the primary hashing mechanism.
    # However, passlib's verify typically works with the string hash it produces.
    # Let's stick to passlib's string hash for now and adjust UserModel if necessary, or adjust verify_password.
    # For now, let's make this consistent with passlib's typical output (str)
    return pwd_context.hash(password) # Returns str

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

# Consider adjusting UserModel.set_password to use get_password_hash (str output) from here,
# and UserModel.check_password to use verify_password (str input for hash) from here for consistency.
# Or, adjust get_password_hash here to return bytes and verify_password to expect bytes, 
# aligning with current UserModel methods that use bcrypt directly.

# For now, UserModel methods (set_password, check_password) use bcrypt directly producing/expecting bytes.
# This auth.py uses passlib which can wrap bcrypt. verify_password needs to handle bytes from DB.
# get_password_hash here produces a string (passlib format). This is a slight mismatch.

# Let's refine get_password_hash to return bytes to match the User model's direct bcrypt usage for now.
# And ensure verify_password correctly handles bytes from the DB.

import bcrypt # Re-import for direct use if matching User model closely

def get_password_hash_bytes(password: str) -> bytes:
    """Hashes password using bcrypt, returns bytes, matching UserModel.set_password."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def verify_password_with_bytes_hash(plain_password: str, hashed_password_bytes: bytes) -> bool:
    """Verifies plain password against a bcrypt bytes hash, matching UserModel.check_password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password_bytes)

# We will use get_password_hash_bytes and verify_password_with_bytes_hash for direct use with the User model
# This keeps consistency with the existing User model methods.

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
        # Do not raise an error if user is not found or token is invalid, just return None
        return user
    except Exception:
        # Any exception during token processing means optional auth fails silently
        return None

# We need to define oauth2_scheme_optional for get_current_user_optional
# This will make the Authorization header optional for endpoints using it.
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/users/token", auto_error=False)

# Need to import UserModel, Session, Depends, user_crud, database for the new function
from sqlalchemy.orm import Session
from server.crud import user as user_crud
from server.utils import database
from server.models.user import User as UserModel 