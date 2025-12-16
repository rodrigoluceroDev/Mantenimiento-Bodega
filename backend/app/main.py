"""
Aplicación FastAPI - Sistema de Mantenimiento Industrial para Bodegas
"""

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import timedelta

from . import crud, schemas
from .database import engine, Base, get_db
from .auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from .deps import get_current_user, get_current_admin, get_current_tecnico
from .qr_gen import generar_qr_base64

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear aplicación FastAPI
app = FastAPI(
    title="Sistema de Mantenimiento Industrial",
    description="API para gestión de mantenimiento de equipos en bodegas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Agregar dominio de producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== RUTAS DE AUTENTICACIÓN ====================

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
async def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login con email y contraseña
    Retorna JWT token y datos del usuario
    """
    # Autenticar usuario
    usuario = crud.autenticar_usuario(db, login_data.email, login_data.password)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    # Crear JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": usuario.id,
            "email": usuario.email,
            "rol": usuario.rol
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": schemas.UsuarioResponse.from_orm(usuario)
    }


@app.get("/api/auth/me", response_model=schemas.UsuarioResponse)
async def obtener_usuario_actual(
    current_user: schemas.UsuarioResponse = Depends(get_current_user)
):
    """
    Obtener datos del usuario actual autenticado
    """
    return current_user


# ==================== RUTAS DE USUARIOS ====================

@app.get("/api/usuarios", response_model=list[schemas.UsuarioResponse])
async def obtener_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: schemas.UsuarioResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios (solo ADMIN)
    """
    usuarios = crud.obtener_todos_usuarios(db, skip=skip, limit=limit)
    return [schemas.UsuarioResponse.from_orm(u) for u in usuarios]


@app.get("/api/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
async def obtener_usuario(
    usuario_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener usuario por ID
    """
    usuario = crud.obtener_usuario_por_id(db, usuario_id)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Solo admin puede ver otros usuarios, lectura puede ver solo su propio usuario
    if current_user.id != usuario_id and current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario"
        )
    
    return schemas.UsuarioResponse.from_orm(usuario)


@app.post("/api/usuarios", response_model=schemas.UsuarioResponse)
async def crear_usuario(
    usuario_create: schemas.UsuarioCreate,
    current_user: schemas.UsuarioResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Crear nuevo usuario (solo ADMIN)
    """
    try:
        usuario = crud.crear_usuario(db, usuario_create)
        return schemas.UsuarioResponse.from_orm(usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/usuarios/{usuario_id}", response_model=schemas.UsuarioResponse)
async def actualizar_usuario(
    usuario_id: int,
    usuario_update: schemas.UsuarioUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar usuario
    El usuario puede actualizar su propia información, admin puede actualizar a cualquiera
    """
    if current_user.id != usuario_id and current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario"
        )
    
    usuario = crud.actualizar_usuario(db, usuario_id, usuario_update)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return schemas.UsuarioResponse.from_orm(usuario)


@app.delete("/api/usuarios/{usuario_id}")
async def eliminar_usuario(
    usuario_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario (solo ADMIN)
    """
    success = crud.eliminar_usuario(db, usuario_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"message": "Usuario eliminado correctamente"}


# ==================== RUTAS DE EQUIPOS ====================

@app.get("/api/equipos", response_model=list[schemas.EquipoResponse])
async def obtener_equipos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    tipo: str = Query(None),
    ubicacion: str = Query(None),
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de equipos con filtros opcionales
    """
    equipos = crud.obtener_todos_equipos(
        db,
        skip=skip,
        limit=limit,
        tipo=tipo,
        ubicacion=ubicacion
    )
    return [schemas.EquipoResponse.from_orm(e) for e in equipos]


@app.get("/api/equipos/{equipo_id}", response_model=schemas.EquipoResponse)
async def obtener_equipo(
    equipo_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener equipo por ID
    """
    equipo = crud.obtener_equipo_por_id(db, equipo_id)
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    return schemas.EquipoResponse.from_orm(equipo)


@app.get("/api/equipos/qr/{codigo_qr}", response_model=schemas.EquipoResponse)
async def obtener_equipo_por_qr(
    codigo_qr: str,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener equipo por código QR
    """
    equipo = crud.obtener_equipo_por_qr(db, codigo_qr)
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    return schemas.EquipoResponse.from_orm(equipo)


@app.post("/api/equipos", response_model=schemas.EquipoResponse)
async def crear_equipo(
    equipo_create: schemas.EquipoCreate,
    current_user: schemas.UsuarioResponse = Depends(get_current_tecnico),
    db: Session = Depends(get_db)
):
    """
    Crear nuevo equipo (TECNICO o ADMIN)
    """
    try:
        equipo = crud.crear_equipo(db, equipo_create)
        return schemas.EquipoResponse.from_orm(equipo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/equipos/{equipo_id}", response_model=schemas.EquipoResponse)
async def actualizar_equipo(
    equipo_id: int,
    equipo_update: schemas.EquipoUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_tecnico),
    db: Session = Depends(get_db)
):
    """
    Actualizar equipo (TECNICO o ADMIN)
    """
    equipo = crud.actualizar_equipo(db, equipo_id, equipo_update)
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    return schemas.EquipoResponse.from_orm(equipo)


@app.delete("/api/equipos/{equipo_id}")
async def eliminar_equipo(
    equipo_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_tecnico),
    db: Session = Depends(get_db)
):
    """
    Eliminar equipo (TECNICO o ADMIN)
    """
    success = crud.eliminar_equipo(db, equipo_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    return {"message": "Equipo eliminado correctamente"}


@app.get("/api/equipos/qr/{codigo_qr}/generar")
async def generar_qr_equipo(
    codigo_qr: str,
    current_user: schemas.UsuarioResponse = Depends(get_current_tecnico),
    db: Session = Depends(get_db)
):
    """
    Generar código QR para un equipo
    """
    equipo = crud.obtener_equipo_por_qr(db, codigo_qr)
    
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    qr_base64 = generar_qr_base64(codigo_qr)
    
    return {
        "equipo_id": equipo.id,
        "codigo_qr": codigo_qr,
        "qr_image": qr_base64
    }


# ==================== RUTAS DE TIPOS DE INTERVENCIÓN ====================

@app.get("/api/tipos-intervencion", response_model=list[schemas.TipoIntervencionResponse])
async def obtener_tipos_intervencion(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de tipos de intervención
    """
    tipos = crud.obtener_todos_tipos_intervencion(db, skip=skip, limit=limit)
    return [schemas.TipoIntervencionResponse.from_orm(t) for t in tipos]


@app.get("/api/tipos-intervencion/{tipo_id}", response_model=schemas.TipoIntervencionResponse)
async def obtener_tipo_intervencion(
    tipo_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener tipo de intervención por ID
    """
    tipo = crud.obtener_tipo_intervencion_por_id(db, tipo_id)
    
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de intervención no encontrado")
    
    return schemas.TipoIntervencionResponse.from_orm(tipo)


@app.post("/api/tipos-intervencion", response_model=schemas.TipoIntervencionResponse)
async def crear_tipo_intervencion(
    tipo_create: schemas.TipoIntervencionCreate,
    current_user: schemas.UsuarioResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Crear nuevo tipo de intervención (solo ADMIN)
    """
    try:
        tipo = crud.crear_tipo_intervencion(db, tipo_create)
        return schemas.TipoIntervencionResponse.from_orm(tipo)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/tipos-intervencion/{tipo_id}", response_model=schemas.TipoIntervencionResponse)
async def actualizar_tipo_intervencion(
    tipo_id: int,
    tipo_update: schemas.TipoIntervencionUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Actualizar tipo de intervención (solo ADMIN)
    """
    tipo = crud.actualizar_tipo_intervencion(db, tipo_id, tipo_update)
    
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de intervención no encontrado")
    
    return schemas.TipoIntervencionResponse.from_orm(tipo)


@app.delete("/api/tipos-intervencion/{tipo_id}")
async def eliminar_tipo_intervencion(
    tipo_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Eliminar tipo de intervención (solo ADMIN)
    """
    success = crud.eliminar_tipo_intervencion(db, tipo_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Tipo de intervención no encontrado")
    
    return {"message": "Tipo de intervención eliminado correctamente"}


# ==================== RUTAS DE INTERVENCIONES ====================

@app.get("/api/intervenciones", response_model=list[schemas.IntervencionResponse])
async def obtener_intervenciones(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    equipo_id: int = Query(None),
    usuario_id: int = Query(None),
    solo_activas: bool = Query(False),
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de intervenciones con filtros opcionales
    """
    intervenciones = crud.obtener_todas_intervenciones(
        db,
        skip=skip,
        limit=limit,
        equipo_id=equipo_id,
        usuario_id=usuario_id,
        solo_activas=solo_activas
    )
    return [schemas.IntervencionResponse.from_orm(i) for i in intervenciones]


@app.get("/api/intervenciones/{intervencion_id}", response_model=schemas.IntervencionDetailResponse)
async def obtener_intervencion(
    intervencion_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener intervención por ID con detalles completos
    """
    intervencion = crud.obtener_intervencion_por_id(db, intervencion_id)
    
    if not intervencion:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    
    return schemas.IntervencionDetailResponse.from_orm(intervencion)


@app.get("/api/equipos/{equipo_id}/historial", response_model=list[schemas.IntervencionResponse])
async def obtener_historial_equipo(
    equipo_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de intervenciones de un equipo
    """
    # Verificar que el equipo exista
    equipo = crud.obtener_equipo_por_id(db, equipo_id)
    if not equipo:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    intervenciones = crud.obtener_historial_equipo(db, equipo_id, skip=skip, limit=limit)
    return [schemas.IntervencionResponse.from_orm(i) for i in intervenciones]


@app.get("/api/usuarios/{usuario_id}/intervenciones", response_model=list[schemas.IntervencionResponse])
async def obtener_intervenciones_usuario(
    usuario_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener intervenciones realizadas por un usuario
    """
    # Verificar permisos
    if current_user.id != usuario_id and current_user.rol != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas intervenciones"
        )
    
    # Verificar que el usuario exista
    usuario = crud.obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    intervenciones = crud.obtener_intervenciones_usuario(db, usuario_id, skip=skip, limit=limit)
    return [schemas.IntervencionResponse.from_orm(i) for i in intervenciones]


@app.post("/api/intervenciones", response_model=schemas.IntervencionResponse)
async def crear_intervencion(
    intervencion_create: schemas.IntervencionCreate,
    current_user: schemas.UsuarioResponse = Depends(get_current_tecnico),
    db: Session = Depends(get_db)
):
    """
    Crear nueva intervención (TECNICO o ADMIN)
    """
    try:
        intervencion = crud.crear_intervencion(db, intervencion_create, current_user.id)
        return schemas.IntervencionResponse.from_orm(intervencion)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/api/intervenciones/{intervencion_id}", response_model=schemas.IntervencionResponse)
async def actualizar_intervencion(
    intervencion_id: int,
    intervencion_update: schemas.IntervencionUpdate,
    current_user: schemas.UsuarioResponse = Depends(get_current_tecnico),
    db: Session = Depends(get_db)
):
    """
    Actualizar intervención (TECNICO o ADMIN)
    """
    intervencion = crud.actualizar_intervencion(db, intervencion_id, intervencion_update)
    
    if not intervencion:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    
    return schemas.IntervencionResponse.from_orm(intervencion)


@app.post("/api/intervenciones/{intervencion_id}/completar")
async def completar_intervencion(
    intervencion_id: int,
    observaciones: str = Query(None),
    tiempo_duracion: int = Query(None),
    current_user: schemas.UsuarioResponse = Depends(get_current_tecnico),
    db: Session = Depends(get_db)
):
    """
    Marcar intervención como completada (TECNICO o ADMIN)
    """
    intervencion = crud.completar_intervencion(
        db,
        intervencion_id,
        observaciones=observaciones,
        tiempo_duracion=tiempo_duracion
    )
    
    if not intervencion:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    
    return {
        "message": "Intervención completada",
        "intervencion": schemas.IntervencionResponse.from_orm(intervencion)
    }


@app.delete("/api/intervenciones/{intervencion_id}")
async def eliminar_intervencion(
    intervencion_id: int,
    current_user: schemas.UsuarioResponse = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Eliminar intervención (solo ADMIN)
    """
    success = crud.eliminar_intervencion(db, intervencion_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Intervención no encontrada")
    
    return {"message": "Intervención eliminada correctamente"}


# ==================== RUTAS DE ESTADÍSTICAS ====================

@app.get("/api/estadisticas")
async def obtener_estadisticas(
    current_user: schemas.UsuarioResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas generales del sistema
    """
    stats = crud.obtener_estadisticas_equipos(db)
    return stats


# ==================== RUTA RAÍZ ====================

@app.get("/", tags=["Health"])
async def root():
    """Verificar que la API está funcionando"""
    return {
        "message": "Sistema de Mantenimiento Industrial - API",
        "version": "1.0.0",
        "status": "online"
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Sistema de Mantenimiento Industrial"
    }
