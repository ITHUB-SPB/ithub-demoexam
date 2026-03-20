from fastapi import FastAPI,Request
from fastapi.templating import Jinja2Templates

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get('/login')
def login_page (request: Request):
    return templates.TemplateResponse("login.html", {"request": request}  )

@app.post('/login')
def login():
    None

@app.get('/admin')
def admin_page (request: Request):
    return templates.TemplateResponse("admin.html", {"request": request}  )

@app.post('/admin')
def admin():
    None

