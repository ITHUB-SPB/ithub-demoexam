from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from database import get_session
from models import User
from state import set_current_user, clear_current_user
import re

router = APIRouter()
templates = Jinja2Templates('templates')


@router.get('/register')
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})


@router.post('/register')
def register(
        request: Request,
        login: str = Form(...),
        password: str = Form(...),
        first_name: str = Form(...),
        last_name: str = Form(...),
        phone: str = Form(...),
        email: str = Form(...)
):
    if not re.match(r'^[a-zA-Z0-9]{6,}$', login):
        return templates.TemplateResponse("register.html",
                                          {"request": request, "error": "Логин: латиница и цифры, мин 6"})
    if len(password) < 8:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Пароль: мин 8"})
    if not re.match(r'^[а-яА-ЯёЁ]+$', first_name):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Имя: только кириллица"})
    if not re.match(r'^[а-яА-ЯёЁ]+$', last_name):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Фамилия: только кириллица"})
    if not re.match(r'^8\(\d{3}\)\d{3}-\d{2}-\d{2}$', phone):
        return templates.TemplateResponse("register.html", {"request": request, "error": "Телефон: 8(XXX)XXX-XX-XX"})

    with get_session() as session:
        existing = session.exec(select(User).where(User.login == login)).first()
        if existing:
            return templates.TemplateResponse("register.html", {"request": request, "error": "Логин занят"})

        user = User(
            login=login,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email
        )
        session.add(user)
        session.commit()

    return RedirectResponse(url="/login", status_code=303)


@router.get('/login')
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post('/login')
def login(request: Request, login: str = Form(...), password: str = Form(...)):
    with get_session() as session:
        user = session.exec(select(User).where(User.login == login)).first()
        if not user or user.password != password:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный логин или пароль"})

        set_current_user(login)

    return RedirectResponse(url="/dashboard", status_code=303)


@router.get('/logout')
def logout():
    clear_current_user()
    return RedirectResponse(url="/", status_code=303)