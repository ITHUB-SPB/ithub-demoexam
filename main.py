from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi import Request
app = FastAPI()

templates = Jinja2Templates("templates")

@app.get("/")
def home ():
    return templates