#!/usr/bin/env python3
"""
Script de verificación de instalación de Proyecto Semilla
Verifica que todos los servicios estén funcionando correctamente
"""

import requests
import time
import sys
from typing import Dict, List

def check_service(url: str, name: str, timeout: int = 10) -> bool:
    """Verificar que un servicio esté respondiendo"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: OK ({url})")
            return True
        else:
            print(f"❌ {name}: Error {response.status_code} ({url})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: No responde ({url}) - {e}")
        return False

def check_login():
    """Verificar que el login funcione"""
    try:
        url = "http://localhost:7777/api/v1/auth/login"
        data = {
            "username": "admin@example.com",
            "password": "admin123"
        }
        response = requests.post(url, data=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if "access_token" in result:
                print("✅ Login: OK (admin@example.com / admin123)")
                return True
            else:
                print("❌ Login: Respuesta inválida")
                return False
        else:
            print(f"❌ Login: Error {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login: Error - {e}")
        return False

def main():
    print("🔍 Verificando instalación de Proyecto Semilla...")
    print("=" * 50)

    services = [
        ("http://localhost:7777/health", "Backend API"),
        ("http://localhost:7701", "Frontend"),
        ("http://localhost:8001/docs", "MCP Server"),
    ]

    all_ok = True

    # Verificar servicios
    for url, name in services:
        if not check_service(url, name):
            all_ok = False

    # Verificar login
    if not check_login():
        all_ok = False

    print("\n" + "=" * 50)
    if all_ok:
        print("🎉 ¡Instalación verificada exitosamente!")
        print("\n📋 Servicios disponibles:")
        print("   - Frontend: http://localhost:7701")
        print("   - Backend API: http://localhost:7777")
        print("   - Documentación API: http://localhost:7777/docs")
        print("   - MCP Server: http://localhost:8001/docs")
        print("\n🔐 Credenciales de acceso:")
        print("   - Usuario: admin@example.com")
        print("   - Contraseña: admin123")
    else:
        print("❌ Algunos servicios no están funcionando correctamente")
        print("Revisa los logs de Docker: docker-compose logs")
        sys.exit(1)

if __name__ == "__main__":
    main()