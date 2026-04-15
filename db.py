
from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationError
from datetime import date, datetime
from main import  engine
import re
from sqlalchemy.orm import sessionmaker, declarative_base

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@field_validator("phone_number")
@classmethod
def validate_phone_number(cls, values: str) -> str:
    if not re.match(r'^\+\d{1,15}$', values):
        raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
    return values

@field_validator("date_of_birth")
@classmethod
def validate_date_of_birth(cls, values: date):
    if values and values >= datetime.now().date():
        raise ValueError('Дата рождения должна быть в прошлом')
    return values