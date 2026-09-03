import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine, SQLModel, text


load_dotenv()  # Cargar variables de entorno desde el archivo .env

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?options=-csearch_path%3Dprueba_evento"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)

def get_session():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def consulta_prueba():
    with Session(engine) as session:
        resultado = session.exec(text("SELECT * FROM usuarios")).first()
        return resultado