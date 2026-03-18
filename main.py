from typing import Annotated
from datetime import date

from fastapi import FastAPI, Form
from sqlmodel import Session, select
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from authx import AuthX, AuthXConfig

from db import Course, engine, Payment, Request as UserRequest, User

auth = AuthX(config=AuthXConfig(
    JWT_SECRET_KEY="jhiasdijhsadjkxjzxcuio321",
    JWT_TOKEN_LOCATION=["cookies"]
))

app = FastAPI()
templates = Jinja2Templates(directory="templates")


@app.post('/create/')
def create_request(
        course_id: Annotated[int, Form()],
        payment_id: Annotated[int, Form()],
        date: Annotated[date, Form()]
):
    with Session(engine) as session:
        session.add(
            UserRequest(course_id=course_id, payment_id=payment_id, date=date)
        )
        session.commit()

    return RedirectResponse('/', status_code=303)

@app.get('/')
async def index(request: Request):
    token = await auth.get_token_from_request(request)
    payload = auth.verify_token(token, verify_csrf=False)

    if not token or not payload:
        return RedirectResponse('/login', status_code=303)

    print(payload.sub)

    with Session(engine) as session:
        courses = session.exec(select(Course)).all()
        payments = session.exec(select(Payment)).all()
        requests = session.exec(select(UserRequest)).all()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "courses": courses,
            "payments": payments,
            "requests": requests
        }
    )

@app.get('/register')
def register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        { "request": request }
    )

@app.post('/register')
def register_form(request: Request, user: Annotated[User, Form()]):
    print(user)
    user.role = 'user'

    with Session(engine) as session:
        session.add(user)
        session.commit()

    return RedirectResponse('/login', status_code=303)

@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        { "request": request }
    )

@app.post('/login')
def login_form(
        request: Request,
        username: Annotated[str, Form()],
        password: Annotated[str, Form()]
):
    with Session(engine) as session:
        statement = select(User).where(User.username == username).where(User.password == password)
        result = session.exec(statement).all()

    if not result:
        return RedirectResponse('/login', status_code=303)

    token = auth.create_access_token(uid=result[0].username)
    response = RedirectResponse('/', status_code=303)
    auth.set_access_cookies(token, response)

    return response