from typing import Annotated
from typing import List
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends, FastAPI
from sqlalchemy import Column, Integer, String, Boolean, Date, Text, Enum
from sqlalchemy.orm import relationship
from .db import Base
from datetime import date, datetime
import enum

engine = create_engine(r'sqlite:///database.sqlite')
SQLModel.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
templates = Jinja2Templates('templates')
static = StaticFiles(directory='./static')

app.mount('/static', static)

class PaymentMethod(str, enum.Enum):
    cash = "наличные"
    phone = "перевод по номеру телефона"

class AppStatus(str, enum.Enum):
    new = "Новая"
    in_progress = "Идет обучение"
    completed = "Обучение завершено"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(16), nullable=False)
    email = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)

    applications = relationship("Application", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user")

class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    course_name = Column(String(100), nullable=False)   # упрощённо: храним название
    desired_start_date = Column(Date, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(AppStatus), default=AppStatus.new)
    created_at = Column(Date, default=date.today)

    user = relationship("User", back_populates="applications")
    review = relationship("Review", back_populates="application", uselist=False)

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    application_id = Column(Integer, unique=True, nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=False)
    created_at = Column(Date, default=date.today)

    user = relationship("User", back_populates="reviews")
    application = relationship("Application", back_populates="review")

@
