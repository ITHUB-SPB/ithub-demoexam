from typing import Annotated

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, create_engine, Session, select

engine = create_engine(r'sqlite:///database.sqlite')
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
templates = Jinja2Templates('templates')
static = StaticFiles(directory='./static')

app.mount('/static', static)


@app.get('/')
def index(request: Request):
    return 'hi'
