from typing import Annotated

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
    user_id: int


class NewRecord(SQLModel):
    course: str
    date: str
    payment: str


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


@app.post('/create')
def create_process(request: Request, new_record: Annotated[NewRecord, Form()]):
    user_id = request.cookies.get('user_id')

    with Session(bind=engine) as session:
        session.add(Record(
            user_id=user_id,
            course=new_record.course,
            payment=new_record.payment,
            date=new_record.date
        ))
        session.commit()

    return RedirectResponse('/profile', status_code=302)



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

    return RedirectResponse('/login', status_code=302)


@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse(request, 'login.html')


@app.post('/login')
def login_process(request: Request, user_auth: Annotated[UserAuth, Form()]):
    with Session(bind=engine) as session:
        s = select(User).where(User.login == user_auth.login).where(User.password == user_auth.password)
        user: User | None = session.exec(s).one_or_none()
        if not user:
            return templates.TemplateResponse(
                request,
                'login.html',
                { "error": "Не удалось войти" }
            )

        response = RedirectResponse('/', status_code=302)

        response.set_cookie('user_id', user.id)
        response.set_cookie('role', user.role)

        return response