"""
Pytest Configuration and Shared Fixtures for Discovery Engine Tests

Configuración centralizada de pytest y fixtures compartidas para
todas las pruebas del Architecture Discovery Engine.
"""

import pytest
import tempfile
import json
from pathlib import Path
import logging
import sys
import os

# Configurar logging para tests
logging.basicConfig(level=logging.WARNING)

# Agregar el directorio core al path para imports
sys.path.insert(0, str(Path(__file__).parents[3]))


@pytest.fixture(scope="session")
def test_data_dir():
    """Directorio de datos de prueba"""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="function")
def temp_project_dir():
    """Directorio temporal para proyecto de prueba"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture(scope="function") 
def sample_backend_structure():
    """Estructura de backend FastAPI de ejemplo"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        backend_dir = project_path / "backend" / "app"
        backend_dir.mkdir(parents=True)
        
        # Main FastAPI app
        (backend_dir / "main.py").write_text("""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Test API",
    description="Test API for discovery engine",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
""")
        
        # Models
        models_dir = backend_dir / "models"
        models_dir.mkdir()
        
        (models_dir / "__init__.py").write_text("""
from .user import User
from .tenant import Tenant

__all__ = ["User", "Tenant"]
""")
        
        (models_dir / "user.py").write_text("""
from sqlalchemy import Column, String, Boolean, UUID, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime

Base = declarative_base()

class User(Base):
    '''User model for authentication'''
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
""")
        
        (models_dir / "tenant.py").write_text("""
from sqlalchemy import Column, String, Boolean, UUID, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4
from datetime import datetime

Base = declarative_base()

class Tenant(Base):
    '''Tenant model for multi-tenancy'''
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
""")
        
        # API Routes
        api_dir = backend_dir / "api" / "v1" / "endpoints"
        api_dir.mkdir(parents=True)
        
        (api_dir / "users.py").write_text("""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[dict])
async def read_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Retrieve users with pagination'''
    users = db.query(User).offset(skip).limit(limit).all()
    return [{"id": str(u.id), "email": u.email} for u in users]

@router.post("/", response_model=dict)
async def create_user(
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Create new user'''
    # Implementation here
    return {"created": True}

@router.get("/{user_id}")
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Get user by ID'''
    return {"user_id": user_id}

@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Update user'''
    return {"updated": True}

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    '''Delete user'''
    return {"deleted": True}
""")
        
        # Security
        core_dir = backend_dir / "core"
        core_dir.mkdir()
        
        (core_dir / "security.py").write_text("""
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    '''Verify password against hash'''
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    '''Hash a password'''
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    '''Create JWT access token'''
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials = Depends(security)):
    '''Get current authenticated user'''
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Return mock user for testing
    return {"id": user_id, "email": "test@example.com"}

def create_refresh_token(user_id: str):
    '''Create refresh token'''
    expires = datetime.utcnow() + timedelta(days=7)
    data = {"sub": user_id, "type": "refresh", "exp": expires}
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
""")
        
        yield project_path


@pytest.fixture(scope="function")
def sample_frontend_structure():
    """Estructura de frontend Next.js/React de ejemplo"""
    with tempfile.TemporaryDirectory() as temp_dir:
        project_path = Path(temp_dir)
        frontend_dir = project_path / "frontend"
        frontend_dir.mkdir()
        
        # Package.json
        (frontend_dir / "package.json").write_text(json.dumps({
            "name": "test-frontend",
            "version": "1.0.0",
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start"
            },
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "tailwindcss": "^3.3.0",
                "@radix-ui/react-slot": "^1.0.2",
                "axios": "^1.6.0"
            },
            "devDependencies": {
                "typescript": "^5.3.0",
                "@types/node": "^20.0.0",
                "@types/react": "^18.2.0",
                "@types/react-dom": "^18.2.0",
                "eslint": "^8.50.0",
                "eslint-config-next": "^14.0.0"
            }
        }, indent=2))
        
        # Next.js config
        (frontend_dir / "next.config.js").write_text("""
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['localhost'],
  },
};

module.exports = nextConfig;
""")
        
        # Source directory
        src_dir = frontend_dir / "src"
        src_dir.mkdir()
        
        # App directory (Next.js 13+ App Router)
        app_dir = src_dir / "app"
        app_dir.mkdir()
        
        (app_dir / "layout.tsx").write_text("""
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Test App',
  description: 'Generated for discovery engine testing',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  )
}
""")
        
        (app_dir / "page.tsx").write_text("""
'use client'

import React, { useState, useEffect } from 'react'
import { UserList } from '@/components/UserList'
import { useAuth } from '@/hooks/useAuth'

export default function Home() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const { user, isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated) {
      fetchUsers()
    }
  }, [isAuthenticated])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/users')
      const data = await response.json()
      setUsers(data)
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        User Management System
      </h1>
      
      {loading ? (
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
        </div>
      ) : (
        <UserList users={users} />
      )}
    </main>
  )
}
""")
        
        # Components
        components_dir = src_dir / "components"
        components_dir.mkdir()
        
        (components_dir / "UserList.tsx").write_text("""
import React from 'react'

interface User {
  id: string
  email: string
  firstName: string
  lastName: string
}

interface UserListProps {
  users: User[]
}

export const UserList: React.FC<UserListProps> = ({ users }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {users.map((user) => (
        <div
          key={user.id}
          className="bg-white shadow-lg rounded-lg p-6 border border-gray-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {user.firstName} {user.lastName}
          </h3>
          <p className="text-gray-600">{user.email}</p>
          
          <div className="mt-4 flex space-x-2">
            <button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
              Edit
            </button>
            <button className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600">
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
""")
        
        (components_dir / "Button.tsx").write_text("""
import React from 'react'
import { cn } from '@/lib/utils'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger'
  size?: 'sm' | 'md' | 'lg'
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  ...props
}) => {
  const baseClasses = 'font-medium rounded focus:outline-none focus:ring-2'
  
  const variantClasses = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-500',
    secondary: 'bg-gray-500 text-white hover:bg-gray-600 focus:ring-gray-500',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-500'
  }
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  }

  return (
    <button
      className={cn(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {children}
    </button>
  )
}
""")
        
        # Hooks
        hooks_dir = src_dir / "hooks"
        hooks_dir.mkdir()
        
        (hooks_dir / "useAuth.ts").write_text("""
import { useState, useEffect, useContext, createContext } from 'react'

interface AuthUser {
  id: string
  email: string
  firstName: string
  lastName: string
}

interface AuthContextType {
  user: AuthUser | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const useAuthProvider = (): AuthContextType => {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check for existing session
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('authToken')
      if (token) {
        // Verify token and get user info
        const response = await fetch('/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        if (response.ok) {
          const userData = await response.json()
          setUser(userData)
        } else {
          localStorage.removeItem('authToken')
        }
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    setLoading(true)
    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })

      if (response.ok) {
        const { token, user: userData } = await response.json()
        localStorage.setItem('authToken', token)
        setUser(userData)
      } else {
        throw new Error('Login failed')
      }
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem('authToken')
    setUser(null)
  }

  return {
    user,
    isAuthenticated: !!user,
    login,
    logout,
    loading
  }
}
""")
        
        # Lib utilities
        lib_dir = src_dir / "lib"
        lib_dir.mkdir()
        
        (lib_dir / "utils.ts").write_text("""
import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date) {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(new Date(date))
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func(...args), delay)
  }
}
""")
        
        # Global styles
        (app_dir / "globals.css").write_text("""
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
  }

  * {
    @apply border-border;
  }
  
  body {
    @apply bg-background text-foreground;
  }
}

@layer components {
  .btn-primary {
    @apply bg-blue-500 text-white hover:bg-blue-600 px-4 py-2 rounded;
  }
}
""")
        
        yield project_path


@pytest.fixture(scope="function")
def complete_project_structure(sample_backend_structure):
    """Estructura de proyecto completa combinando backend y frontend"""
    with tempfile.TemporaryDirectory() as temp_dir:
        complete_path = Path(temp_dir)
        
        # Copiar estructura de backend
        import shutil
        shutil.copytree(sample_backend_structure, complete_path / "backend")
        
        # Agregar frontend (estructura simplificada)
        frontend_dir = complete_path / "frontend"
        frontend_dir.mkdir()
        
        (frontend_dir / "package.json").write_text(json.dumps({
            "name": "complete-frontend",
            "dependencies": {
                "react": "^18.0.0",
                "next": "^14.0.0",
                "typescript": "^5.0.0",
                "tailwindcss": "^3.0.0"
            }
        }))
        
        src_dir = frontend_dir / "src"
        src_dir.mkdir()
        
        (src_dir / "App.tsx").write_text("""
import React, { useState, useEffect } from 'react';

const App: React.FC = () => {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    // Fetch data from API
  }, []);
  
  return <div className="container mx-auto">App</div>;
};

export default App;
""")
        
        # Archivos adicionales del proyecto
        (complete_path / "README.md").write_text("""
# Complete Test Project

This is a complete test project structure for the Discovery Engine.

## Architecture

- **Backend**: FastAPI with SQLAlchemy
- **Frontend**: Next.js with React and TypeScript
- **Database**: PostgreSQL with multi-tenant support
- **Authentication**: JWT with refresh tokens

## Features

- Multi-tenant architecture
- Row-Level Security (RLS)
- RESTful API
- Modern React components
- TypeScript support
""")
        
        (complete_path / "docker-compose.yml").write_text("""
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/testdb
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=testdb
    ports:
      - "5432:5432"
""")
        
        # Archivos de configuración adicionales
        (complete_path / ".env.example").write_text("""
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/testdb

# JWT
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Environment
DEBUG=True
""")
        
        yield complete_path


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Configuración automática del entorno de pruebas"""
    # Configurar variables de entorno para tests
    os.environ["TESTING"] = "true"
    os.environ["LOG_LEVEL"] = "WARNING"
    
    # Asegurar que los imports funcionen
    import sys
    sys.path.insert(0, str(Path(__file__).parents[1]))
    
    yield
    
    # Cleanup después de todas las pruebas
    if "TESTING" in os.environ:
        del os.environ["TESTING"]


@pytest.fixture
def mock_logger():
    """Logger mock para pruebas"""
    import logging
    from unittest.mock import Mock
    
    mock_logger = Mock(spec=logging.Logger)
    mock_logger.debug = Mock()
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()
    mock_logger.critical = Mock()
    
    return mock_logger


# Marcar tests como lentos para ejecución opcional
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


# Configurar pytest para mejor output
def pytest_collection_modifyitems(config, items):
    """Modificar items de test para agregar markers automáticamente"""
    for item in items:
        # Marcar tests de integración
        if "integration" in item.nodeid or "test_integration" in item.name:
            item.add_marker(pytest.mark.integration)
        
        # Marcar tests unitarios
        elif "unit" in item.nodeid or item.nodeid.endswith("test_"):
            item.add_marker(pytest.mark.unit)
        
        # Marcar tests lentos
        if any(keyword in item.name for keyword in ["complete_project", "comprehensive", "end_to_end"]):
            item.add_marker(pytest.mark.slow)