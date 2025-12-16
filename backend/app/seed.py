"""
Scripts de seed para poblar base de datos
"""

from sqlalchemy.orm import Session
from . import crud, schemas, models
from .auth import hash_password


def seed_tipos_intervencion(db: Session):
    """Crear tipos de intervención estándar"""
    tipos = [
        {
            "nombre": "Mantenimiento Preventivo",
            "descripcion": "Mantenimiento preventivo programado"
        },
        {
            "nombre": "Mantenimiento Correctivo",
            "descripcion": "Reparación de equipo con falla"
        },
        {
            "nombre": "Revisión Técnica",
            "descripcion": "Inspección y revisión técnica"
        },
        {
            "nombre": "Calibración",
            "descripcion": "Calibración de equipos de medición"
        },
        {
            "nombre": "Limpieza",
            "descripcion": "Limpieza y mantenimiento de equipo"
        },
    ]
    
    for tipo_data in tipos:
        existing = crud.obtener_tipo_intervencion_por_nombre(db, tipo_data["nombre"])
        if not existing:
            crud.crear_tipo_intervencion(
                db,
                schemas.TipoIntervencionCreate(**tipo_data)
            )
    
    print("✓ Tipos de intervención creados")


def seed_usuario_admin(db: Session, email: str = "admin@bodega.com", password: str = "Admin123!"):
    """Crear usuario administrador"""
    existing = crud.obtener_usuario_por_email(db, email)
    
    if not existing:
        usuario_create = schemas.UsuarioCreate(
            email=email,
            nombre="Administrador",
            rol="ADMIN",
            password=password
        )
        crud.crear_usuario(db, usuario_create)
        print(f"✓ Usuario ADMIN creado: {email}")
    else:
        print(f"⚠ Usuario {email} ya existe")


def seed_usuario_tecnico(db: Session, email: str = "tecnico@bodega.com", password: str = "Tecnico123!"):
    """Crear usuario técnico"""
    existing = crud.obtener_usuario_por_email(db, email)
    
    if not existing:
        usuario_create = schemas.UsuarioCreate(
            email=email,
            nombre="Técnico",
            rol="TECNICO",
            password=password
        )
        crud.crear_usuario(db, usuario_create)
        print(f"✓ Usuario TECNICO creado: {email}")
    else:
        print(f"⚠ Usuario {email} ya existe")


def seed_all(db: Session):
    """Ejecutar todos los seeds"""
    print("Iniciando seed de base de datos...")
    seed_tipos_intervencion(db)
    seed_usuario_admin(db)
    seed_usuario_tecnico(db)
    print("✓ Seed completado")
