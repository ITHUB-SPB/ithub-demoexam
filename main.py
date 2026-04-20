from datetime import date, datetime
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlmodel import select

from database import get_session, init_db
from models import Application, User
from state import get_current_user
from routers import auth

init_db()

with get_session() as session:
    admin = session.exec(select(User).where(User.login == "Admin")).first()
    if not admin:
        admin = User(
            login="Admin",
            password="KorokNET",
            first_name="Администратор",
            last_name="Системы",
            phone="8(921)185-33-90",
            email="admin@gmail.com.net",
            role="admin"
        )
        session.add(admin)
        session.commit()

app = FastAPI(debug=True)
templates = Jinja2Templates('templates')
static = StaticFiles(directory='./static')
app.mount('/static', static)

app.include_router(auth.router)

COURSES = [
    "Основы алгоритмизации и программирования",
    "Основы веб-дизайна",
    "Основы проектирования баз данных"
]

@app.get('/')
def index(request: Request):
    user = get_current_user()
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/dashboard')
def dashboard(request: Request):
    user = get_current_user()
    if not user:
        return RedirectResponse(url="/login")

    with get_session() as session:
        applications = session.exec(
            select(Application).where(Application.user_id == user.id)
        ).all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user,
        "applications": applications
    })

@app.get('/request')
def request_form(request: Request):
    user = get_current_user()
    if not user:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse("request.html", {
        "request": request,
        "courses": COURSES,
        "user": user,
        "error": None
    })

@app.post('/request')
def create_request(
    request: Request,
    course_name: str = Form(...),
    start_date: str = Form(...),
    payment_method: str = Form(...)
):
    user = get_current_user()
    if not user:
        return RedirectResponse(url="/login")

    try:
        start_date_obj = datetime.strptime(start_date, "%d.%m.%Y").date()
        if start_date_obj < date.today():
            return templates.TemplateResponse("request.html", {
                "request": request,
                "courses": COURSES,
                "user": user,
                "error": "Дата не может быть в прошлом"
            })
    except ValueError:
        return templates.TemplateResponse("request.html", {
            "request": request,
            "courses": COURSES,
            "user": user,
            "error": "Неверный формат даты. Используйте ДД.ММ.ГГГГ"
        })

    with get_session() as session:
        new_application = Application(
            user_id=user.id,
            course_name=course_name,
            start_date=start_date_obj,
            payment_method=payment_method,
            status="Новая"
        )
        session.add(new_application)
        session.commit()

    return RedirectResponse(url="/dashboard", status_code=303)


@app.get('/admin')
def admin_panel(request: Request):
    user = get_current_user()
    if not user or user.role != "admin":
        return RedirectResponse(url="/login")

    with get_session() as session:
        applications = session.exec(select(Application)).all()
        apps_with_users = []
        for app in applications:
            app_user = session.exec(select(User).where(User.id == app.user_id)).first()
            apps_with_users.append((app, app_user))

    return templates.TemplateResponse("admin.html", {
        "request": request,
        "applications": apps_with_users
    })


@app.post('/admin/status/{app_id}')
def change_status(app_id: int, new_status: str = Form(...)):
    user = get_current_user()
    if not user or user.role != "admin":
        return RedirectResponse(url="/login")

    with get_session() as session:
        app = session.exec(select(Application).where(Application.id == app_id)).first()
        if app:
            app.status = new_status
            session.add(app)
            session.commit()

    return RedirectResponse(url="/admin", status_code=303)