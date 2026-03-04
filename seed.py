from sqlmodel import SQLModel, Session, select
from db import engine, Course, Payment

SQLModel.metadata.create_all(bind=engine)

courses = [
    "Основы алгоритмизации и программирования",
    "Основы веб-дизайна",
    "Основы проектирования баз данных"
]

payment = [
    "Наличные",
    "Перевод"
]

with Session(engine) as session:
    try:
        for course in courses:
            session.add(Course(title=course))
    except Exception:
        pass

    try:
        for p in payment:
            session.add(Payment(title=p))
    except Exception:
        pass

    session.commit()

    courses = session.exec(select(Course)).all()
    payment = session.exec(select(Payment)).all()
    print(courses)
    print(payment)