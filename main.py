from fastapi import FastAPI, HTTPException, Depends, status, HTTPException
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import auth
from auth import get_current_user



app = FastAPI()
app.include_router(auth.router)

models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
    username: str

class ApplicationBase(BaseModel):
    job_title: str
    status: str
    user_id: int

    class Config:
        orm_mode = True #Ensure ORM objects are serialized correctly

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

#users api---------------------------------------------------
#default end point
@app.get("/",status_code=status.HTTP_200_OK)
async def user(user: user_dependency, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Authentication Failed")
    return {"User":user}

#create user
@app.post("/users/", response_model=UserBase, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


#search for user
@app.get("/users/{user_id}",status_code=status.HTTP_200_OK)
async def read_user(user_id:int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail='Customer not found')
    return user

#delete user
@app.delete("/users/{user_id}",status_code=status.HTTP_200_OK)
async def delete_user(user_id:int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    db.query(models.Application).filter(models.Application.user_id == user_id).delete()   # Delete associated applications

    db.delete(user)
    db.commit()
    return {"detail":"User deleted"}
                            



#applications api---------------------------------------------------
#create application
@app.post("/applications/", response_model=ApplicationBase, status_code=status.HTTP_201_CREATED)
async def create_application(application: ApplicationBase, db: db_dependency):
    # Check if the user exists
    user = db.query(models.User).filter(models.User.id == application.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_application = models.Application(**application.dict())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application



   
#search application
@app.get("/applications/{application_id}", status_code= status.HTTP_200_OK)
async def read_application(application_id: int, db: db_dependency):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application  not found")
    return application

#delete application
@app.delete("/application/{application_id}", status_code=status.HTTP_200_OK)
async def delete_application(application_id: int, db:db_dependency):
    application = db.query(models.Application).filter(models.Application.id == application_id).first()
    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(application)
    db.commit()
    return {"detail":"Application deleted successfully"}





   
   
