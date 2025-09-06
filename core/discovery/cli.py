#!/usr/bin/env python3
"""
CLI Principal para Architecture Discovery Engine
🧠 Vibecoding Expert System - Interfaz de Línea de Comandos en Español

Uso:
    vibecoding-discovery analyze [PROYECTO] [--detallado] [--guardar] [--formato FORMAT]
    vibecoding-discovery demo [--interactivo]
    vibecoding-discovery version
    vibecoding-discovery ayuda
    
Ejemplos:
    vibecoding-discovery analyze .                    # Analizar proyecto actual
    vibecoding-discovery analyze /mi/proyecto --guardar  # Analizar y guardar resultados
    vibecoding-discovery demo                         # Demo interactivo
    vibecoding-discovery analyze . --formato json    # Generar solo reporte JSON
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional, List
import json
import time

# Asegurar imports correctos
sys.path.insert(0, str(Path(__file__).parents[2]))

from core.discovery import discover_project_architecture, DiscoveryEngine
from core.discovery.i18n_manager import get_i18n

def crear_parser_cli():
    """Crea el parser principal de CLI en español"""
    parser = argparse.ArgumentParser(
        description='🧠 Architecture Discovery Engine - Análisis Inteligente de Arquitectura',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  🔍 Análisis básico:
    vibecoding-discovery analyze .
    vibecoding-discovery analyze /ruta/a/mi/proyecto

  📊 Análisis detallado con guardado:
    vibecoding-discovery analyze . --detallado --guardar
    vibecoding-discovery analyze . --guardar --salida /tmp/analisis

  🎯 Formatos específicos:
    vibecoding-discovery analyze . --formato json
    vibecoding-discovery analyze . --formato md --guardar

  🚀 Demostración interactiva:
    vibecoding-discovery demo
    vibecoding-discovery demo --interactivo

Para más información: vibecoding-discovery ayuda
        """
    )
    
    subparsers = parser.add_subparsers(dest='comando', help='Comandos disponibles')
    
    # Comando 'analyze'
    parser_analyze = subparsers.add_parser(
        'analyze',
        help='Analizar arquitectura de proyecto',
        aliases=['analizar', 'a']
    )
    parser_analyze.add_argument(
        'proyecto',
        nargs='?',
        default='.',
        help='Ruta al proyecto a analizar (por defecto: directorio actual)'
    )
    parser_analyze.add_argument(
        '--detallado', '-v',
        action='store_true',
        help='Mostrar información detallada durante el análisis'
    )
    parser_analyze.add_argument(
        '--guardar', '-s',
        action='store_true',
        help='Guardar resultados en archivos'
    )
    parser_analyze.add_argument(
        '--salida', '-o',
        help='Directorio donde guardar los resultados'
    )
    parser_analyze.add_argument(
        '--formato', '-f',
        choices=['json', 'md', 'txt', 'todos'],
        default='todos',
        help='Formato de salida (por defecto: todos)'
    )
    parser_analyze.add_argument(
        '--idioma',
        choices=['es', 'en'],
        default='es',
        help='Idioma del análisis (por defecto: español)'
    )
    parser_analyze.add_argument(
        '--incluir-seguridad',
        action='store_true',
        default=True,
        help='Incluir análisis de seguridad (activado por defecto)'
    )
    parser_analyze.add_argument(
        '--incluir-patrones',
        action='store_true',
        default=True,
        help='Incluir reconocimiento de patrones (activado por defecto)'
    )
    
    # Comando 'demo'
    parser_demo = subparsers.add_parser(
        'demo',
        help='Ejecutar demostración del sistema',
        aliases=['demostrar', 'd']
    )
    parser_demo.add_argument(
        '--interactivo', '-i',
        action='store_true',
        help='Modo interactivo con menú de opciones'
    )
    parser_demo.add_argument(
        '--guardar-demo',
        action='store_true',
        help='Guardar resultados de la demostración'
    )
    
    # Comando 'version'
    parser_version = subparsers.add_parser(
        'version',
        help='Mostrar información de versión',
        aliases=['v']
    )
    
    # Comando 'ayuda'
    parser_ayuda = subparsers.add_parser(
        'ayuda',
        help='Mostrar ayuda detallada',
        aliases=['help', 'h']
    )
    parser_ayuda.add_argument(
        'tema',
        nargs='?',
        choices=['analyze', 'demo', 'formatos', 'ejemplos'],
        help='Tema específico de ayuda'
    )
    
    return parser

def mostrar_banner():
    """Muestra el banner principal"""
    banner = """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║    🧠 Architecture Discovery Engine                                ║
║                                                                    ║
║    Motor Inteligente de Análisis de Arquitectura en Español       ║
║    🇪🇸 Vibecoding Expert System v1.0.0                            ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def mostrar_version():
    """Muestra información de versión"""
    version_info = """
🧠 Architecture Discovery Engine v1.0.0
🏗️  Vibecoding Expert System

Componentes:
  • DatabaseAnalyzer        ✅ v1.0
  • APIPatternDetector      ✅ v1.0  
  • FrontendAnalyzer        ✅ v1.0
  • SecurityMapper          ✅ v1.0
  • PatternRecognizer       ✅ v1.0
  • I18nManager             ✅ v1.0

Idiomas soportados: 🇪🇸 Español, 🇺🇸 Inglés
Tecnologías detectadas: FastAPI, React, Next.js, SQLAlchemy, PostgreSQL
    """
    print(version_info)

def mostrar_ayuda(tema: Optional[str] = None):
    """Muestra ayuda detallada por tema"""
    if tema == 'analyze':
        print("""
🔍 COMANDO ANALYZE - Análisis de Arquitectura

El comando 'analyze' es el corazón del sistema. Analiza cualquier proyecto
de software y genera reportes detallados de su arquitectura.

Uso básico:
  vibecoding-discovery analyze [PROYECTO] [OPCIONES]

Opciones principales:
  --detallado, -v          Mostrar progreso detallado
  --guardar, -s            Guardar resultados en archivos
  --salida DIR, -o DIR     Directorio de salida personalizado
  --formato FORMAT         Formato: json, md, txt, todos
  --idioma LANG            Idioma: es (español), en (inglés)

Análisis incluidos:
  ✅ Base de datos (modelos, relaciones, RLS)
  ✅ API (endpoints, autenticación, middleware)  
  ✅ Frontend (componentes, estado, estilos)
  ✅ Seguridad (JWT, RBAC, vulnerabilidades)
  ✅ Patrones (arquitectónicos, anti-patrones)

Ejemplos prácticos:
  vibecoding-discovery analyze .                     # Proyecto actual
  vibecoding-discovery analyze /mi/app --detallado  # Con progreso  
  vibecoding-discovery analyze . --guardar          # Guardar reportes
  vibecoding-discovery analyze . --formato json     # Solo JSON
        """)
        
    elif tema == 'demo':
        print("""
🚀 COMANDO DEMO - Demostración Interactiva

El comando 'demo' ejecuta una demostración del sistema usando el propio
Proyecto Semilla como ejemplo.

Uso básico:
  vibecoding-discovery demo [OPCIONES]

Opciones:
  --interactivo, -i        Menú interactivo paso a paso
  --guardar-demo          Guardar resultados de demo

Qué hace el demo:
  1. 🔍 Analiza la arquitectura del Proyecto Semilla
  2. 📊 Muestra métricas de calidad en tiempo real  
  3. 🎯 Demuestra detección de patrones arquitectónicos
  4. 🔒 Evalúa modelo de seguridad y vulnerabilidades
  5. 💡 Genera recomendaciones contextualizadas

Perfecto para:
  • Evaluación inicial del sistema
  • Demos a stakeholders técnicos
  • Validación de capacidades antes de uso en producción
        """)
        
    elif tema == 'formatos':
        print("""
📄 FORMATOS DE SALIDA DISPONIBLES

El sistema genera reportes en múltiples formatos según tus necesidades:

Formatos disponibles:
  
  📊 JSON (--formato json)
    • Datos estructurados para integración
    • APIs y automatización
    • Análisis programático
    
  📝 Markdown (--formato md)  
    • Reportes ejecutivos elegantes
    • Documentación técnica
    • GitHub, wikis, Notion
    
  📄 Texto (--formato txt)
    • Reportes simples para terminal
    • Logs y herramientas CLI
    • Integración con scripts
    
  📋 Todos (--formato todos) [Por defecto]
    • Genera los 3 formatos anteriores
    • Máxima flexibilidad
    • Recomendado para uso general

Estructura de archivos generados:
  📁 resultados/
  ├── 📊 architecture_analysis.json      # Datos estructurados
  ├── 📝 architecture_report.md          # Reporte ejecutivo  
  └── 📄 architecture_summary.txt        # Resumen simple
        """)
        
    elif tema == 'ejemplos':
        print("""
💡 EJEMPLOS PRÁCTICOS DE USO

🔍 Análisis Rápido:
  vibecoding-discovery analyze .
  → Analiza proyecto actual, muestra en pantalla

📊 Análisis Completo con Guardado:
  vibecoding-discovery analyze /mi/proyecto --detallado --guardar
  → Análisis completo con progreso y archivos guardados

🎯 Análisis para CI/CD:
  vibecoding-discovery analyze . --formato json --salida ./reports
  → Solo JSON para integración automatizada

🌐 Análisis Multiidioma:
  vibecoding-discovery analyze . --idioma en --guardar  
  → Reportes en inglés guardados

🚀 Demo Interactivo:
  vibecoding-discovery demo --interactivo
  → Demostración paso a paso con menú

📈 Evaluación de Proyecto Existente:
  vibecoding-discovery analyze /legacy-app --detallado --guardar --salida ./audit
  → Auditoría completa de aplicación legacy

🔒 Focus en Seguridad:
  vibecoding-discovery analyze . --incluir-seguridad --formato md
  → Análisis con énfasis en seguridad, reporte Markdown

Para casos específicos, combina opciones según tus necesidades.
        """)
    else:
        print("""
🎯 AYUDA GENERAL - Architecture Discovery Engine

Comandos disponibles:

  🔍 analyze    Analizar arquitectura de proyecto
  🚀 demo       Ejecutar demostración interactiva  
  📋 version    Mostrar información de versión
  ❓ ayuda      Mostrar esta ayuda

Para ayuda específica:
  vibecoding-discovery ayuda analyze     # Análisis de proyectos
  vibecoding-discovery ayuda demo        # Demostración  
  vibecoding-discovery ayuda formatos    # Formatos de salida
  vibecoding-discovery ayuda ejemplos    # Ejemplos prácticos

Inicio rápido:
  vibecoding-discovery demo              # Ejecutar demo
  vibecoding-discovery analyze .         # Analizar proyecto actual
        """)

def ejecutar_analisis(args):
    """Ejecuta análisis de arquitectura según argumentos CLI"""
    proyecto_path = Path(args.proyecto).resolve()
    
    if not proyecto_path.exists():
        print(f"❌ Error: La ruta '{proyecto_path}' no existe")
        sys.exit(1)
        
    if not proyecto_path.is_dir():
        print(f"❌ Error: '{proyecto_path}' no es un directorio")
        sys.exit(1)
    
    print(f"📁 Analizando proyecto: {proyecto_path}")
    if args.detallado:
        print(f"🔍 Modo detallado: Activado")
    if args.guardar:
        salida = args.salida or str(proyecto_path / "architecture_analysis_results")
        print(f"💾 Resultados se guardarán en: {salida}")
    
    print("\n" + "="*60)
    print("🔍 INICIANDO ANÁLISIS DE ARQUITECTURA")
    print("="*60 + "\n")
    
    try:
        # Ejecutar análisis
        start_time = time.time()
        
        result = discover_project_architecture(
            project_path=str(proyecto_path),
            locale=args.idioma,
            verbose=args.detallado,
            save_to=args.salida if args.guardar else None
        )
        
        duration = time.time() - start_time
        
        print("\n" + "="*60)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*60)
        
        print(f"⏱️  Duración: {duration:.1f} segundos")
        print(f"📈 Score general: {result.metrics.overall_architecture_score:.1f}/10")
        
        # Mostrar resumen de componentes
        if hasattr(result, 'database_analysis'):
            db_models = result.database_analysis.get('total_models', 0)
            print(f"📊 Modelos de BD: {db_models}")
            
        if hasattr(result, 'api_analysis'):  
            api_endpoints = result.api_analysis.get('total_endpoints', 0)
            print(f"🔌 Endpoints API: {api_endpoints}")
            
        if hasattr(result, 'frontend_analysis'):
            frontend_components = result.frontend_analysis.get('total_components', 0) 
            print(f"🎨 Componentes Frontend: {frontend_components}")
            
        if hasattr(result, 'security_analysis'):
            security_score = result.security_analysis.get('security_score', 0)
            print(f"🔒 Score Seguridad: {security_score:.0f}/100")
        
        if args.guardar:
            salida_final = args.salida or str(proyecto_path / "architecture_analysis_results")
            print(f"\n💾 Resultados guardados en: {salida_final}")
        
        print("\n🎯 Para más detalles, usa --detallado o revisa los archivos guardados")
        
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        if args.detallado:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def ejecutar_demo(args):
    """Ejecuta la demostración del sistema"""
    from core.discovery.demo import main as demo_main
    
    # Preparar argumentos para el demo
    demo_args = []
    if not args.interactivo:
        demo_args.append('--auto')
    if args.guardar_demo:
        demo_args.append('--save')
    
    # Ejecutar demo
    sys.argv = ['demo.py'] + demo_args
    demo_main()

def main():
    """Función principal de CLI"""
    parser = crear_parser_cli()
    args = parser.parse_args()
    
    if not args.comando:
        mostrar_banner()
        parser.print_help()
        sys.exit(1)
    
    if args.comando in ['version', 'v']:
        mostrar_version()
        
    elif args.comando in ['ayuda', 'help', 'h']:
        mostrar_ayuda(args.tema if hasattr(args, 'tema') else None)
        
    elif args.comando in ['analyze', 'analizar', 'a']:
        if not args.detallado:
            mostrar_banner()
        ejecutar_analisis(args)
        
    elif args.comando in ['demo', 'demostrar', 'd']:
        ejecutar_demo(args)
        
    else:
        print(f"❌ Comando desconocido: {args.comando}")
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()