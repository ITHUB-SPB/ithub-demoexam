from typing import Annotated

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, create_engine, Session

class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    login: str = Field(unique=True)
    password: str
    email: str
    fio: str
    phone: str
    role: str | None = Field(default="user")


engine = create_engine(r'sqlite:///database.sqlite')
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
templates = Jinja2Templates('templates')


@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(request, 'index.html')


@app.get('/register')
def register(request: Request):
    return templates.TemplateResponse(request, 'register.html')


@app.post('/register')
def register_process(request: Request, user: Annotated[User, Form()]):
    with Session(bind=engine) as session:
        try:
            session.add(user)
            session.commit()
        except IntegrityError:
            session.rollback()
            return templates.TemplateResponse(
                request,
                'register.html',
                { "error": "Логин уже существует" }
            )

    return templates.TemplateResponse(request, 'index.html')