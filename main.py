from typing import Annotated
from datetime import date

from fastapi import FastAPI, Form
from sqlmodel import Session, select
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from db import Course, engine, Payment, Request as UserRequest

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
def index(request: Request):
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