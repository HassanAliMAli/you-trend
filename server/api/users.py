from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from server.utils import database, auth
from server.schemas import user as user_schema
from server.crud import user as user_crud
from server.models.user import User as UserModel # For type hinting current_user

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# Dependency to get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth.decode_token_payload(token)
    if payload is None:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception    
    user = user_crud.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@router.post("/register", response_model=user_schema.User)
def register_user(user: user_schema.UserCreate, db: Session = Depends(database.get_db)):
    db_user_by_email = user_crud.get_user_by_email(db, email=user.email)
    if db_user_by_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_user_by_username = user_crud.get_user_by_username(db, username=user.username)
    if db_user_by_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
    return user_crud.create_user(db=db, user=user)

@router.post("/token", response_model=user_schema.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = user_crud.get_user_by_username(db, username=form_data.username)
    if not user or not user.check_password(form_data.password): # Using model's check_password
    # Alternative using auth.py: not auth.verify_password_with_bytes_hash(form_data.password, user.hashed_password)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    access_token = auth.create_access_token(
        data={"sub": user.username} 
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=user_schema.User)
async def read_users_me(current_user: UserModel = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=user_schema.User)
async def update_users_me(
    user_update: user_schema.UserUpdate, 
    db: Session = Depends(database.get_db), 
    current_user: UserModel = Depends(get_current_active_user)
):
    # Check for email/username collision if they are being changed
    if user_update.email and user_update.email != current_user.email:
        existing_user = user_crud.get_user_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user.")
    if user_update.username and user_update.username != current_user.username:
        existing_user = user_crud.get_user_by_username(db, username=user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken by another user.")
            
    # Superuser status cannot be changed by user themselves via this endpoint
    if user_update.is_superuser is not None and user_update.is_superuser != current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot change superuser status.")

    # Prevent non-superusers from making themselves superusers
    if user_update.is_superuser and not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only superusers can assign superuser status.")

    # Ensure only superusers can deactivate/activate other users or change their own superuser status (handled by admin endpoint)
    # Here, user can only change their own active status if they are a superuser trying to deactivate themselves (which is odd but allowed by schema)
    # Or a regular user trying to change their API key or password etc.
    
    updated_user = user_crud.update_user(db=db, db_user=current_user, user_in=user_update)
    return updated_user

# Admin endpoint (example - can be expanded)
@router.get("/", response_model=List[user_schema.User])
def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: UserModel = Depends(get_current_active_user) # Add authorization
):
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    users = user_crud.get_users(db, skip=skip, limit=limit)
    return users

# --- New Admin User Management Endpoints ---

@router.get("/manage/{user_id}", response_model=user_schema.User)
def admin_read_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_admin: UserModel = Depends(get_current_active_user) 
):
    """Admin: Get a specific user by ID."""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this action")
    
    user = user_crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.put("/manage/{user_id}", response_model=user_schema.User)
def admin_update_user(
    user_id: int,
    user_update: user_schema.UserUpdate, # Use the existing UserUpdate schema
    db: Session = Depends(database.get_db),
    current_admin: UserModel = Depends(get_current_active_user)
):
    """Admin: Update a specific user by ID. Allows changing is_active and is_superuser."""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this action")

    db_user_to_update = user_crud.get_user(db, user_id=user_id)
    if db_user_to_update is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to update not found")

    # Prevent admin from accidentally removing their own superuser status if they are the only one?
    # This logic can be complex. For now, allow admin to change any field on any user via this endpoint.
    # If an admin updates their own record, ensure they don't lock themselves out (e.g. by making themselves inactive)
    # but this is more of an operational concern for the admin using the API.

    # Check for email/username collision if they are being changed by admin
    if user_update.email and user_update.email != db_user_to_update.email:
        existing_user = user_crud.get_user_by_email(db, email=user_update.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered by another user.")
    
    if user_update.username and user_update.username != db_user_to_update.username:
        existing_user = user_crud.get_user_by_username(db, username=user_update.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken by another user.")

    updated_user = user_crud.update_user(db=db, db_user=db_user_to_update, user_in=user_update)
    return updated_user

@router.delete("/manage/{user_id}", response_model=user_schema.User)
def admin_delete_user(
    user_id: int,
    db: Session = Depends(database.get_db),
    current_admin: UserModel = Depends(get_current_active_user)
):
    """Admin: Delete a specific user by ID."""
    if not current_admin.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this action")

    # Prevent admin from deleting themselves? 
    if current_admin.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account via this admin endpoint.")

    deleted_user = user_crud.delete_user(db, user_id=user_id)
    if deleted_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return deleted_user 