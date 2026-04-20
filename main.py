from typing import Annotated
from typing import Optional
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, create_engine, Session, select

class Record(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    course: str
    date: str
    payment: str
    status: str
    user_id: int


class NewRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    course: str
    date: str
    payment: str
    user_id: int


class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    login: str = Field(unique=True)
    password: str
    email: str
    fio: str
    phone: str
    role: str | None = Field(default="user")

class UserAuth(SQLModel):
    login: str
    password: str

engine = create_engine(r'sqlite:///database.sqlite')
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
templates = Jinja2Templates('templates')
static = StaticFiles(directory='./static')

app.mount('/static', static)


@app.get('/')
def index(request: Request):
    role = request.cookies.get('role')

    if not role:
        return RedirectResponse('/login', status_code=302)

    if role == "admin":
        return RedirectResponse('/admin', status_code=302)

    return RedirectResponse('/profile', status_code=302)


@app.get('/admin')
def admin(request: Request):
    role = request.cookies.get('role')

    with Session(bind=engine) as session:

        s = select(Record, User).where(Record.uder_id == User.id)
        record = session.exec(s).all()
    return templates.TemplateResponse(
        request,
        'admin.html',
        {"records": record}
    )

@app.get('/profile')
def profile(request: Request):
    role = request.cookies.get('role')
    user_id = request.cookies.get('user_id')

    with Session(bind=engine) as session:
        s = select(Record).where(Record.user_id == int(user_id))
        records = session.exec(s).all()

        return templates.TemplateResponse(
            request,
            'profile.html',
            { "records": records }
        )
    

@app.get('/logout')
def logout():
    response = RedirectResponse('/login', status_code=302)

    response.delete_cookie('user_id')
    response.delete_cookie('role')

    return response


@app.get('/create')
def create(request: Request):
    return templates.TemplateResponse(request, 'create.html')