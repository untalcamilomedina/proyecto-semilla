#!/usr/bin/env python3
"""
Proyecto Semilla - Interactive Installation Script
Automated setup for fresh installations with security best practices
"""

import asyncio
import getpass
import json
import os
import secrets
import shutil
import string
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import modules that don't depend on .env first
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


class Installer:
    """Main installer class"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.backend_dir = self.project_root / "backend"
        self.frontend_dir = self.project_root / "frontend"
        self.env_file = self.project_root / ".env"
        self.config = {}

    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}🚀 {text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.GREEN}✅ {text}{Colors.END}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.RED}❌ {text}{Colors.END}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

    def get_user_input(self, prompt: str, default: str = "", password: bool = False) -> str:
        """Get user input with optional default value"""
        if default:
            prompt = f"{prompt} (default: {default}): "
        else:
            prompt = f"{prompt}: "

        if password:
            value = getpass.getpass(prompt)
        else:
            value = input(prompt).strip()

        return value if value else default

    def generate_secure_secret(self, length: int = 32) -> str:
        """Generate a secure random secret"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def check_prerequisites(self) -> bool:
        """Check system prerequisites"""
        self.print_header("Verificando Prerrequisitos")

        prerequisites = [
            ("Python", "python3 --version", "3.9"),
            ("pip", "pip3 --version", None),
            ("PostgreSQL", "psql --version", None),
            ("Node.js", "node --version", "16"),
            ("npm", "npm --version", None),
        ]

        all_good = True

        for name, command, min_version in prerequisites:
            try:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    check=True
                )
                version_output = result.stdout.strip()
                if version_output:
                    # Handle different version output formats
                    if name == "Node.js":
                        # Node.js version format: v16.14.0
                        version = version_output.split()[1].lstrip('v') if len(version_output.split()) > 1 else version_output
                    else:
                        version = version_output.split()[1] if len(version_output.split()) > 1 else version_output
                else:
                    version = "Unknown"

                if min_version and version != "Unknown" and version.startswith(min_version):
                    self.print_success(f"{name} {version} - OK")
                elif not min_version:
                    self.print_success(f"{name} - OK")
                else:
                    self.print_warning(f"{name} {version} - Versión mínima requerida: {min_version}")
                    all_good = False

            except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
                self.print_error(f"{name} no encontrado")
                all_good = False

        if not all_good:
            self.print_error("Algunos prerrequisitos no están instalados. Instálalos antes de continuar.")
            return False

        self.print_success("Todos los prerrequisitos verificados correctamente")
        return True

    def install_dependencies(self) -> bool:
        """Install Python and Node.js dependencies"""
        self.print_header("Instalando Dependencias")

        # Install Python dependencies
        self.print_info("Instalando dependencias de Python...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
                cwd=self.backend_dir,
                check=True,
                capture_output=True
            )
            self.print_success("Dependencias de Python instaladas")
        except subprocess.CalledProcessError as e:
            self.print_error(f"Error instalando dependencias de Python: {e}")
            return False

        # Install Node.js dependencies
        self.print_info("Instalando dependencias de Node.js...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=self.frontend_dir,
                check=True,
                capture_output=True
            )
            self.print_success("Dependencias de Node.js instaladas")
        except subprocess.CalledProcessError as e:
            self.print_error(f"Error instalando dependencias de Node.js: {e}")
            return False

        return True

    def setup_database_config(self) -> bool:
        """Setup database configuration"""
        self.print_header("Configuración de Base de Datos")

        print("\nConfiguración de PostgreSQL:")
        print("Asegúrate de tener PostgreSQL corriendo y un usuario con permisos para crear bases de datos.")

        # Database configuration
        db_host = self.get_user_input("Host de PostgreSQL", "localhost")
        db_port = self.get_user_input("Puerto de PostgreSQL", "5432")
        db_name = self.get_user_input("Nombre de la base de datos", "proyecto_semilla")
        db_user = self.get_user_input("Usuario de PostgreSQL", "postgres")
        db_password = self.get_user_input("Contraseña de PostgreSQL", password=True)

        self.config.update({
            'DB_HOST': db_host,
            'DB_PORT': db_port,
            'DB_NAME': db_name,
            'DB_USER': db_user,
            'DB_PASSWORD': db_password,
        })

        # Test database connection
        self.print_info("Probando conexión a la base de datos...")
        try:
            import psycopg2
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database="postgres"  # Connect to default db first
            )
            conn.close()
            self.print_success("Conexión a PostgreSQL exitosa")
        except Exception as e:
            self.print_error(f"Error conectando a PostgreSQL: {e}")
            return False

        # Create database if it doesn't exist
        try:
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=db_user,
                password=db_password,
                database="postgres"
            )
            conn.autocommit = True
            cursor = conn.cursor()

            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {db_name}")
                self.print_success(f"Base de datos '{db_name}' creada")
            else:
                self.print_success(f"Base de datos '{db_name}' ya existe")

            cursor.close()
            conn.close()

        except Exception as e:
            self.print_error(f"Error creando base de datos: {e}")
            return False

        return True

    def generate_env_file(self) -> bool:
        """Generate secure .env file"""
        self.print_header("Generando Configuración Segura")

        # Generate secure secrets
        jwt_secret = self.generate_secure_secret(64)
        admin_password = self.generate_secure_secret(16)

        # Additional configuration
        cors_origins = self.get_user_input(
            "Orígenes CORS (separados por coma)",
            "http://localhost:3000,http://localhost:3001,http://localhost:3002"
        )

        env_content = f"""# Base de datos
DB_PASSWORD={self.config['DB_PASSWORD']}
DB_HOST={self.config['DB_HOST']}
DB_PORT={self.config['DB_PORT']}
DB_NAME={self.config['DB_NAME']}
DB_USER={self.config['DB_USER']}

# Backend
JWT_SECRET={jwt_secret}
CORS_ORIGINS={cors_origins}

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Configuración adicional
DEBUG=true
LOG_LEVEL=INFO

# Seed Data Configuration
SEED_ADMIN_PASSWORD={admin_password}
SEED_DEMO_PASSWORD={self.generate_secure_secret(16)}

# Cookie Security Configuration
COOKIE_SECURE=false
COOKIE_DOMAIN=
COOKIE_SAME_SITE=lax

# Redis (opcional)
REDIS_URL=redis://localhost:6379
"""

        try:
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            self.print_success("Archivo .env generado con configuración segura")

            # Store admin password for later use
            self.config['ADMIN_PASSWORD'] = admin_password
            self.config['JWT_SECRET'] = jwt_secret

            return True

        except Exception as e:
            self.print_error(f"Error creando archivo .env: {e}")
            return False

    async def setup_database(self) -> bool:
        """Setup database tables and initial data"""
        self.print_header("Configurando Base de Datos")

        try:
            # Import modules that depend on .env being present
            from app.core.config import settings
            from app.core.database import create_tables, engine
            from app.core.security import get_password_hash
            from app.models.tenant import Tenant
            from app.models.user import User
            from app.models.role import Role
            from app.models.user_role import UserRole

            # Create tables
            self.print_info("Creando tablas de base de datos...")
            async with engine.begin() as conn:
                from app.models import Tenant, User, Role, UserRole, RefreshToken, Article, Comment, Category
                await conn.run_sync(Tenant.metadata.create_all)
                await conn.run_sync(User.metadata.create_all)
                await conn.run_sync(Role.metadata.create_all)
                await conn.run_sync(UserRole.metadata.create_all)
                await conn.run_sync(RefreshToken.metadata.create_all)
                await conn.run_sync(Article.metadata.create_all)
                await conn.run_sync(Comment.metadata.create_all)
                await conn.run_sync(Category.metadata.create_all)

            self.print_success("Tablas de base de datos creadas")

            # Create initial data
            await self.create_initial_data()
            return True

        except Exception as e:
            self.print_error(f"Error configurando base de datos: {e}")
            return False

    async def create_initial_data(self):
        """Create initial tenant, roles, and super admin"""
        self.print_info("Creando datos iniciales...")

        # Import modules that depend on .env being present
        from app.core.config import settings
        from app.core.database import engine
        from app.core.security import get_password_hash
        from app.models.tenant import Tenant
        from app.models.user import User
        from app.models.role import Role
        from app.models.user_role import UserRole

        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            try:
                # Create initial tenant
                tenant = Tenant(
                    name="Proyecto Semilla",
                    slug="proyecto-semilla",
                    description="Plataforma SaaS multi-tenant de Proyecto Semilla",
                    settings=json.dumps({
                        "theme": "default",
                        "features": ["auth", "tenants", "users", "articles"]
                    })
                )
                session.add(tenant)
                await session.commit()
                await session.refresh(tenant)

                # Create admin role
                admin_role = Role(
                    tenant_id=tenant.id,
                    name="admin",
                    description="Administrator with full access",
                    permissions=json.dumps([
                        "users:read", "users:write", "users:delete",
                        "tenants:read", "tenants:write",
                        "roles:read", "roles:write",
                        "articles:read", "articles:write", "articles:delete",
                        "system:admin"
                    ]),
                    hierarchy_level=100,
                    is_default=False
                )
                session.add(admin_role)
                await session.commit()
                await session.refresh(admin_role)

                # Create user role
                user_role = Role(
                    tenant_id=tenant.id,
                    name="user",
                    description="Standard user role",
                    permissions=json.dumps([
                        "users:read",
                        "tenants:read",
                        "articles:read", "articles:write"
                    ]),
                    hierarchy_level=10,
                    is_default=True
                )
                session.add(user_role)
                await session.commit()
                await session.refresh(user_role)

                # Create super admin user
                admin_email = self.get_user_input("Email del super administrador", "admin@proyectosemilla.dev")
                admin_first_name = self.get_user_input("Nombre del super administrador", "Super")
                admin_last_name = self.get_user_input("Apellido del super administrador", "Admin")

                hashed_password = get_password_hash(self.config['ADMIN_PASSWORD'])

                admin_user = User(
                    tenant_id=tenant.id,
                    email=admin_email,
                    hashed_password=hashed_password,
                    first_name=admin_first_name,
                    last_name=admin_last_name,
                    full_name=f"{admin_first_name} {admin_last_name}",
                    is_active=True,
                    is_verified=True,
                    preferences=json.dumps({
                        "language": "es",
                        "theme": "dark"
                    })
                )
                session.add(admin_user)
                await session.commit()
                await session.refresh(admin_user)

                # Assign admin role
                user_role_association = UserRole(
                    user_id=admin_user.id,
                    role_id=admin_role.id
                )
                session.add(user_role_association)
                await session.commit()

                # Store for summary
                self.config.update({
                    'TENANT_NAME': tenant.name,
                    'ADMIN_EMAIL': admin_email,
                    'ADMIN_NAME': f"{admin_first_name} {admin_last_name}"
                })

                self.print_success("Datos iniciales creados correctamente")

            except Exception as e:
                await session.rollback()
                raise e

    def validate_installation(self) -> bool:
        """Validate the installation"""
        self.print_header("Validando Instalación")

        validation_checks = [
            ("Archivo .env existe", self.env_file.exists()),
            ("Backend directory existe", self.backend_dir.exists()),
            ("Frontend directory existe", self.frontend_dir.exists()),
        ]

        all_valid = True
        for check_name, is_valid in validation_checks:
            if is_valid:
                self.print_success(check_name)
            else:
                self.print_error(check_name)
                all_valid = False

        if all_valid:
            self.print_success("Instalación validada correctamente")
        else:
            self.print_error("Errores encontrados en la validación")

        return all_valid

    def print_installation_summary(self):
        """Print installation summary"""
        self.print_header("Instalación Completada")

        print(f"\n{Colors.BOLD}📋 Resumen de Instalación:{Colors.END}")
        print(f"{'─'*40}")
        print(f"Tenant Principal: {self.config.get('TENANT_NAME', 'N/A')}")
        print(f"Super Admin: {self.config.get('ADMIN_EMAIL', 'N/A')}")
        print(f"Contraseña Admin: {self.config.get('ADMIN_PASSWORD', 'N/A')}")
        print(f"Base de Datos: {self.config.get('DB_NAME', 'N/A')}")
        print(f"Host DB: {self.config.get('DB_HOST', 'N/A')}:{self.config.get('DB_PORT', 'N/A')}")

        print(f"\n{Colors.BOLD}🚀 Para iniciar la aplicación:{Colors.END}")
        print(f"{'─'*40}")
        print("1. Backend: cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        print("2. Frontend: cd frontend && npm run dev")
        print("3. Accede a http://localhost:3000")

        print(f"\n{Colors.YELLOW}⚠️  IMPORTANTE:{Colors.END}")
        print("- Guarda la contraseña del admin en un lugar seguro")
        print("- Cambia la contraseña después del primer login")
        print("- Configura variables de entorno para producción")
        print("- Revisa la documentación de seguridad")

    async def run_installation(self):
        """Run the complete installation process"""
        print(f"{Colors.BOLD}{Colors.BLUE}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                 🏗️  INSTALADOR PROYECTO SEMILLA               ║")
        print("║                 Configuración Automática Segura              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}")

        try:
            # Step 1: Check prerequisites
            if not self.check_prerequisites():
                return

            # Step 2: Install dependencies
            if not self.install_dependencies():
                return

            # Step 3: Setup database configuration
            if not self.setup_database_config():
                return

            # Step 4: Generate secure .env file
            if not self.generate_env_file():
                return

            # Step 5: Setup database and initial data
            if not await self.setup_database():
                return

            # Step 6: Validate installation
            if not self.validate_installation():
                return

            # Step 7: Print summary
            self.print_installation_summary()

            self.print_success("🎉 ¡Instalación completada exitosamente!")

        except KeyboardInterrupt:
            self.print_warning("\nInstalación cancelada por el usuario")
        except Exception as e:
            self.print_error(f"\nError durante la instalación: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """Main entry point"""
    installer = Installer()
    await installer.run_installation()


if __name__ == "__main__":
    asyncio.run(main())