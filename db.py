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
    username: str = Field(unique=True)
    password: str
    first_name: str
    last_name: str
    second_name: str
    phone: str
    email: str
    role: str | None = Field(default="user")

class Request(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    date: date
    payment_id: int = Field(foreign_key="payment.id")
    course_id: int = Field(foreign_key="course.id")
    user_id: int = Field(foreign_key="user.id")

