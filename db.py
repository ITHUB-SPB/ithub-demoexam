from datetime import date
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Field

engine = create_engine(r'sqlite:///db.sqlite')

class Course(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    title: str = Field(unique=True)

class payment(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    type: str = Field(unique=True)
    date: date

class user(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    username: str = Field(unique=True)
    surname: str = Field(unique=True)
    password: str = Field(unique=True)
    email: str = Field(unique=True)
    phone: str = Field(unique=True)
    role: str = Field(unique=True)

