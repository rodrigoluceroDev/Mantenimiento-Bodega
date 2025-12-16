from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar URL de base de datos
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost/bodega_mantenimiento"
)

# Crear engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver queries SQL
    pool_pre_ping=True,  # Verificar conexiones antes de usar
)

# Crear sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """Dependencia para obtener sesión de BD en rutas FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
