
import sqlite3
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="BANANA")

templates = Jinja2Templates(directory="templates")

DATABASE = "database.db"
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return  conn

def init_db():
    with get_db() as conn:
        conn.executescript("""
        create table if not exists users(
        id integer primary key autoincrement,
        login text unique not null,
        password not null,
        email not null,
        phone not null,
        fio not null
        );
        
        create table if not exists requests(
        id integer primary key autoincrement,
        course_name text,
        user_id integer not null,
        date_start not null,
        payment_method not null,
        status not null default 'Новая',
        foreign key (user_id) references users(id) on delete cascade
        );
        """)

init_db()

@app.get("/")
def get_login(request: Request):
    return RedirectResponse(url="/login", status_code=302)


@app.get("/register")
def get_register(request: Request):
    return templates.TemplateResponse("register.html",{"request":request, "error": None})

@app.get("/login")
def get_login(request: Request):
    return templates.TemplateResponse("login.html",{"request":request, "error": None})



@app.post("/register")
def post_register(request: Request,
                login: str = Form(...),
                password: str = Form(...),
                fio: str = Form(...),
                email: str = Form(...),
                phone  : str = Form(...)
                  ):
    with get_db() as conn:
        conn.execute("insert into users (login,password,email,phone,fio) values (?,?,?,?,?)", (login, password,email,phone,fio))
        return RedirectResponse("/login", status_code=302)
    return templates.TemplateResponse("register.html",{"request":request, "error": "Бро, данные неверные"})


@app.post("/login")
def post_login(request: Request,
                  login: str = Form(...),
                  password: str = Form(...)
                  ):
    if login == "Admin" and password == "KorokNET":
        request.session["admin"] = True
        return RedirectResponse(url="/admin", status_code=302)

    with get_db() as conn:
        user = conn.execute("select * from users where login = ?", (login,)).fetchone()
        if user and user["password"] == password:
            request.session["user_id"] = user["id"]
            return RedirectResponse("/profile",status_code=302)
        else:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Неверный пароль или логин"})

COURSES = [
    "Основы алгоритмизации и программирования",
    "Основы веб-дизайна",
    "Основы проектирования баз данных"
]
PAYMENTS = ["наличными", "переводом по номеру телефона"]



@app.get("/profile")
def get_profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    with get_db() as conn:
        requests_list = conn.execute("select * from requests where user_id = ?", (user_id,)).fetchall()
    return templates.TemplateResponse("profile.html", {"request": request, "requests": requests_list})


@app.get("/create_request")
def create_request_form(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse("create_request.html",{"request": request, "courses": COURSES, "payment": PAYMENTS, "error": None})

@app.post("/create_request")
def post_create_request(request: Request,
                        courses: str = Form(...),
                        date: str = Form(...),
                        payment: str = Form(...)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=302)

    with get_db() as conn:
        conn.execute("insert into requests (user_id,course_name, date_start,payment_method) values (?,?,?,?)",(user_id,courses,date,payment))
    return RedirectResponse(url="/profile", status_code=302)


@app.get("/admin")
def get_admin(request: Request):
    if not request.session.get("admin"):
        return RedirectResponse(url="/login", status_code=302)
    with get_db() as conn:
        request_list = conn.execute("select r.*, u.login,u.fio from requests r join users u on r.user_id = u.id order by r.id desc").fetchall()
    return templates.TemplateResponse("admin.html", {"request": request, "requests": request_list})


@app.get("/logout")
def get_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login",status_code=302)
