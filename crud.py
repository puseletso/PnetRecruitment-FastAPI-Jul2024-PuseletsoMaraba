from sqlalchemy.orm import Session
from . import models, schemas

def create_user(db: Session, user: schemas.UserBase):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

