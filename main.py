from fastapi import FastAPI ,Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from  db import user
app = FastAPI()


app.mount("/static", StaticFiles(directory="public", html=True))
@app.get("/")
def root():
    return FileResponse("public/index.html")

@app.post("/reg")
async def reg(user_info: user):
     username = user["username"]
     surname = user["surname"]
     email = user["email"]
     phone = user["phone"]
     password = user["password"]
     return {user_info : f"{username}, ваш возраст - {surname}, ваш email - {email}, ваш phone - {phone}, ваш password - {password}"}