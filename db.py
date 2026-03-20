from datetime import date
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Field

engine = create_engine(r'sqlite:///db.sqlite')

class Course(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    title: str = Field(unique=True)
