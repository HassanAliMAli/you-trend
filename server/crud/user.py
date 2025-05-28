from sqlalchemy.orm import Session
from server.models.user import User as UserModel
from server.schemas.user import UserCreate, UserUpdate

def get_user(db: Session, user_id: int):
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(UserModel).filter(UserModel.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(UserModel).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    db_user = UserModel(
        email=user.email,
        username=user.username,
        full_name=user.full_name
    )
    db_user.set_password(user.password) # Hashing the password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: UserModel, user_in: UserUpdate):
    update_data = user_in.dict(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        db_user.set_password(update_data["password"])
        del update_data["password"] # Don't try to set it directly

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return db_user
    return None 