"""
Script para crear tablas en la base de datos
Ejecutar: python scripts/create_tables.py
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, Base
from app import models


def create_tables():
    """Crear todas las tablas en la base de datos"""
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tablas creadas exitosamente")


if __name__ == "__main__":
    create_tables()
