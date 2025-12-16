from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum
from database import Base


class RoleEnum(str, PyEnum):
    """Enumeración de roles de usuario"""
    ADMIN = "ADMIN"
    TECNICO = "TECNICO"
    LECTURA = "LECTURA"


class Usuario(Base):
    """Modelo de usuario del sistema"""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    rol = Column(Enum(RoleEnum), default=RoleEnum.LECTURA, nullable=False)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    intervenciones = relationship("Intervencion", back_populates="usuario", cascade="all, delete-orphan")

    class Config:
        from_attributes = True


class Equipo(Base):
    """Modelo de equipos/máquinas a mantener"""
    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    codigo_qr = Column(String, unique=True, index=True, nullable=False)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    ubicacion = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # Ej: "Compresor", "Molino", "Bomba"
    modelo = Column(String, nullable=True)
    serie = Column(String, nullable=True)
    fabricante = Column(String, nullable=True)
    fecha_instalacion = Column(DateTime, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    intervenciones = relationship("Intervencion", back_populates="equipo", cascade="all, delete-orphan")

    class Config:
        from_attributes = True


class TipoIntervencion(Base):
    """Modelo para tipos de intervención/mantenimiento"""
    __tablename__ = "tipos_intervencion"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Relaciones
    intervenciones = relationship("Intervencion", back_populates="tipo_intervencion")

    class Config:
        from_attributes = True


class Intervencion(Base):
    """Modelo de intervenciones/mantenimientos realizados"""
    __tablename__ = "intervenciones"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, ForeignKey("equipos.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo_id = Column(Integer, ForeignKey("tipos_intervencion.id"), nullable=False)
    
    descripcion = Column(Text, nullable=False)
    observaciones = Column(Text, nullable=True)
    tiempo_duracion = Column(Integer, nullable=True)  # En minutos
    
    fecha_inicio = Column(DateTime, default=datetime.utcnow)
    fecha_fin = Column(DateTime, nullable=True)
    
    completada = Column(Boolean, default=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    equipo = relationship("Equipo", back_populates="intervenciones")
    usuario = relationship("Usuario", back_populates="intervenciones")
    tipo_intervencion = relationship("TipoIntervencion", back_populates="intervenciones")

    class Config:
        from_attributes = True
