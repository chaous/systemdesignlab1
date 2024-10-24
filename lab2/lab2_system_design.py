from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional, List
import jwt
from datetime import datetime, timedelta

# Инициализация приложения
app = FastAPI()

# JWT settings
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Мастер-пользователь
MASTER_USER = {"username": "admin", "password": "secret"}

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# В памяти данные (users, projects, tasks)
users_db = {}
projects_db = {}
tasks_db = {}

# Модель пользователя
class User(BaseModel):
    username: str
    full_name: str
    email: str
    password: str

# Модель проекта
class Project(BaseModel):
    name: str
    description: Optional[str] = None
    owner: str

# Модель задачи
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    project: str
    assigned_to: Optional[str] = None

# Модель для токена
class Token(BaseModel):
    access_token: str
    token_type: str

# Функция проверки пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Создание токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Аутентификация пользователя
async def authenticate_user(username: str, password: str):
    user = users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        return False
    return user

# Получение текущего пользователя по JWT
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = users_db.get(username)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Создание мастер-пользователя
users_db[MASTER_USER["username"]] = {
    "username": MASTER_USER["username"],
    "full_name": "Administrator",
    "email": "admin@example.com",
    "password": get_password_hash(MASTER_USER["password"]),
}

# Роут для аутентификации
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Создание нового пользователя
@app.post("/users/")
async def create_user(user: User, current_user: User = Depends(get_current_user)):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    users_db[user.username] = {
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "password": get_password_hash(user.password),
    }
    return {"message": "User created successfully"}

# Поиск пользователя по логину
@app.get("/users/{username}")
async def get_user(username: str, current_user: User = Depends(get_current_user)):
    user = users_db.get(username)
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")

# Создание проекта
@app.post("/projects/")
async def create_project(project: Project, current_user: User = Depends(get_current_user)):
    projects_db[project.name] = project
    return {"message": "Project created successfully"}

# Поиск проекта по имени
@app.get("/projects/{project_name}")
async def get_project(project_name: str, current_user: User = Depends(get_current_user)):
    project = projects_db.get(project_name)
    if project:
        return project
    raise HTTPException(status_code=404, detail="Project not found")

# Создание задачи в проекте
@app.post("/tasks/")
async def create_task(task: Task, current_user: User = Depends(get_current_user)):
    if task.project not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    tasks_db[task.title] = task
    return {"message": "Task created successfully"}

# Получение всех задач проекта
@app.get("/projects/{project_name}/tasks/")
async def get_tasks(project_name: str, current_user: User = Depends(get_current_user)):
    project_tasks = [task for task in tasks_db.values() if task.project == project_name]
    return project_tasks
