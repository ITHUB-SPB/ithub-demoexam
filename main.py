
from fastapi import FastAPI
from sqlmodel import Session, select
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from db import Course, engine, Payment

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def main(request: Request):
    with Session(engine) as session:
        courses = session.exec(select(Course)).all()
        payments = session.exec(select(Payment)).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "courses": courses,
            "payments": payments
        }
    )

@app.get("/register")
async def root(request: Request):
    return { }

@app.get("/login")
async def user(request: Request):
    return user

@app.get("/admin")
async def user(request: Request):
    return { "user_id": "the current user" }