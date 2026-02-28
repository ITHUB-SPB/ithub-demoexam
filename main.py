from fastapi import FastAPI

app = FastAPI()


@app.get('/')
def index():
    return { "ping": "pong" }


@app.get('/upper/{word}')
def index(word: str):
    return { word: word.upper() }
