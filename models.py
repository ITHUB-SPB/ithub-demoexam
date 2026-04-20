from sqlmodel import SQLModel, Field
from datetime import date

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    login: str = Field(unique=True, nullable=False)
    password: str = Field(nullable=False)
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    phone: str = Field(nullable=False)
    email: str = Field(nullable=False)
    role: str = Field(default="user")

class Application(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    course_name: str = Field(nullable=False)
    start_date: date = Field(nullable=False)
    payment_method: str = Field(nullable=False)
    status: str = Field(default="Новая")
    review: str | None = Field(default=None)