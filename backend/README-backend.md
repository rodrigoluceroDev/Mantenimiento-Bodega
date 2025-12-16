# Backend - Sistema de Mantenimiento Industrial

Backend desarrollado con FastAPI, SQLAlchemy y PostgreSQL.

## Requisitos Previos

- Python 3.9+
- PostgreSQL
- pip

## Instalación

### 1. Crear entorno virtual

```bash
python -m venv venv
source venv/Scripts/activate  # En Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Crear archivo `.env`:

```
DATABASE_URL=postgresql://usuario:password@localhost/bodega_mantenimiento
SECRET_KEY=tu-clave-secreta-muy-segura-cambiar-en-produccion
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. Crear base de datos y tablas

```bash
python scripts/create_tables.py
```

### 5. Crear usuario administrador

```bash
python scripts/create_admin.py
```

## Ejecutar la aplicación

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: `http://localhost:8000`
Documentación interactiva en: `http://localhost:8000/docs`

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # Aplicación FastAPI
│   ├── models.py        # Modelos SQLAlchemy
│   ├── schemas.py       # Esquemas Pydantic
│   ├── crud.py          # Operaciones CRUD
│   ├── auth.py          # Autenticación JWT
│   ├── deps.py          # Dependencias
│   ├── database.py      # Configuración BD
│   ├── qr_gen.py        # Generador QR
│   └── seed.py          # Datos iniciales
├── scripts/
│   ├── create_tables.py # Crear tablas
│   ├── create_admin.py  # Crear admin
│   └── see_data.py      # Ver datos
├── tests/
│   ├── test_auth.py
│   ├── test_equipos.py
│   └── __init__.py
├── requirements.txt
└── Dockerfile
```

## API Endpoints

### Autenticación
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Usuario actual

### Usuarios
- `GET /api/usuarios` - Listar usuarios (ADMIN)
- `GET /api/usuarios/{id}` - Obtener usuario
- `POST /api/usuarios` - Crear usuario (ADMIN)
- `PUT /api/usuarios/{id}` - Actualizar usuario
- `DELETE /api/usuarios/{id}` - Eliminar usuario (ADMIN)

### Equipos
- `GET /api/equipos` - Listar equipos
- `GET /api/equipos/{id}` - Obtener equipo
- `GET /api/equipos/qr/{codigo_qr}` - Obtener por QR
- `POST /api/equipos` - Crear equipo (TECNICO)
- `PUT /api/equipos/{id}` - Actualizar equipo (TECNICO)
- `DELETE /api/equipos/{id}` - Eliminar equipo (TECNICO)
- `GET /api/equipos/qr/{codigo_qr}/generar` - Generar QR

### Tipos de Intervención
- `GET /api/tipos-intervencion` - Listar tipos
- `GET /api/tipos-intervencion/{id}` - Obtener tipo
- `POST /api/tipos-intervencion` - Crear tipo (ADMIN)
- `PUT /api/tipos-intervencion/{id}` - Actualizar tipo (ADMIN)
- `DELETE /api/tipos-intervencion/{id}` - Eliminar tipo (ADMIN)

### Intervenciones
- `GET /api/intervenciones` - Listar intervenciones
- `GET /api/intervenciones/{id}` - Obtener intervención
- `GET /api/equipos/{id}/historial` - Historial de equipo
- `GET /api/usuarios/{id}/intervenciones` - Intervenciones de usuario
- `POST /api/intervenciones` - Crear intervención (TECNICO)
- `PUT /api/intervenciones/{id}` - Actualizar intervención (TECNICO)
- `POST /api/intervenciones/{id}/completar` - Completar intervención (TECNICO)
- `DELETE /api/intervenciones/{id}` - Eliminar intervención (ADMIN)

### Estadísticas
- `GET /api/estadisticas` - Estadísticas generales

## Testing

```bash
pytest tests/
```

## Variables de entorno

```
DATABASE_URL          # URL de conexión PostgreSQL
SECRET_KEY           # Clave secreta para JWT
ACCESS_TOKEN_EXPIRE_MINUTES  # Minutos antes de expirar token (default: 30)
```

## Roles de Usuario

- **ADMIN**: Acceso total, gestión de usuarios
- **TECNICO**: Crear/actualizar equipos e intervenciones
- **LECTURA**: Solo lectura

## Notas

- Los tokens JWT expiran cada 30 minutos
- Las contraseñas se hashean con bcrypt
- Las eliminaciones son soft delete (marcar como inactivo)
- CORS habilitado para `localhost:3000` (frontend)
