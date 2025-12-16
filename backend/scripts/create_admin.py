"""
Script para crear usuario administrador
Ejecutar: python scripts/create_admin.py
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.seed import seed_usuario_admin, seed_tipos_intervencion


def crear_admin():
    """Crear usuario administrador"""
    db = SessionLocal()
    try:
        seed_tipos_intervencion(db)
        seed_usuario_admin(db)
        print("\n✓ Administrador creado exitosamente")
        print("  Email: admin@bodega.com")
        print("  Contraseña: Admin123!")
    finally:
        db.close()


if __name__ == "__main__":
    crear_admin()
