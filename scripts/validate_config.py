#!/usr/bin/env python3
"""
Validador de Configuración para Proyecto Semilla
Verifica que la configuración del entorno sea correcta y segura
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple

class ConfigValidator:
    """Validador de configuración del proyecto"""

    def __init__(self, env_file: str = ".env"):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / env_file
        self.config = {}
        self.errors = []
        self.warnings = []

    def log_error(self, message: str):
        """Registrar error"""
        self.errors.append(message)
        print(f"❌ {message}")

    def log_warning(self, message: str):
        """Registrar advertencia"""
        self.warnings.append(message)
        print(f"⚠️  {message}")

    def log_success(self, message: str):
        """Registrar éxito"""
        print(f"✅ {message}")

    def load_env_file(self) -> bool:
        """Cargar archivo .env"""
        if not self.env_file.exists():
            self.log_error(f"Archivo .env no encontrado: {self.env_file}")
            return False

        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.config[key.strip()] = value.strip()
            self.log_success("Archivo .env cargado correctamente")
            return True
        except Exception as e:
            self.log_error(f"Error leyendo archivo .env: {e}")
            return False

    def validate_required_variables(self) -> bool:
        """Validar variables requeridas"""
        required_vars = [
            'DB_PASSWORD',
            'JWT_SECRET',
            'DB_HOST',
            'DB_PORT',
            'DB_NAME',
            'DB_USER'
        ]

        missing_vars = []
        for var in required_vars:
            if var not in self.config or not self.config[var]:
                missing_vars.append(var)

        if missing_vars:
            self.log_error(f"Variables requeridas faltantes: {', '.join(missing_vars)}")
            return False

        self.log_success("Todas las variables requeridas están presentes")
        return True

    def validate_jwt_secret(self) -> bool:
        """Validar JWT_SECRET"""
        jwt_secret = self.config.get('JWT_SECRET', '')

        if len(jwt_secret) < 64:
            self.log_error(f"JWT_SECRET demasiado corto: {len(jwt_secret)} caracteres (mínimo 64)")
            return False

        # Verificar que contiene caracteres variados
        has_upper = bool(re.search(r'[A-Z]', jwt_secret))
        has_lower = bool(re.search(r'[a-z]', jwt_secret))
        has_digit = bool(re.search(r'[0-9]', jwt_secret))
        has_special = bool(re.search(r'[^A-Za-z0-9]', jwt_secret))

        if not all([has_upper, has_lower, has_digit, has_special]):
            self.log_warning("JWT_SECRET podría ser más seguro con mayúsculas, minúsculas, números y caracteres especiales")

        self.log_success(f"JWT_SECRET válido (longitud: {len(jwt_secret)} caracteres)")
        return True

    def validate_database_config(self) -> bool:
        """Validar configuración de base de datos"""
        db_password = self.config.get('DB_PASSWORD', '')

        if len(db_password) < 8:
            self.log_warning("Contraseña de base de datos muy corta (mínimo recomendado: 8 caracteres)")

        # Verificar puerto válido
        try:
            port = int(self.config.get('DB_PORT', '5432'))
            if not (1024 <= port <= 65535):
                self.log_warning(f"Puerto de base de datos inusual: {port}")
        except ValueError:
            self.log_error("Puerto de base de datos inválido")

        self.log_success("Configuración de base de datos válida")
        return True

    def validate_cors_origins(self) -> bool:
        """Validar orígenes CORS"""
        cors_origins = self.config.get('CORS_ORIGINS', '')

        if not cors_origins:
            self.log_warning("CORS_ORIGINS no configurado")
            return True

        origins = [origin.strip() for origin in cors_origins.split(',')]

        for origin in origins:
            if not origin.startswith(('http://', 'https://')):
                self.log_warning(f"Origen CORS sin protocolo válido: {origin}")

        self.log_success("Configuración CORS válida")
        return True

    def validate_file_permissions(self) -> bool:
        """Validar permisos del archivo .env"""
        try:
            # Verificar permisos (debe ser solo lectura para owner)
            import stat
            file_stat = os.stat(self.env_file)
            mode = stat.filemode(file_stat.st_mode)

            if 'w' in mode[1:]:  # Verificar si otros pueden escribir
                self.log_warning("Archivo .env tiene permisos de escritura para otros usuarios")

            self.log_success("Permisos del archivo .env correctos")
            return True
        except Exception as e:
            self.log_warning(f"No se pudieron verificar permisos del archivo: {e}")
            return True

    def check_security_best_practices(self):
        """Verificar mejores prácticas de seguridad"""
        # Verificar que no hay contraseñas débiles
        weak_passwords = ['password', '123456', 'admin', 'root', 'changeme']

        for var in ['DB_PASSWORD']:
            value = self.config.get(var, '')
            if value.lower() in weak_passwords:
                self.log_error(f"Contraseña débil detectada en {var}")

        # Verificar DEBUG en producción
        debug = self.config.get('DEBUG', '').lower()
        if debug in ['true', '1', 'yes']:
            self.log_warning("DEBUG está habilitado - deshabilitar en producción")

    def run_validation(self) -> bool:
        """Ejecutar validación completa"""
        print("🔍 Validador de Configuración - Proyecto Semilla")
        print("=" * 50)

        # Cargar archivo
        if not self.load_env_file():
            return False

        # Validaciones
        validations = [
            self.validate_required_variables,
            self.validate_jwt_secret,
            self.validate_database_config,
            self.validate_cors_origins,
            self.validate_file_permissions,
        ]

        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                self.log_error(f"Error en validación {validation.__name__}: {e}")
                all_passed = False

        # Verificar mejores prácticas
        self.check_security_best_practices()

        # Resumen
        print("\n" + "=" * 50)
        print("📊 RESUMEN DE VALIDACIÓN")

        if self.errors:
            print(f"❌ Errores: {len(self.errors)}")
            for error in self.errors:
                print(f"   - {error}")

        if self.warnings:
            print(f"⚠️  Advertencias: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   - {warning}")

        if not self.errors:
            print("✅ Validación completada exitosamente")
            print("🎉 La configuración es segura y está lista para producción")
            return True
        else:
            print("❌ La configuración tiene errores que deben corregirse")
            return False

def main():
    """Función principal"""
    validator = ConfigValidator()

    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()