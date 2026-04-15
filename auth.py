from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
import os
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .db import get_db
from .main import User
from .auth import hash_password, verify_password, create_access_token
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24
router = APIRouter(tags=["auth"])
templates = Jinja2Templates(directory="app/templates")


def validate_register(login, password, full_name, phone, email):
    errors = {}
    if not re.match(r"^[a-zA-Z0-9]{6,}$", login):
        errors["login"] = "Логин: латиница и цифры, не менее 6 символов"
    if len(password) < 8:
        errors["password"] = "Пароль не менее 8 символов"
    if not re.match(r"^[А-Яа-я\s]+$", full_name):
        errors["full_name"] = "ФИО: только кириллица и пробелы"
    if not re.match(r"^8\(\d{3}\)\d{3}-\d{2}-\d{2}$", phone):
        errors["phone"] = "Формат: 8(XXX)XXX-XX-XX"
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        errors["email"] = "Неверный email"
    return errors


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "errors": {}})


@router.post("/register")
def register(
        request: Request,
        login: str = Form(...),
        password: str = Form(...),
        full_name: str = Form(...),
        phone: str = Form(...),
        email: str = Form(...),
        db: Session = Depends(get_db)
):
    errors = validate_register(login, password, full_name, phone, email)
    if db.query(User).filter(User.login == login).first():
        errors["login"] = "Логин уже существует"
    if errors:
        return templates.TemplateResponse("register.html", {"request": request, "errors": errors})

    new_user = User(
        login=login,
        password_hash=hash_password(password),
        full_name=full_name,
        phone=phone,
        email=email,
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login")
def login(
        request: Request,
        login: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.login == login).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})

    token = create_access_token(data={"sub": str(user.id)})
    response = RedirectResponse(url="/applications", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response


def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None