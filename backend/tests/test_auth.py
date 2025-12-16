"""
Tests para autenticación y JWT
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base
from app import crud, schemas


# Crear base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Setup y teardown para cada test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_crear_usuario():
    """Test crear usuario"""
    response = client.post(
        "/api/usuarios",
        json={
            "email": "test@example.com",
            "nombre": "Test User",
            "rol": "TECNICO",
            "password": "testpass123"
        }
    )
    assert response.status_code == 401  # Sin autenticación


def test_login_invalido():
    """Test login con credenciales inválidas"""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "noexiste@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email o contraseña incorrectos"


def test_health_check():
    """Test health check"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    """Test endpoint raíz"""
    response = client.get("/")
    assert response.status_code == 200
    assert "version" in response.json()
