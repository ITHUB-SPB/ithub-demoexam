import sqlite3
import re as ree
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(debug=True)
app.add_middleware(SessionMiddleware, secret_key="deadlock")
templates = Jinja2Templates('templates')


DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
create table if not exists users(id integer primary key autoincrement,
                           login text not null,
                           password text not null,
                           fio text not null,
                           phone text not null,
                           email text not null);
create table if not exists requests(id integer primary key autoincrement,
                           user_id integer references users(id) on delete cascade,
                           course_name text not null,
                           date_start text not null,
                           payment_method text not null,
                           status text default 'Новая',
                           review text);
                           """)
        
init_db()


@app.get('/')
def get_base(request: Request):
    return RedirectResponse(url="/login", status_code=302)

@app.get("/logout")
def get_logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)

@app.get("/register")
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register")
def post_register(request: Request,
                  login: str = Form(...),
                  password: str = Form(...),
                  fio: str = Form(...),
                  phone: str = Form(...),
                  email: str = Form(...)):
    error = None
    if not ree.fullmatch(r'[a-zA-Z0-9]{6,}', login):
        error = "Логин: латиница и цифры, не менее 6 символов"
    if len(password) < 8:
        error = "Пароль: минимум 8 символов"
    if not ree.fullmatch(r'[а-яА-ЯёЁ\s]+', fio):
        error = "ФИО: символы кириллицы и пробелы"
    if not ree.fullmatch(r'8\(\d{3}\)\d{3}-\d{2}-\d{2}', phone):
        error = "Телефон: формат: 8(XXX)XXX-XX-XX"
    if not ree.fullmatch(r'[^@]+@[^@]+\.[^@]+', email):
        error = "Почта: формат: электронной почты"
    with get_db() as conn:
        user = conn.execute("select * from users where login = ?", (login,)).fetchone()
        if not user:
            conn.execute("insert into users (login, password, fio, phone, email) values (?,?,?,?,?)", (login, password, fio, phone, email))
            return RedirectResponse(url="/login", status_code=302)
        else: 
            error = "Логин уже занят"
    return templates.TemplateResponse("register.html", {"request": request, "error": error, "login": login, "password": password, "fio": fio, "phone": phone, "email": email})

@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def post_login(request: Request,
               login: str = Form(...),
               password: str = Form(...)):
    if login == "Admin":
        if password == "KorokNET":
            request.session["admin"] = True
            return RedirectResponse(url="/admin", status_code=302)
        else: 
            return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные"})
    with get_db() as conn:
        user = conn.execute("select * from users where login = ?", (login,)).fetchone()
        if user and user["password"] == password:
            request.session["user_id"] = user["id"]
            return RedirectResponse(url="/profile", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": "Неверные данные"})

@app.get("/profile")
def get_profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    with get_db() as conn:
        request_list = conn.execute("select * from requests where user_id = ?", (user_id,)).fetchall()
    return templates.TemplateResponse("profile.html", {"request": request, "requests": request_list})

COURSES = ["Основы алгоритмизации и программирования", "Основы веб-дизайна", "Основы проектирования баз данных"]
PAYMENTS = ["наличными", "переводом по номеру телефона"]

@app.get("/create_request")
def get_create_request(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("create_request.html", {"request": request, "courses": COURSES, "payments": PAYMENTS})

@app.post("/create_request")
def post_create_request(request: Request,
                        course: str = Form(...),
                        date: str = Form(...),
                        payment: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    with get_db() as conn:
        conn.execute("insert into requests (course_name, date_start, payment_method, user_id) values (?,?,?,?)", (course, date, payment, user_id))
    return RedirectResponse(url="/profile", status_code=302)

@app.get("/admin")
def get_admin(request: Request):
    user_id = request.session.get("admin")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)    
    with get_db() as conn:
        request_list = conn.execute("select requests.*, users.login, users.fio from requests, users where user_id = requests.user_id")
    return templates.TemplateResponse("admin.html", {"request": request, "requests": request_list})

@app.post("/admin/change_status")
def get_admin_change_status(request: Request,
              status: str = Form(...),
              request_id: str = Form(...)):
    user_id = request.session.get("admin")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)    
    with get_db() as conn:
        conn.execute("update requests set status = ? where id = ?", (status, request_id))
    return RedirectResponse(url="/admin", status_code=302)

@app.post("/add_review")
def post_add_review(request: Request,
                    review: str = Form(...),
                    request_id: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)
    with get_db() as conn:
        cur = conn.execute("select * from requests where status = 'Обучение завершено' and id = ? and review is null", (request_id,)).fetchone()
        if cur:
            conn.execute("update requests set review = ? where id = ?", (review, request_id))
    return RedirectResponse(url="/profile", status_code=302)