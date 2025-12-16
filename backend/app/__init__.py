"""
Inicializador del paquete app
"""

from .database import Base, engine

# Crear tablas al importar el paquete
Base.metadata.create_all(bind=engine)
