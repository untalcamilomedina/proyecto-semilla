#!/usr/bin/env python3
"""
Generador de contraseñas seguras para Proyecto Semilla
Genera contraseñas aleatorias seguras y sus hashes
"""

import sys
import os
import secrets
import string
from pathlib import Path

# Agregar backend al path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

def generate_secure_password(length: int = 16) -> str:
    """Generar una contraseña segura aleatoria"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_dependencies():
    """Verificar dependencias necesarias"""
    try:
        from app.core.security import get_password_hash
        return True
    except ImportError as e:
        print(f"❌ Error: No se puede importar app.core.security: {e}")
        print("Asegúrate de que el backend esté configurado correctamente.")
        return False

def main():
    """Función principal"""
    if not check_dependencies():
        sys.exit(1)

    from app.core.security import get_password_hash

    # Generar contraseña aleatoria
    password = generate_secure_password(16)
    hashed_password = get_password_hash(password)

    print("🔐 Generador de Contraseñas Seguras - Proyecto Semilla")
    print("=" * 50)
    print(f"Contraseña generada: {password}")
    print(f"Hash bcrypt: {hashed_password}")
    print(f"Longitud: {len(password)} caracteres")
    print("\n⚠️  IMPORTANTE: Guarda la contraseña en un lugar seguro")
    print("Esta contraseña no se puede recuperar una vez generada.")

if __name__ == "__main__":
    main()