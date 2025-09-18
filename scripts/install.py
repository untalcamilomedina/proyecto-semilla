#!/usr/bin/env python3
"""
Proyecto Semilla - Instalador Interactivo
Script de instalación automatizada para configurar el entorno de desarrollo
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional


def check_dependencies():
    """Verificar que las dependencias Python necesarias estén instaladas"""
    print("🔍 Verificando dependencias Python...")

    required_modules = [
        'alembic',  # Para migraciones de base de datos
        'secrets',  # Para generación de secrets (incluido en Python 3.6+)
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} - OK")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module} - FALTANTE")

    if missing_modules:
        print(f"\n❌ Módulos faltantes: {', '.join(missing_modules)}")
        print("\nPara instalar las dependencias faltantes:")
        print("  pip install alembic")
        print("\nO instala todas las dependencias del proyecto:")
        print("  pip install -r backend/requirements.txt")
        return False

    print("✅ Todas las dependencias Python están instaladas")
    return True


class ProyectoSemillaInstaller:
    """
    Instalador interactivo para Proyecto Semilla
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / ".env"
        self.required_commands = ["docker", "docker-compose"]

    def print_header(self):
        """Imprimir header del instalador"""
        print("\n" + "="*60)
        print("🌱 PROYECTO SEMILLA - INSTALADOR INTERACTIVO")
        print("="*60)
        print("Bienvenido al instalador de Proyecto Semilla")
        print("Este script te guiará a través de la configuración inicial.\n")

    def check_prerequisites(self) -> bool:
        """Verificar prerrequisitos del sistema"""
        print("🔍 Verificando prerrequisitos...")

        missing_commands = []
        for cmd in self.required_commands:
            if not self.command_exists(cmd):
                missing_commands.append(cmd)

        if missing_commands:
            print(f"❌ Comandos faltantes: {', '.join(missing_commands)}")
            print("\nPor favor instala Docker y Docker Compose:")
            print("- Docker: https://docs.docker.com/get-docker/")
            print("- Docker Compose: https://docs.docker.com/compose/install/")
            return False

        print("✅ Todos los prerrequisitos están instalados")
        return True

    def command_exists(self, command: str) -> bool:
        """Verificar si un comando existe en el sistema"""
        try:
            subprocess.run([command, "--version"],
                         capture_output=True,
                         check=True,
                         text=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_user_input(self, prompt: str, default: str = "", required: bool = False) -> str:
        """Obtener input del usuario con validación"""
        while True:
            if default:
                value = input(f"{prompt} (default: {default}): ").strip()
                if not value:
                    return default
            else:
                value = input(f"{prompt}: ").strip()

            if required and not value:
                print("❌ Este campo es obligatorio")
                continue

            return value

    def get_yes_no(self, prompt: str, default: bool = True) -> bool:
        """Obtener respuesta sí/no del usuario"""
        default_text = "Y/n" if default else "y/N"
        while True:
            response = input(f"{prompt} [{default_text}]: ").strip().lower()
            if not response:
                return default
            if response in ["y", "yes", "s", "si"]:
                return True
            if response in ["n", "no"]:
                return False
            print("Por favor responde 'y' para sí o 'n' para no")

    def configure_environment(self) -> Dict[str, Any]:
        """Configurar variables de entorno"""
        print("\n⚙️ Configuración del Entorno")
        print("-" * 30)

        config = {}

        # Base de datos
        print("\n🗄️ Configuración de Base de Datos:")
        config["DB_PASSWORD"] = self.get_user_input(
            "Contraseña para PostgreSQL",
            "changeme123",
            required=True
        )

        # JWT
        print("\n🔐 Configuración de JWT:")
        jwt_secret = self.get_user_input(
            "JWT Secret Key (deja vacío para generar automáticamente)",
            ""
        )
        if not jwt_secret:
            import secrets
            jwt_secret = secrets.token_urlsafe(64)  # Generar JWT_SECRET de al menos 64 caracteres
            print(f"🔑 JWT Secret generado: {jwt_secret[:20]}... (longitud: {len(jwt_secret)})")

        config["JWT_SECRET"] = jwt_secret

        # Configuración adicional
        config["DEBUG"] = "True" if self.get_yes_no("¿Habilitar modo debug?", True) else "False"

        return config

    def create_env_file(self, config: Dict[str, Any]):
        """Crear archivo .env con la configuración"""
        print("\n📝 Creando archivo .env...")

        env_content = f"""# Proyecto Semilla - Configuración de Entorno
# Generado automáticamente por install.py

# Base de datos
DB_PASSWORD={config["DB_PASSWORD"]}
DB_HOST=db
DB_PORT=5432
DB_NAME=proyecto_semilla

# Backend
JWT_SECRET={config["JWT_SECRET"]}
CORS_ORIGINS=http://localhost:7701,http://localhost:7777
DEBUG={config["DEBUG"]}

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:7777

# Configuración adicional
LOG_LEVEL=INFO
"""

        try:
            with open(self.env_file, "w", encoding="utf-8") as f:
                f.write(env_content)
            print(f"✅ Archivo .env creado en: {self.env_file}")
        except Exception as e:
            print(f"❌ Error creando archivo .env: {e}")
            raise

    def setup_database(self):
        """Configurar la base de datos"""
        print("\n🗄️ Configurando Base de Datos...")

        try:
            # Levantar servicios de base de datos
            subprocess.run([
                "docker-compose", "up", "-d", "db", "redis"
            ], cwd=self.project_root, check=True)

            print("⏳ Esperando a que los servicios estén listos...")
            import time
            time.sleep(15)  # Esperar a que DB y Redis estén listos

            # Ejecutar migraciones de Alembic
            print("📦 Ejecutando migraciones de base de datos...")
            result = subprocess.run([
                "PYTHONPATH=/app", "python3", "-m", "alembic", "upgrade", "head"
            ], cwd=self.project_root / "backend", capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Migraciones ejecutadas correctamente")
            else:
                print("❌ Error en migraciones:")
                print(result.stderr)
                return False

            print("✅ Base de datos configurada correctamente")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Error configurando la base de datos: {e}")
            return False

    def create_superuser(self):
        """Crear usuario superadministrador"""
        print("\n👤 Creación de Superadministrador")
        print("-" * 35)

        if not self.get_yes_no("¿Quieres crear datos iniciales (superadmin + demo)?", True):
            print("ℹ️ El superadministrador se puede crear desde el frontend después de iniciar la aplicación")
            print("   Accede a la aplicación y usa la interfaz de configuración inicial")
            return

        print("Ejecutando script de seeding...")
        try:
            import subprocess
            result = subprocess.run([
                "PYTHONPATH=/app", "python3", "-m", "app.initial_data"
            ], cwd=self.project_root / "backend", capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Datos iniciales creados exitosamente")
                print(result.stdout)
            else:
                print("❌ Error creando datos iniciales")
                print(result.stderr)

        except Exception as e:
            print(f"❌ Error ejecutando script de seeding: {e}")
            print("Puedes ejecutar manualmente: python -m app.initial_data")

    def test_installation(self):
        """Probar la instalación"""
        print("\n🧪 Probando Instalación...")

        try:
            # Verificar que los servicios se levanten
            result = subprocess.run([
                "docker-compose", "ps"
            ], cwd=self.project_root, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Servicios Docker están ejecutándose")
                return True
            else:
                print("❌ Error en los servicios Docker")
                print(result.stderr)
                return False

        except Exception as e:
            print(f"❌ Error probando la instalación: {e}")
            return False

    def show_next_steps(self):
        """Mostrar próximos pasos"""
        print("\n" + "="*60)
        print("🎉 ¡INSTALACIÓN COMPLETADA!")
        print("="*60)
        print("\n📋 Próximos pasos:")
        print("1. Levantar todos los servicios:")
        print("   docker-compose up -d")
        print("\n2. Verificar instalación:")
        print("   python scripts/verify_installation.py")
        print("\n3. Acceder a la aplicación:")
        print("   - Frontend: http://localhost:7701")
        print("   - Backend API: http://localhost:7777")
        print("   - Documentación API: http://localhost:7777/docs")
        print("   - MCP Server: http://localhost:8001/docs")
        print("\n4. Credenciales de acceso:")
        print("   - Usuario: admin@example.com")
        print("   - Contraseña: admin123")
        print("\n📚 Para más información, consulta la documentación:")
        print("   https://github.com/proyecto-semilla/proyecto-semilla")

    def run(self):
        """Ejecutar el instalador"""
        self.print_header()

        # Verificar dependencias Python
        if not check_dependencies():
            sys.exit(1)

        # Verificar prerrequisitos
        if not self.check_prerequisites():
            sys.exit(1)

        # Configurar entorno
        config = self.configure_environment()

        # Crear archivo .env
        self.create_env_file(config)

        # Configurar base de datos
        if not self.setup_database():
            print("❌ Error en la configuración de la base de datos")
            sys.exit(1)

        # Crear superusuario
        self.create_superuser()

        # Probar instalación
        if self.test_installation():
            self.show_next_steps()
        else:
            print("❌ La instalación no se completó correctamente")
            print("Revisa los logs de Docker para más detalles")
            sys.exit(1)


def main():
    """Función principal"""
    try:
        installer = ProyectoSemillaInstaller()
        installer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ Instalación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()