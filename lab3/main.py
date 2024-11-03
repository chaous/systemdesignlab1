from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import List, Optional
from datetime import datetime, timedelta

# Настройка приложения
app = FastAPI()

# Конфигурация базы данных
DATABASE_URL = "postgresql://user:password@localhost/project_management"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Настройка JWT
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модели базы данных
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    full_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    project_id = Column(Integer, ForeignKey("projects.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))

# Создание таблиц
Base.metadata.create_all(bind=engine)

# Схемы запросов и ответов
class UserCreate(BaseModel):
    username: str
    full_name: str
    email: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    project_id: int
    assigned_to: Optional[int] = None

# Функции для работы с базой данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршруты и логика API
@app.post("/users/", response_model=dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, full_name=user.full_name, email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

@app.post("/projects/", response_model=dict)
def create_project(project: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_project = Project(name=project.name, description=project.description, owner_id=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return {"message": "Project created successfully"}

@app.post("/tasks/", response_model=dict)
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_task = Task(title=task.title, description=task.description, project_id=task.project_id, assigned_to=task.assigned_to)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return {"message": "Task created successfully"}

# Функции аутентификации и другие маршруты можно реализовать аналогично.
