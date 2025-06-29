import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Ruta a la base de datos (asegurándonos que sea relativa desde la raíz del proyecto)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Obtiene la ubicación de database.py
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, '../../db.sqlite3')}"  # Ruta correcta al archivo db.sqlite3

# DATABASE_URL = "sqlite:///api/db.sqlite3"  # Ruta correcta a db.sqlite3 en la carpeta 'api'



# Configuración de SQLAlchemy
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Función para obtener la sesión de DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
