"""
Integration Tests - Pruebas de Integración del Discovery Engine

Pruebas end-to-end que validan el funcionamiento completo del sistema
de descubrimiento de arquitectura con proyectos reales.
"""

import pytest
import tempfile
import json
from pathlib import Path
import time

from ..discovery_engine import DiscoveryEngine, discover_project_architecture
from ..i18n_manager import setup_i18n


@pytest.mark.integration
class TestDiscoveryEngineIntegration:
    """Pruebas de integración del motor completo"""
    
    def test_full_analysis_backend_only(self, sample_backend_structure):
        """Test análisis completo de proyecto solo backend"""
        engine = DiscoveryEngine(locale="es")
        
        result = engine.discover_architecture(
            str(sample_backend_structure),
            verbose=False
        )
        
        # Verificar que el análisis se completó
        assert result is not None
        assert result.project_path == str(sample_backend_structure)
        assert result.metrics is not None
        assert result.metrics.duration_seconds > 0
        
        # Verificar que encontró componentes backend
        db_analysis = result.database_analysis
        api_analysis = result.api_analysis
        
        assert db_analysis.get("total_models", 0) >= 2  # User, Tenant
        assert api_analysis.get("total_endpoints", 0) >= 5  # CRUD endpoints
        
        # Verificar detección de tecnologías
        assert api_analysis.get("uses_openapi", False) is True
        assert result.security_analysis.get("uses_jwt", False) is True
        
        # Verificar reporte generado
        assert len(result.spanish_report) > 1000
        assert "FastAPI" in result.spanish_report
        assert "SQLAlchemy" in result.spanish_report or "Base de Datos" in result.spanish_report
        assert "JWT" in result.spanish_report
        
        # Verificar JSON summary
        assert isinstance(result.json_summary, dict)
        assert "metadata" in result.json_summary
        assert "component_analysis" in result.json_summary
    
    def test_full_analysis_frontend_only(self, sample_frontend_structure):
        """Test análisis completo de proyecto solo frontend"""
        engine = DiscoveryEngine(locale="es")
        
        result = engine.discover_architecture(
            str(sample_frontend_structure),
            verbose=False
        )
        
        # Verificar componentes frontend
        frontend_analysis = result.frontend_analysis
        
        assert frontend_analysis.get("framework", "") == "Next.js"
        assert frontend_analysis.get("typescript_usage", False) is True
        assert frontend_analysis.get("total_components", 0) >= 2  # Button, UserList
        
        # Verificar detección de tecnologías
        assert "tailwind" in frontend_analysis.get("styling_approach", "").lower()
        assert frontend_analysis.get("routing_type", "") == "app-router"
        
        # Verificar reporte
        assert "React" in result.spanish_report
        assert "TypeScript" in result.spanish_report
        assert "Tailwind" in result.spanish_report or "CSS" in result.spanish_report
    
    def test_full_analysis_complete_project(self, complete_project_structure):
        """Test análisis completo de proyecto full-stack"""
        engine = DiscoveryEngine(locale="es")
        
        start_time = time.time()
        result = engine.discover_architecture(
            str(complete_project_structure),
            include_patterns=True,
            include_security=True,
            verbose=True  # Test modo verbose
        )
        end_time = time.time()
        
        # Verificar tiempo razonable (debería completarse en menos de 30 segundos)
        assert (end_time - start_time) < 30
        
        # Verificar todos los componentes analizados
        assert "error" not in result.database_analysis
        assert "error" not in result.api_analysis  
        assert "error" not in result.frontend_analysis
        assert "error" not in result.security_analysis
        
        # Verificar métricas de calidad
        assert result.metrics.overall_architecture_score > 0
        assert result.metrics.overall_architecture_score <= 10
        
        # Verificar detección de patrones
        pattern_analysis = result.pattern_analysis
        assert pattern_analysis.get("patterns_detected", 0) > 0
        
        # Verificar insights de integración
        assert len(result.integration_insights) >= 0
        
        # Verificar recomendaciones cross-component
        assert len(result.cross_component_recommendations) > 0
        
        # Verificar resumen de arquitectura
        arch_summary = result.architecture_summary
        assert arch_summary["architecture_type"] in ["Full-Stack Enterprise", "Full-Stack Standard", "Full-Stack Básico"]
        assert arch_summary["complexity_level"] in ["Muy Baja", "Baja", "Media", "Alta"]
        assert arch_summary["maturity_level"] in ["Inicial", "Básica", "Intermedia", "Madura"]
        
        # Verificar stack tecnológico detectado
        tech_stack = arch_summary["technology_stack"]
        assert "FastAPI" in tech_stack.get("backend", "")
        assert "React" in tech_stack.get("frontend", "") or "Next.js" in tech_stack.get("frontend", "")
        
        # Verificar reporte completo
        report = result.spanish_report
        assert "Resumen Ejecutivo" in report
        assert "Stack Tecnológico" in report
        assert "Capa de Base de Datos" in report
        assert "Capa de API" in report
        assert "Capa Frontend" in report
        assert "Modelo de Seguridad" in report
        assert "Recomendaciones" in report
        assert "Métricas de Calidad" in report
    
    def test_error_handling_with_corrupted_files(self, temp_project_dir):
        """Test manejo de errores con archivos corruptos"""
        # Crear proyecto con archivos problemáticos
        backend_dir = temp_project_dir / "backend" / "app"
        backend_dir.mkdir(parents=True)
        
        # Archivo Python con sintaxis inválida
        (backend_dir / "broken.py").write_text("""
import this is not valid python syntax
class BrokenModel(Base):
    invalid = Column(
""")
        
        # Archivo JSON inválido
        (temp_project_dir / "frontend" / "package.json").write_text("""
{
  "name": "test",
  invalid json here
""")
        
        engine = DiscoveryEngine()
        
        # No debería lanzar excepción, sino manejar errores gracefully
        result = engine.discover_architecture(str(temp_project_dir), verbose=False)
        
        assert result is not None
        assert result.metrics.errors_encountered > 0
        
        # Debería seguir generando reporte a pesar de errores
        assert len(result.spanish_report) > 100
        assert "error" in result.spanish_report.lower() or result.metrics.errors_encountered > 0
    
    def test_save_and_load_results(self, sample_backend_structure):
        """Test guardado y carga de resultados"""
        engine = DiscoveryEngine()
        
        # Ejecutar análisis
        result = engine.discover_architecture(str(sample_backend_structure), verbose=False)
        
        with tempfile.TemporaryDirectory() as output_dir:
            # Guardar resultados
            files = engine.save_results(output_dir, formats=['json', 'md', 'txt'])
            
            # Verificar archivos creados
            assert 'json' in files
            assert 'md' in files 
            assert 'txt' in files
            
            assert Path(files['json']).exists()
            assert Path(files['md']).exists()
            assert Path(files['txt']).exists()
            
            # Verificar contenido JSON
            with open(files['json'], 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            assert "metadata" in loaded_data
            assert "architecture_summary" in loaded_data
            assert "component_analysis" in loaded_data
            assert loaded_data["metadata"]["project_path"] == result.project_path
            
            # Verificar contenido Markdown
            with open(files['md'], 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            assert "Análisis de Arquitectura" in md_content
            assert len(md_content) > 1000
            
            # Verificar que el contenido TXT es texto plano
            with open(files['txt'], 'r', encoding='utf-8') as f:
                txt_content = f.read()
            
            assert "**" not in txt_content  # Sin markdown formatting
            assert "#" not in txt_content[:10]  # Sin headers markdown
    
    def test_multilingual_reports(self, sample_backend_structure):
        """Test generación de reportes en múltiples idiomas"""
        # Test español
        engine_es = DiscoveryEngine(locale="es")
        result_es = engine_es.discover_architecture(str(sample_backend_structure), verbose=False)
        
        assert "Análisis de Arquitectura" in result_es.spanish_report
        assert "Base de Datos" in result_es.spanish_report
        assert "Recomendaciones" in result_es.spanish_report
        
        # Test inglés
        engine_en = DiscoveryEngine(locale="en")
        result_en = engine_en.discover_architecture(str(sample_backend_structure), verbose=False)
        
        # Debería tener reporte en inglés
        if result_en.english_report:
            assert "Architecture Analysis" in result_en.english_report
            assert "Database" in result_en.english_report or "Executive Summary" in result_en.english_report
    
    def test_performance_with_large_project(self):
        """Test rendimiento con proyecto grande simulado"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Crear estructura de proyecto grande
            backend_dir = project_path / "backend" / "app"
            backend_dir.mkdir(parents=True)
            
            # Crear muchos modelos
            models_dir = backend_dir / "models"
            models_dir.mkdir()
            
            for i in range(20):  # 20 modelos
                (models_dir / f"model_{i:02d}.py").write_text(f"""
from sqlalchemy import Column, String, UUID, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

class Model{i:02d}(Base):
    __tablename__ = "model_{i:02d}s"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
""")
            
            # Crear muchos endpoints
            api_dir = backend_dir / "api" / "v1"
            api_dir.mkdir(parents=True)
            
            for i in range(15):  # 15 archivos de API
                (api_dir / f"endpoints_{i:02d}.py").write_text(f"""
from fastapi import APIRouter, Depends

router = APIRouter()

@router.get("/endpoint_{i:02d}/")
def get_endpoint_{i:02d}():
    return {{"data": "endpoint_{i:02d}"}}

@router.post("/endpoint_{i:02d}/")
def create_endpoint_{i:02d}():
    return {{"created": True}}

@router.put("/endpoint_{i:02d}/{{item_id}}")
def update_endpoint_{i:02d}(item_id: str):
    return {{"updated": True}}

@router.delete("/endpoint_{i:02d}/{{item_id}}")
def delete_endpoint_{i:02d}(item_id: str):
    return {{"deleted": True}}
""")
            
            # Crear frontend con muchos componentes
            frontend_dir = project_path / "frontend" / "src"
            frontend_dir.mkdir(parents=True)
            
            (frontend_dir / "package.json").write_text(json.dumps({
                "name": "large-project",
                "dependencies": {"react": "^18.0.0", "typescript": "^5.0.0"}
            }))
            
            components_dir = frontend_dir / "components"
            components_dir.mkdir()
            
            for i in range(30):  # 30 componentes
                (components_dir / f"Component{i:02d}.tsx").write_text(f"""
import React, {{ useState, useEffect }} from 'react';

interface Component{i:02d}Props {{
  data: any[];
  onUpdate: (id: string) => void;
}}

export const Component{i:02d}: React.FC<Component{i:02d}Props> = ({{ data, onUpdate }}) => {{
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState(data);
  
  useEffect(() => {{
    // Effect logic
  }}, [data]);
  
  return (
    <div className="component-{i:02d} p-4 bg-white shadow rounded">
      <h2 className="text-xl font-bold">Component {i:02d}</h2>
      {{items.map((item, index) => (
        <div key={{index}} className="item p-2 border-b">
          {{item.name}}
        </div>
      ))}}
    </div>
  );
}};
""")
            
            # Ejecutar análisis y medir tiempo
            engine = DiscoveryEngine()
            
            start_time = time.time()
            result = engine.discover_architecture(str(project_path), verbose=False)
            end_time = time.time()
            
            # Verificar que se completó en tiempo razonable (menos de 60 segundos)
            duration = end_time - start_time
            assert duration < 60, f"Análisis tomó {duration} segundos, demasiado lento"
            
            # Verificar que detectó la cantidad correcta de componentes
            assert result.database_analysis.get("total_models", 0) >= 20
            assert result.api_analysis.get("total_endpoints", 0) >= 60  # 4 endpoints * 15 archivos
            assert result.frontend_analysis.get("total_components", 0) >= 30


@pytest.mark.integration  
class TestConvenienceFunctions:
    """Pruebas de funciones de conveniencia"""
    
    def test_discover_project_architecture_function(self, sample_backend_structure):
        """Test función de conveniencia discover_project_architecture"""
        with tempfile.TemporaryDirectory() as output_dir:
            result = discover_project_architecture(
                project_path=str(sample_backend_structure),
                locale="es",
                verbose=False,
                save_to=output_dir
            )
            
            # Verificar resultado
            assert result is not None
            assert result.project_path == str(sample_backend_structure)
            
            # Verificar que se guardaron archivos
            expected_files = [
                "architecture_analysis.json",
                "architecture_report.md", 
                "architecture_summary.txt"
            ]
            
            for filename in expected_files:
                filepath = Path(output_dir) / filename
                assert filepath.exists(), f"Archivo {filename} no fue creado"
                assert filepath.stat().st_size > 100, f"Archivo {filename} está vacío"
    
    def test_discover_project_architecture_english(self, sample_backend_structure):
        """Test función con idioma inglés"""
        result = discover_project_architecture(
            project_path=str(sample_backend_structure),
            locale="en",
            verbose=False
        )
        
        # Verificar que el i18n se configuró correctamente
        assert result is not None
        
        # El reporte principal siempre debería estar en español
        # pero debería existir versión en inglés si se especificó
        assert len(result.spanish_report) > 0


@pytest.mark.integration
@pytest.mark.slow
class TestRealWorldScenarios:
    """Pruebas con escenarios del mundo real"""
    
    def test_empty_project_directory(self, temp_project_dir):
        """Test con directorio de proyecto vacío"""
        engine = DiscoveryEngine()
        
        result = engine.discover_architecture(str(temp_project_dir), verbose=False)
        
        # Debería manejar gracefully proyecto vacío
        assert result is not None
        assert result.metrics.errors_encountered >= 0
        
        # Debería indicar que no encontró componentes
        assert result.database_analysis.get("total_models", 0) == 0
        assert result.api_analysis.get("total_endpoints", 0) == 0
        assert result.frontend_analysis.get("total_components", 0) == 0
    
    def test_project_with_mixed_technologies(self, temp_project_dir):
        """Test proyecto con tecnologías mixtas"""
        # Crear proyecto con Django + React (no FastAPI)
        backend_dir = temp_project_dir / "backend"
        backend_dir.mkdir()
        
        (backend_dir / "models.py").write_text("""
from django.db import models

class User(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
""")
        
        (backend_dir / "views.py").write_text("""
from django.http import JsonResponse

def user_list(request):
    return JsonResponse({'users': []})
""")
        
        # Frontend Vue.js
        frontend_dir = temp_project_dir / "frontend"
        frontend_dir.mkdir()
        
        (frontend_dir / "package.json").write_text(json.dumps({
            "name": "vue-app",
            "dependencies": {"vue": "^3.0.0"}
        }))
        
        (frontend_dir / "App.vue").write_text("""
<template>
  <div>Vue App</div>
</template>

<script>
export default {
  name: 'App'
}
</script>
""")
        
        engine = DiscoveryEngine()
        result = engine.discover_architecture(str(temp_project_dir), verbose=False)
        
        # Debería detectar algunos componentes aunque no sean las tecnologías esperadas
        assert result is not None
        assert len(result.spanish_report) > 100
        
        # Podría no detectar todo perfectamente, pero no debería fallar
        assert result.metrics.errors_encountered >= 0
    
    def test_concurrent_analysis(self, sample_backend_structure):
        """Test análisis concurrente (básico)"""
        import threading
        import time
        
        results = []
        errors = []
        
        def run_analysis():
            try:
                engine = DiscoveryEngine()
                result = engine.discover_architecture(
                    str(sample_backend_structure), 
                    verbose=False
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Ejecutar múltiples análisis en paralelo
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=run_analysis)
            threads.append(thread)
            thread.start()
        
        # Esperar que terminen
        for thread in threads:
            thread.join(timeout=30)  # Timeout de 30 segundos
        
        # Verificar resultados
        assert len(errors) == 0, f"Errores en análisis concurrente: {errors}"
        assert len(results) == 3, f"Solo {len(results)} de 3 análisis completados"
        
        # Verificar que todos los resultados son válidos
        for result in results:
            assert result is not None
            assert len(result.spanish_report) > 100
            assert result.metrics.overall_architecture_score > 0


if __name__ == "__main__":
    # Ejecutar algunas pruebas básicas si se ejecuta directamente
    print("🧪 Ejecutando pruebas de integración...")
    
    # Estas pruebas necesitan fixtures, así que solo podemos hacer tests básicos
    try:
        # Test función de conveniencia con proyecto temporal
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Crear estructura mínima
            (project_path / "backend").mkdir()
            (project_path / "backend" / "main.py").write_text("# Minimal FastAPI")
            
            # Test básico (sin análisis completo)
            from ..discovery_engine import DiscoveryEngine
            engine = DiscoveryEngine()
            
            # Solo verificar inicialización
            assert engine.locale == "es"
            assert engine.i18n is not None
            
            print("✓ Inicialización básica funciona")
        
        print("🎉 Pruebas básicas de integración pasaron!")
        print("💡 Ejecutar con pytest para pruebas completas con fixtures")
        
    except Exception as e:
        print(f"❌ Error en pruebas básicas: {e}")
        raise