from database import get_session
from models import User
from sqlmodel import select

current_user_login = None


def set_current_user(login):
    global current_user_login
    current_user_login = login


def clear_current_user():
    global current_user_login
    current_user_login = None


def get_current_user():

    if not current_user_login:
        return None
    with get_session() as session:
        return session.exec(select(User).where(User.login == current_user_login)).first()