# 🚀 Guía de Inicio Rápido

## Inicio Rápido Backend

### 1. Preparar Entorno

```powershell
# Navegar al directorio backend
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (macOS/Linux)
source venv/bin/activate
```

### 2. Instalar Dependencias

```powershell
pip install -r requirements.txt
```

### 3. Configurar Base de Datos

Opción A: **SQLite** (desarrollo rápido)
```powershell
# Crear archivo .env
copy .env.example .env

# La URL ya está configurada para SQLite
```

Opción B: **PostgreSQL** (recomendado)
```powershell
# Editar .env
DATABASE_URL=postgresql://postgres:password@localhost/bodega_mantenimiento

# Crear base de datos en PostgreSQL
createdb bodega_mantenimiento
```

### 4. Crear Tablas y Admin

```powershell
# Crear tablas
python scripts/create_tables.py

# Crear usuario administrador
python scripts/create_admin.py
```

**Credenciales de administrador creadas:**
- Email: `admin@bodega.com`
- Password: `Admin123!`

### 5. Ejecutar API

```powershell
# En el directorio backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**API disponible en:**
- 🌐 http://localhost:8000
- 📚 Documentación: http://localhost:8000/docs
- 🔧 ReDoc: http://localhost:8000/redoc

---

## Inicio Rápido Frontend

### 1. Instalar Dependencias

```powershell
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

Crear archivo `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Ejecutar Frontend

```powershell
npm run dev
```

**Frontend disponible en:** http://localhost:3000

---

## 🔑 Roles de Usuario

| Rol | Permisos |
|-----|----------|
| **ADMIN** | Gestión completa del sistema |
| **TECNICO** | Crear/editar equipos e intervenciones |
| **LECTURA** | Solo lectura de datos |

---

## 📡 Probar API

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@bodega.com","password":"Admin123!"}'
```

### Obtener Usuario Actual
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer <TOKEN>"
```

### Crear Equipo
```bash
curl -X POST "http://localhost:8000/api/equipos" \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "codigo_qr":"EQ-001",
    "nombre":"Compresor Industrial",
    "ubicacion":"Bodega A",
    "tipo":"Compresor"
  }'
```

---

## 🗄️ Ver Datos en BD

```powershell
python scripts/see_data.py
```

---

## 🧪 Ejecutar Tests

```powershell
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=app
```

---

## 📦 Docker

### Build
```powershell
docker build -t bodega-mantenimiento-backend .
```

### Run
```powershell
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:password@postgres:5432/bodega \
  bodega-mantenimiento-backend
```

### Docker Compose
```powershell
docker-compose up --build
```

---

## ❌ Resolver Problemas Comunes

### Error: "Database connection refused"
→ Verificar que PostgreSQL esté corriendo
→ Verificar credenciales en `.env`
→ Usar SQLite para desarrollo rápido

### Error: "Port 8000 already in use"
```powershell
# Cambiar puerto
uvicorn app.main:app --port 8001
```

### Error: "Module not found"
```powershell
# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

### Error: "Token inválido en Frontend"
→ Verificar `Authorization: Bearer <token>` en headers
→ Verificar que el token no haya expirado
→ Verificar `CORS` en `main.py`

---

## 📚 Documentación

- [Backend README](backend/README-backend.md)
- [Frontend README](frontend/README-frontend.md)
- [Evaluación de Estructura](EVALUACION_ESTRUCTURA.md)

---

## 🎯 Próximos Pasos

1. ✅ Completar integración frontend-backend
2. ✅ Implementar notificaciones en tiempo real (WebSockets)
3. ✅ Agregar generación de reportes
4. ✅ Configurar CI/CD con GitHub Actions
5. ✅ Desplegar en producción (AWS/Azure/Heroku)

---

**¡Listo para desarrollar! 🚀**
