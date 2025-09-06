#!/usr/bin/env python3
"""
Demo del Architecture Discovery Engine

Demostración interactiva del motor de descubrimiento de arquitectura
que analiza el propio Proyecto Semilla como ejemplo.

Uso:
    python demo.py [--verbose] [--save-results]
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Optional

# Asegurar imports correctos
sys.path.insert(0, str(Path(__file__).parents[2]))

from core.discovery import discover_project_architecture, DiscoveryEngine


def print_banner():
    """Muestra banner de bienvenida"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║    🧠 Architecture Discovery Engine - Demostración          ║
║                                                              ║
║    Motor Inteligente de Análisis de Arquitectura            ║
║    🇪🇸 Completamente en Español                              ║
║                                                              ║
║    Vibecoding Expert System v1.0.0                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_separator(title: str = "", char: str = "=", length: int = 70):
    """Imprime separador con título opcional"""
    if title:
        title_formatted = f" {title} "
        padding = (length - len(title_formatted)) // 2
        separator = char * padding + title_formatted + char * padding
    else:
        separator = char * length
    
    print(f"\n{separator}\n")


def analyze_proyecto_semilla(verbose: bool = True, save_results: bool = False) -> Optional[str]:
    """
    Analiza el Proyecto Semilla como demostración del Discovery Engine
    
    Returns:
        Ruta donde se guardaron los resultados (si save_results=True)
    """
    # Detectar ruta del proyecto (asumiendo que estamos en core/discovery/)
    current_file = Path(__file__)
    project_root = current_file.parents[2]  # Subir 2 niveles desde core/discovery/
    
    print(f"📁 Analizando proyecto: {project_root}")
    print(f"🔍 Modo detallado: {'Activado' if verbose else 'Desactivado'}")
    
    if save_results:
        results_dir = project_root / "discovery_demo_results"
        results_dir.mkdir(exist_ok=True)
        print(f"💾 Resultados se guardarán en: {results_dir}")
    else:
        results_dir = None
    
    print_separator("INICIANDO ANÁLISIS")
    
    try:
        # Ejecutar análisis completo
        start_time = time.time()
        
        result = discover_project_architecture(
            project_path=str(project_root),
            locale="es",
            verbose=verbose,
            save_to=str(results_dir) if results_dir else None
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print_separator("ANÁLISIS COMPLETADO")
        print(f"✅ Análisis completado en {duration:.1f} segundos")
        print(f"📊 Score general de arquitectura: {result.metrics.overall_architecture_score:.1f}/10")
        
        if result.metrics.errors_encountered > 0:
            print(f"⚠️  Se encontraron {result.metrics.errors_encountered} errores (ver detalles abajo)")
        
        return str(results_dir) if results_dir else None
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        return None


def show_quick_stats(project_root: Path):
    """Muestra estadísticas rápidas del proyecto"""
    print_separator("ESTADÍSTICAS RÁPIDAS DEL PROYECTO")
    
    try:
        # Contar archivos por tipo
        python_files = len(list(project_root.rglob("*.py")))
        js_files = len(list(project_root.rglob("*.js")))
        ts_files = len(list(project_root.rglob("*.ts")))
        tsx_files = len(list(project_root.rglob("*.tsx")))
        
        print(f"🐍 Archivos Python: {python_files}")
        print(f"📜 Archivos JavaScript: {js_files}")
        print(f"📘 Archivos TypeScript: {ts_files}")
        print(f"⚛️ Archivos TSX (React): {tsx_files}")
        
        # Verificar directorios principales
        backend_exists = (project_root / "backend").exists()
        frontend_exists = (project_root / "frontend").exists()
        tests_exists = (project_root / "tests").exists()
        
        print(f"\n📂 Estructura detectada:")
        print(f"   Backend: {'✅' if backend_exists else '❌'}")
        print(f"   Frontend: {'✅' if frontend_exists else '❌'}")
        print(f"   Tests: {'✅' if tests_exists else '❌'}")
        
    except Exception as e:
        print(f"Error calculando estadísticas: {e}")


def demonstrate_individual_analyzers(project_root: Path):
    """Demuestra analizadores individuales"""
    print_separator("DEMOSTRACIÓN DE ANALIZADORES INDIVIDUALES")
    
    from core.discovery.analyzers.database_analyzer import DatabaseAnalyzer
    from core.discovery.analyzers.api_pattern_detector import APIPatternDetector
    from core.discovery.analyzers.frontend_analyzer import FrontendAnalyzer
    from core.discovery.analyzers.security_mapper import SecurityMapper
    
    analyzers = [
        ("🗂️ Base de Datos", DatabaseAnalyzer()),
        ("🔌 API Patterns", APIPatternDetector()),
        ("🎨 Frontend", FrontendAnalyzer()),
        ("🔒 Seguridad", SecurityMapper())
    ]
    
    for name, analyzer in analyzers:
        print(f"\n{name}:")
        print("-" * 40)
        
        try:
            start = time.time()
            result = analyzer.analyze_project(str(project_root))
            duration = time.time() - start
            
            summary = analyzer.get_analysis_summary()
            
            print(f"⏱️  Tiempo: {duration:.2f}s")
            
            # Mostrar métricas clave según el tipo de analizador
            if isinstance(analyzer, DatabaseAnalyzer):
                print(f"📊 Modelos encontrados: {summary.get('total_models', 0)}")
                print(f"🔗 Multi-tenant: {'Sí' if summary.get('multi_tenant', False) else 'No'}")
                
            elif isinstance(analyzer, APIPatternDetector):
                print(f"🔌 Endpoints encontrados: {summary.get('total_endpoints', 0)}")
                print(f"📖 OpenAPI: {'Sí' if summary.get('uses_openapi', False) else 'No'}")
                
            elif isinstance(analyzer, FrontendAnalyzer):
                print(f"⚛️ Componentes: {summary.get('total_components', 0)}")
                print(f"📘 TypeScript: {'Sí' if summary.get('typescript_usage', False) else 'No'}")
                
            elif isinstance(analyzer, SecurityMapper):
                print(f"🛡️ Score de seguridad: {summary.get('security_score', 0)}/100")
                print(f"🔑 JWT: {'Sí' if summary.get('uses_jwt', False) else 'No'}")
            
            print("✅ Completado")
            
        except Exception as e:
            print(f"❌ Error: {e}")


def show_interactive_menu():
    """Muestra menú interactivo para diferentes demostraciones"""
    print_separator("MENÚ INTERACTIVO")
    
    options = [
        ("1", "🚀 Análisis Completo del Proyecto Semilla", "full_analysis"),
        ("2", "📊 Estadísticas Rápidas", "quick_stats"),
        ("3", "🔧 Demostración de Analizadores Individuales", "individual_analyzers"),
        ("4", "🧪 Prueba con Proyecto Personalizado", "custom_project"),
        ("5", "🌐 Cambiar Idioma (Español/Inglés)", "change_language"),
        ("6", "❓ Mostrar Información del Sistema", "system_info"),
        ("0", "🚪 Salir", "exit")
    ]
    
    print("Seleccione una opción:")
    for option_key, description, _ in options:
        print(f"   {option_key}. {description}")
    
    return options


def get_system_info():
    """Muestra información del sistema"""
    print_separator("INFORMACIÓN DEL SISTEMA")
    
    import platform
    import psutil
    
    print(f"🖥️  Sistema: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {platform.python_version()}")
    print(f"💾 RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"⚡ CPU: {psutil.cpu_count()} cores")
    
    # Verificar dependencias
    print(f"\n📦 Dependencias:")
    dependencies = [
        ("sqlalchemy", "Análisis de base de datos"),
        ("fastapi", "Detección de patrones API"),
        ("pathlib", "Manejo de archivos"),
        ("ast", "Análisis de código Python")
    ]
    
    for dep, description in dependencies:
        try:
            __import__(dep)
            print(f"   ✅ {dep}: {description}")
        except ImportError:
            print(f"   ❌ {dep}: {description} (FALTANTE)")
    
    # Información del Discovery Engine
    print(f"\n🧠 Discovery Engine:")
    print(f"   Versión: 1.0.0")
    print(f"   Idiomas soportados: Español, Inglés")
    print(f"   Analizadores: 5 (DB, API, Frontend, Security, Patterns)")
    print(f"   Patrones detectables: 8+ arquitectónicos")


def test_custom_project():
    """Permite probar el engine con un proyecto personalizado"""
    print_separator("ANÁLISIS DE PROYECTO PERSONALIZADO")
    
    print("Ingrese la ruta al proyecto que desea analizar:")
    print("(Presione Enter para cancelar)")
    
    project_path = input("Ruta del proyecto: ").strip()
    
    if not project_path:
        print("❌ Operación cancelada")
        return
    
    project_path = Path(project_path)
    
    if not project_path.exists():
        print(f"❌ La ruta no existe: {project_path}")
        return
    
    if not project_path.is_dir():
        print(f"❌ La ruta no es un directorio: {project_path}")
        return
    
    print(f"🔍 Analizando proyecto personalizado: {project_path}")
    
    try:
        result = discover_project_architecture(
            project_path=str(project_path),
            locale="es",
            verbose=True
        )
        
        print_separator("RESULTADOS")
        print(f"✅ Análisis completado")
        print(f"📊 Score: {result.metrics.overall_architecture_score:.1f}/10")
        
        # Mostrar resumen breve
        if result.database_analysis.get("total_models", 0) > 0:
            print(f"🗂️ Modelos de BD: {result.database_analysis['total_models']}")
        
        if result.api_analysis.get("total_endpoints", 0) > 0:
            print(f"🔌 Endpoints API: {result.api_analysis['total_endpoints']}")
        
        if result.frontend_analysis.get("total_components", 0) > 0:
            print(f"⚛️ Componentes: {result.frontend_analysis['total_components']}")
        
    except Exception as e:
        print(f"❌ Error analizando proyecto: {e}")


def run_interactive_demo():
    """Ejecuta demo interactivo"""
    print_banner()
    
    # Detectar proyecto
    current_file = Path(__file__)
    project_root = current_file.parents[2]
    
    while True:
        options = show_interactive_menu()
        
        try:
            choice = input("\nSeleccione una opción (0-6): ").strip()
            
            option_map = {opt[0]: opt[2] for opt in options}
            
            if choice not in option_map:
                print("❌ Opción inválida. Intente nuevamente.")
                continue
            
            action = option_map[choice]
            
            if action == "exit":
                print("\n👋 ¡Gracias por probar el Architecture Discovery Engine!")
                print("🧠 Vibecoding Expert System - Análisis Inteligente en Español")
                break
            
            elif action == "full_analysis":
                save_results = input("¿Guardar resultados? (s/N): ").lower().startswith('s')
                analyze_proyecto_semilla(verbose=True, save_results=save_results)
            
            elif action == "quick_stats":
                show_quick_stats(project_root)
            
            elif action == "individual_analyzers":
                demonstrate_individual_analyzers(project_root)
            
            elif action == "custom_project":
                test_custom_project()
            
            elif action == "change_language":
                print("🌐 Cambio de idioma:")
                print("   Actualmente solo está disponible Español")
                print("   Inglés estará disponible en futuras versiones")
            
            elif action == "system_info":
                get_system_info()
            
            # Pausa para leer resultados
            input("\nPresione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrumpido. ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("Presione Enter para continuar...")


def main():
    """Función principal con argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Demo del Architecture Discovery Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
    python demo.py                    # Demo interactivo
    python demo.py --auto             # Análisis automático
    python demo.py --auto --save      # Análisis automático con guardado
    python demo.py --verbose          # Modo detallado
        """
    )
    
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Ejecutar análisis automático sin menú interactivo"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Mostrar información detallada durante el análisis"
    )
    
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Guardar resultados en archivos"
    )
    
    parser.add_argument(
        "--project", "-p",
        type=str,
        help="Ruta al proyecto a analizar (por defecto: Proyecto Semilla)"
    )
    
    args = parser.parse_args()
    
    if args.auto:
        # Modo automático
        print_banner()
        
        if args.project:
            # Proyecto personalizado
            print(f"🔍 Analizando proyecto personalizado: {args.project}")
            try:
                result = discover_project_architecture(
                    project_path=args.project,
                    locale="es",
                    verbose=args.verbose,
                    save_to="./discovery_results" if args.save else None
                )
                
                print(f"\n✅ Análisis completado!")
                print(f"📊 Score: {result.metrics.overall_architecture_score:.1f}/10")
                
                if args.save:
                    print(f"💾 Resultados guardados en: ./discovery_results")
                
            except Exception as e:
                print(f"❌ Error: {e}")
                sys.exit(1)
        else:
            # Proyecto Semilla por defecto
            results_path = analyze_proyecto_semilla(
                verbose=args.verbose,
                save_results=args.save
            )
            
            if results_path:
                print(f"\n💾 Resultados guardados en: {results_path}")
    else:
        # Modo interactivo
        run_interactive_demo()


if __name__ == "__main__":
    main()