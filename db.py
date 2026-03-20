from datetime import date
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Field

engine = create_engine(r'sqlite:///db.sqlite')

class Course(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    title: str = Field(unique=True)

class Payment(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    title: str = Field(unique=True)

class User(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    first_name: str
    second_name: str
    last_name: str | None
    username: str
    password: str
    phone: str
    email: str
    role: str | None = Field(default="user")
