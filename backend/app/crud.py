"""
CRUD operations para el sistema de mantenimiento
Contiene todas las operaciones de base de datos
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime
from typing import List, Optional

from . import models, schemas
from .auth import hash_password, verify_password


# ==================== USUARIOS ====================

def obtener_usuario_por_id(db: Session, usuario_id: int) -> Optional[models.Usuario]:
    """Obtener usuario por ID"""
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()


def obtener_usuario_por_email(db: Session, email: str) -> Optional[models.Usuario]:
    """Obtener usuario por email"""
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()


def obtener_todos_usuarios(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    solo_activos: bool = True
) -> List[models.Usuario]:
    """Obtener todos los usuarios con paginación"""
    query = db.query(models.Usuario)
    
    if solo_activos:
        query = query.filter(models.Usuario.activo == True)
    
    return query.offset(skip).limit(limit).all()


def crear_usuario(db: Session, usuario: schemas.UsuarioCreate) -> models.Usuario:
    """Crear nuevo usuario"""
    # Verificar que el email no exista
    if obtener_usuario_por_email(db, usuario.email):
        raise ValueError(f"El email {usuario.email} ya está registrado")
    
    db_usuario = models.Usuario(
        email=usuario.email,
        nombre=usuario.nombre,
        rol=usuario.rol,
        hashed_password=hash_password(usuario.password)
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def actualizar_usuario(
    db: Session,
    usuario_id: int,
    usuario_update: schemas.UsuarioUpdate
) -> Optional[models.Usuario]:
    """Actualizar usuario"""
    db_usuario = obtener_usuario_por_id(db, usuario_id)
    
    if not db_usuario:
        return None
    
    update_data = usuario_update.dict(exclude_unset=True)
    
    # Hashear nueva contraseña si se proporciona
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    
    # Actualizar campos
    for campo, valor in update_data.items():
        setattr(db_usuario, campo, valor)
    
    db_usuario.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


def eliminar_usuario(db: Session, usuario_id: int) -> bool:
    """Eliminar usuario (soft delete)"""
    db_usuario = obtener_usuario_por_id(db, usuario_id)
    
    if not db_usuario:
        return False
    
    db_usuario.activo = False
    db.commit()
    return True


def autenticar_usuario(
    db: Session,
    email: str,
    password: str
) -> Optional[models.Usuario]:
    """Autenticar usuario con email y contraseña"""
    usuario = obtener_usuario_por_email(db, email)
    
    if not usuario:
        return None
    
    if not usuario.activo:
        return None
    
    if not verify_password(password, usuario.hashed_password):
        return None
    
    return usuario


# ==================== EQUIPOS ====================

def obtener_equipo_por_id(db: Session, equipo_id: int) -> Optional[models.Equipo]:
    """Obtener equipo por ID"""
    return db.query(models.Equipo).filter(models.Equipo.id == equipo_id).first()


def obtener_equipo_por_qr(db: Session, codigo_qr: str) -> Optional[models.Equipo]:
    """Obtener equipo por código QR"""
    return db.query(models.Equipo).filter(models.Equipo.codigo_qr == codigo_qr).first()


def obtener_todos_equipos(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    solo_activos: bool = True,
    tipo: Optional[str] = None,
    ubicacion: Optional[str] = None
) -> List[models.Equipo]:
    """Obtener todos los equipos con filtros opcionales"""
    query = db.query(models.Equipo)
    
    if solo_activos:
        query = query.filter(models.Equipo.activo == True)
    
    if tipo:
        query = query.filter(models.Equipo.tipo == tipo)
    
    if ubicacion:
        query = query.filter(models.Equipo.ubicacion == ubicacion)
    
    return query.offset(skip).limit(limit).all()


def crear_equipo(db: Session, equipo: schemas.EquipoCreate) -> models.Equipo:
    """Crear nuevo equipo"""
    # Verificar que el QR no exista
    if obtener_equipo_por_qr(db, equipo.codigo_qr):
        raise ValueError(f"El código QR {equipo.codigo_qr} ya existe")
    
    db_equipo = models.Equipo(**equipo.dict())
    db.add(db_equipo)
    db.commit()
    db.refresh(db_equipo)
    return db_equipo


def actualizar_equipo(
    db: Session,
    equipo_id: int,
    equipo_update: schemas.EquipoUpdate
) -> Optional[models.Equipo]:
    """Actualizar equipo"""
    db_equipo = obtener_equipo_por_id(db, equipo_id)
    
    if not db_equipo:
        return None
    
    update_data = equipo_update.dict(exclude_unset=True)
    
    for campo, valor in update_data.items():
        setattr(db_equipo, campo, valor)
    
    db_equipo.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(db_equipo)
    return db_equipo


def eliminar_equipo(db: Session, equipo_id: int) -> bool:
    """Eliminar equipo (soft delete)"""
    db_equipo = obtener_equipo_por_id(db, equipo_id)
    
    if not db_equipo:
        return False
    
    db_equipo.activo = False
    db.commit()
    return True


def obtener_equipos_por_ubicacion(db: Session, ubicacion: str) -> List[models.Equipo]:
    """Obtener equipos por ubicación"""
    return db.query(models.Equipo).filter(
        and_(
            models.Equipo.ubicacion == ubicacion,
            models.Equipo.activo == True
        )
    ).all()


# ==================== TIPOS DE INTERVENCIÓN ====================

def obtener_tipo_intervencion_por_id(
    db: Session,
    tipo_id: int
) -> Optional[models.TipoIntervencion]:
    """Obtener tipo de intervención por ID"""
    return db.query(models.TipoIntervencion).filter(
        models.TipoIntervencion.id == tipo_id
    ).first()


def obtener_tipo_intervencion_por_nombre(
    db: Session,
    nombre: str
) -> Optional[models.TipoIntervencion]:
    """Obtener tipo de intervención por nombre"""
    return db.query(models.TipoIntervencion).filter(
        models.TipoIntervencion.nombre == nombre
    ).first()


def obtener_todos_tipos_intervencion(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.TipoIntervencion]:
    """Obtener todos los tipos de intervención"""
    return db.query(models.TipoIntervencion).offset(skip).limit(limit).all()


def crear_tipo_intervencion(
    db: Session,
    tipo: schemas.TipoIntervencionCreate
) -> models.TipoIntervencion:
    """Crear nuevo tipo de intervención"""
    # Verificar que no exista
    if obtener_tipo_intervencion_por_nombre(db, tipo.nombre):
        raise ValueError(f"El tipo '{tipo.nombre}' ya existe")
    
    db_tipo = models.TipoIntervencion(**tipo.dict())
    db.add(db_tipo)
    db.commit()
    db.refresh(db_tipo)
    return db_tipo


def actualizar_tipo_intervencion(
    db: Session,
    tipo_id: int,
    tipo_update: schemas.TipoIntervencionUpdate
) -> Optional[models.TipoIntervencion]:
    """Actualizar tipo de intervención"""
    db_tipo = obtener_tipo_intervencion_por_id(db, tipo_id)
    
    if not db_tipo:
        return None
    
    update_data = tipo_update.dict(exclude_unset=True)
    
    for campo, valor in update_data.items():
        setattr(db_tipo, campo, valor)
    
    db.commit()
    db.refresh(db_tipo)
    return db_tipo


def eliminar_tipo_intervencion(db: Session, tipo_id: int) -> bool:
    """Eliminar tipo de intervención"""
    db_tipo = obtener_tipo_intervencion_por_id(db, tipo_id)
    
    if not db_tipo:
        return False
    
    db.delete(db_tipo)
    db.commit()
    return True


# ==================== INTERVENCIONES ====================

def obtener_intervencion_por_id(
    db: Session,
    intervencion_id: int
) -> Optional[models.Intervencion]:
    """Obtener intervención por ID"""
    return db.query(models.Intervencion).filter(
        models.Intervencion.id == intervencion_id
    ).first()


def obtener_todas_intervenciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    equipo_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    solo_activas: bool = False
) -> List[models.Intervencion]:
    """Obtener todas las intervenciones con filtros opcionales"""
    query = db.query(models.Intervencion)
    
    if equipo_id:
        query = query.filter(models.Intervencion.equipo_id == equipo_id)
    
    if usuario_id:
        query = query.filter(models.Intervencion.usuario_id == usuario_id)
    
    if solo_activas:
        query = query.filter(models.Intervencion.completada == False)
    
    return query.order_by(desc(models.Intervencion.fecha_inicio)).offset(skip).limit(limit).all()


def obtener_historial_equipo(
    db: Session,
    equipo_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Intervencion]:
    """Obtener historial de intervenciones de un equipo"""
    return db.query(models.Intervencion).filter(
        models.Intervencion.equipo_id == equipo_id
    ).order_by(desc(models.Intervencion.fecha_inicio)).offset(skip).limit(limit).all()


def obtener_intervenciones_usuario(
    db: Session,
    usuario_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.Intervencion]:
    """Obtener intervenciones realizadas por un usuario"""
    return db.query(models.Intervencion).filter(
        models.Intervencion.usuario_id == usuario_id
    ).order_by(desc(models.Intervencion.fecha_inicio)).offset(skip).limit(limit).all()


def crear_intervencion(
    db: Session,
    intervencion: schemas.IntervencionCreate,
    usuario_id: int
) -> models.Intervencion:
    """Crear nueva intervención"""
    # Verificar que el equipo exista
    if not obtener_equipo_por_id(db, intervencion.equipo_id):
        raise ValueError("El equipo no existe")
    
    # Verificar que el tipo existe
    if not obtener_tipo_intervencion_por_id(db, intervencion.tipo_id):
        raise ValueError("El tipo de intervención no existe")
    
    db_intervencion = models.Intervencion(
        **intervencion.dict(),
        usuario_id=usuario_id
    )
    db.add(db_intervencion)
    db.commit()
    db.refresh(db_intervencion)
    return db_intervencion


def actualizar_intervencion(
    db: Session,
    intervencion_id: int,
    intervencion_update: schemas.IntervencionUpdate
) -> Optional[models.Intervencion]:
    """Actualizar intervención"""
    db_intervencion = obtener_intervencion_por_id(db, intervencion_id)
    
    if not db_intervencion:
        return None
    
    update_data = intervencion_update.dict(exclude_unset=True)
    
    for campo, valor in update_data.items():
        setattr(db_intervencion, campo, valor)
    
    db_intervencion.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(db_intervencion)
    return db_intervencion


def completar_intervencion(
    db: Session,
    intervencion_id: int,
    observaciones: Optional[str] = None,
    tiempo_duracion: Optional[int] = None
) -> Optional[models.Intervencion]:
    """Completar una intervención"""
    db_intervencion = obtener_intervencion_por_id(db, intervencion_id)
    
    if not db_intervencion:
        return None
    
    db_intervencion.completada = True
    db_intervencion.fecha_fin = datetime.utcnow()
    
    if observaciones:
        db_intervencion.observaciones = observaciones
    
    if tiempo_duracion:
        db_intervencion.tiempo_duracion = tiempo_duracion
    
    db_intervencion.fecha_actualizacion = datetime.utcnow()
    db.commit()
    db.refresh(db_intervencion)
    return db_intervencion


def eliminar_intervencion(db: Session, intervencion_id: int) -> bool:
    """Eliminar intervención"""
    db_intervencion = obtener_intervencion_por_id(db, intervencion_id)
    
    if not db_intervencion:
        return False
    
    db.delete(db_intervencion)
    db.commit()
    return True


def obtener_estadisticas_equipos(db: Session) -> dict:
    """Obtener estadísticas de equipos y mantenimientos"""
    total_equipos = db.query(models.Equipo).filter(
        models.Equipo.activo == True
    ).count()
    
    total_intervenciones = db.query(models.Intervencion).count()
    
    intervenciones_completadas = db.query(models.Intervencion).filter(
        models.Intervencion.completada == True
    ).count()
    
    intervenciones_pendientes = db.query(models.Intervencion).filter(
        models.Intervencion.completada == False
    ).count()
    
    return {
        "total_equipos": total_equipos,
        "total_intervenciones": total_intervenciones,
        "intervenciones_completadas": intervenciones_completadas,
        "intervenciones_pendientes": intervenciones_pendientes
    }
