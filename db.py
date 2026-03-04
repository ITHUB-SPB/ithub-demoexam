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

class Request(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    date: date
    payment_id: int = Field(foreign_key="payment.id")
    course_id: int = Field(foreign_key="course.id")
