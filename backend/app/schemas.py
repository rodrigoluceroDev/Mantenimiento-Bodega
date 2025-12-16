from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum


class RoleEnum(str, PyEnum):
    """Enumeración de roles"""
    ADMIN = "ADMIN"
    TECNICO = "TECNICO"
    LECTURA = "LECTURA"


# ==================== USUARIO ====================

class UsuarioBase(BaseModel):
    """Schema base de usuario"""
    email: EmailStr
    nombre: str
    rol: RoleEnum = RoleEnum.LECTURA


class UsuarioCreate(UsuarioBase):
    """Schema para crear usuario"""
    password: str = Field(..., min_length=8)


class UsuarioUpdate(BaseModel):
    """Schema para actualizar usuario"""
    nombre: Optional[str] = None
    rol: Optional[RoleEnum] = None
    activo: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=8)


class UsuarioResponse(UsuarioBase):
    """Schema de respuesta de usuario"""
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


# ==================== EQUIPO ====================

class EquipoBase(BaseModel):
    """Schema base de equipo"""
    codigo_qr: str
    nombre: str
    descripcion: Optional[str] = None
    ubicacion: str
    tipo: str
    modelo: Optional[str] = None
    serie: Optional[str] = None
    fabricante: Optional[str] = None
    fecha_instalacion: Optional[datetime] = None


class EquipoCreate(EquipoBase):
    """Schema para crear equipo"""
    pass


class EquipoUpdate(BaseModel):
    """Schema para actualizar equipo"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    ubicacion: Optional[str] = None
    tipo: Optional[str] = None
    modelo: Optional[str] = None
    serie: Optional[str] = None
    fabricante: Optional[str] = None
    fecha_instalacion: Optional[datetime] = None
    activo: Optional[bool] = None


class EquipoResponse(EquipoBase):
    """Schema de respuesta de equipo"""
    id: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


# ==================== TIPO INTERVENCIÓN ====================

class TipoIntervencionBase(BaseModel):
    """Schema base de tipo de intervención"""
    nombre: str
    descripcion: Optional[str] = None


class TipoIntervencionCreate(TipoIntervencionBase):
    """Schema para crear tipo de intervención"""
    pass


class TipoIntervencionUpdate(BaseModel):
    """Schema para actualizar tipo de intervención"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class TipoIntervencionResponse(TipoIntervencionBase):
    """Schema de respuesta de tipo de intervención"""
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ==================== INTERVENCIÓN ====================

class IntervencionBase(BaseModel):
    """Schema base de intervención"""
    equipo_id: int
    tipo_id: int
    descripcion: str
    observaciones: Optional[str] = None
    tiempo_duracion: Optional[int] = None


class IntervencionCreate(IntervencionBase):
    """Schema para crear intervención"""
    pass


class IntervencionUpdate(BaseModel):
    """Schema para actualizar intervención"""
    descripcion: Optional[str] = None
    observaciones: Optional[str] = None
    tiempo_duracion: Optional[int] = None
    completada: Optional[bool] = None
    fecha_fin: Optional[datetime] = None


class IntervencionResponse(IntervencionBase):
    """Schema de respuesta de intervención"""
    id: int
    usuario_id: int
    completada: bool
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime

    class Config:
        from_attributes = True


class IntervencionDetailResponse(IntervencionResponse):
    """Schema detallado de intervención con relaciones"""
    equipo: EquipoResponse
    usuario: UsuarioResponse
    tipo_intervencion: TipoIntervencionResponse


# ==================== AUTH ====================

class TokenResponse(BaseModel):
    """Schema de respuesta de token"""
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse


class LoginRequest(BaseModel):
    """Schema para login"""
    email: EmailStr
    password: str
