"""
Dependencias FastAPI
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from sqlalchemy.orm import Session

from . import schemas, crud
from .database import get_db
from .auth import verify_token

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> schemas.UsuarioResponse:
    """
    Obtener usuario actual desde token JWT
    Verifica que el token sea válido y el usuario exista
    """
    token = credentials.credentials
    
    # Verificar token
    token_data = verify_token(token)
    
    # Obtener usuario de base de datos
    usuario = crud.obtener_usuario_por_id(db, token_data["user_id"])
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado"
        )
    
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario inactivo"
        )
    
    return schemas.UsuarioResponse.from_orm(usuario)


async def get_current_admin(
    current_user: schemas.UsuarioResponse = Depends(get_current_user)
) -> schemas.UsuarioResponse:
    """
    Verificar que el usuario actual sea ADMIN
    """
    if current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol ADMIN"
        )
    
    return current_user


async def get_current_tecnico(
    current_user: schemas.UsuarioResponse = Depends(get_current_user)
) -> schemas.UsuarioResponse:
    """
    Verificar que el usuario actual sea TECNICO o ADMIN
    """
    if current_user.rol not in ["TECNICO", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requiere rol TECNICO o ADMIN"
        )
    
    return current_user


async def get_authenticated_user(
    current_user: schemas.UsuarioResponse = Depends(get_current_user)
) -> schemas.UsuarioResponse:
    """
    Verificar que el usuario esté autenticado (cualquier rol)
    """
    return current_user
