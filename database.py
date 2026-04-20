from sqlmodel import create_engine, Session, SQLModel

DATABASE_URL = r'sqlite:///database.sqlite'
engine = create_engine(DATABASE_URL)

def get_session():
    return Session(engine)

def init_db():
    SQLModel.metadata.create_all(bind=engine)