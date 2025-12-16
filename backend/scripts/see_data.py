"""
Script para ver datos en la base de datos
Ejecutar: python scripts/see_data.py
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app import models


def ver_datos():
    """Ver todos los datos en la base de datos"""
    db = SessionLocal()
    try:
        # Usuarios
        usuarios = db.query(models.Usuario).all()
        print("\n=== USUARIOS ===")
        for usuario in usuarios:
            print(f"ID: {usuario.id} | Email: {usuario.email} | Rol: {usuario.rol} | Activo: {usuario.activo}")
        
        if not usuarios:
            print("No hay usuarios")
        
        # Equipos
        equipos = db.query(models.Equipo).all()
        print("\n=== EQUIPOS ===")
        for equipo in equipos:
            print(f"ID: {equipo.id} | Nombre: {equipo.nombre} | QR: {equipo.codigo_qr} | Ubicación: {equipo.ubicacion}")
        
        if not equipos:
            print("No hay equipos")
        
        # Tipos de intervención
        tipos = db.query(models.TipoIntervencion).all()
        print("\n=== TIPOS DE INTERVENCIÓN ===")
        for tipo in tipos:
            print(f"ID: {tipo.id} | Nombre: {tipo.nombre}")
        
        if not tipos:
            print("No hay tipos de intervención")
        
        # Intervenciones
        intervenciones = db.query(models.Intervencion).all()
        print("\n=== INTERVENCIONES ===")
        for intervencion in intervenciones:
            print(f"ID: {intervencion.id} | Equipo: {intervencion.equipo_id} | Usuario: {intervencion.usuario_id} | Completada: {intervencion.completada}")
        
        if not intervenciones:
            print("No hay intervenciones")
        
    finally:
        db.close()


if __name__ == "__main__":
    ver_datos()
