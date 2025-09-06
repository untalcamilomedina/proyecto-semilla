"""
Test Discovery Engine - Pruebas del Motor Principal de Descubrimiento

Pruebas comprehensivas para el motor principal que orquesta
todos los analizadores del Discovery Engine.
"""

import pytest
import tempfile
from pathlib import Path
import os
import json
from unittest.mock import Mock, patch, MagicMock

from ..discovery_engine import (
    DiscoveryEngine, 
    DiscoveryResult, 
    AnalysisMetrics, 
    IntegrationInsight,
    discover_project_architecture
)


class TestDiscoveryEngine:
    """Pruebas del motor principal de descubrimiento"""
    
    def test_initialization_default(self):
        """Test inicialización por defecto"""
        engine = DiscoveryEngine()
        
        assert engine.locale == "es"
        assert engine.i18n is not None
        assert engine.database_analyzer is not None
        assert engine.api_detector is not None
        assert engine.frontend_analyzer is not None
        assert engine.security_mapper is not None
        assert engine.pattern_recognizer is not None
        assert engine.current_analysis is None
        assert engine.is_analyzing is False
    
    def test_initialization_custom_locale(self):
        """Test inicialización con idioma personalizado"""
        engine = DiscoveryEngine(locale="en")
        
        assert engine.locale == "en"
        assert engine.i18n.current_locale == "en"
    
    @pytest.fixture
    def mock_project_structure(self):
        """Fixture que crea estructura de proyecto mock"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Crear estructura básica
            backend_dir = project_path / "backend" / "app"
            frontend_dir = project_path / "frontend" / "src"
            
            backend_dir.mkdir(parents=True)
            frontend_dir.mkdir(parents=True)
            
            # Crear algunos archivos Python
            (backend_dir / "main.py").write_text("""
from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
""")
            
            (backend_dir / "models.py").write_text("""
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    name = Column(String)
""")
            
            # Crear archivo frontend
            (frontend_dir / "App.tsx").write_text("""
import React from 'react';

function App() {
  return <div>Hello World</div>;
}

export default App;
""")
            
            yield str(project_path)
    
    def test_discover_architecture_invalid_path(self):
        """Test descubrimiento con ruta inválida"""
        engine = DiscoveryEngine()
        
        with pytest.raises(FileNotFoundError):
            engine.discover_architecture("/path/that/does/not/exist")
    
    def test_discover_architecture_already_analyzing(self, mock_project_structure):
        """Test error cuando ya hay análisis en progreso"""
        engine = DiscoveryEngine()
        engine.is_analyzing = True
        
        with pytest.raises(RuntimeError, match="Ya hay un análisis en progreso"):
            engine.discover_architecture(mock_project_structure)
    
    @patch('core.discovery.analyzers.database_analyzer.DatabaseAnalyzer.analyze_project')
    @patch('core.discovery.analyzers.api_pattern_detector.APIPatternDetector.analyze_project')
    @patch('core.discovery.analyzers.frontend_analyzer.FrontendAnalyzer.analyze_project')
    @patch('core.discovery.analyzers.security_mapper.SecurityMapper.analyze_project')
    @patch('core.discovery.analyzers.pattern_recognizer.PatternRecognizer.analyze_patterns')
    def test_discover_architecture_success(self, mock_patterns, mock_security, mock_frontend, 
                                         mock_api, mock_database, mock_project_structure):
        """Test descubrimiento exitoso con mocks"""
        # Configurar mocks
        mock_database.return_value = Mock()
        mock_api.return_value = Mock()
        mock_frontend.return_value = Mock()
        mock_security.return_value = Mock()
        mock_patterns.return_value = Mock()
        
        engine = DiscoveryEngine()
        
        # Mock get_analysis_summary methods
        engine.database_analyzer.get_analysis_summary = Mock(return_value={
            "total_models": 3,
            "multi_tenant": True,
            "patterns": ["Repository Pattern"]
        })
        
        engine.api_detector.get_analysis_summary = Mock(return_value={
            "total_endpoints": 15,
            "uses_openapi": True,
            "auth_type": "JWT"
        })
        
        engine.frontend_analyzer.get_analysis_summary = Mock(return_value={
            "framework": "React",
            "total_components": 25,
            "typescript_usage": True
        })
        
        engine.security_mapper.get_analysis_summary = Mock(return_value={
            "security_score": 85,
            "uses_jwt": True,
            "uses_rls": True
        })
        
        engine.pattern_recognizer.get_analysis_summary = Mock(return_value={
            "patterns_detected": 5,
            "architecture_score": 8.5
        })
        
        # Ejecutar análisis
        result = engine.discover_architecture(mock_project_structure, verbose=False)
        
        # Verificar resultado
        assert isinstance(result, DiscoveryResult)
        assert result.project_path == mock_project_structure
        assert result.metrics is not None
        assert result.spanish_report != ""
        assert result.json_summary != {}
        
        # Verificar que se llamaron los analizadores
        mock_database.assert_called_once()
        mock_api.assert_called_once()
        mock_frontend.assert_called_once()
        mock_security.assert_called_once()
        mock_patterns.assert_called_once()
        
        # Verificar que el análisis se guardó
        assert engine.current_analysis == result
        assert engine.is_analyzing is False
    
    def test_discover_architecture_with_errors(self, mock_project_structure):
        """Test descubrimiento con errores en analizadores"""
        engine = DiscoveryEngine()
        
        # Mock para que falle el analizador de base de datos
        with patch.object(engine.database_analyzer, 'analyze_project', 
                         side_effect=Exception("Database analysis failed")):
            with patch.object(engine.database_analyzer, 'get_analysis_summary',
                             return_value={"error": "Database analysis failed"}):
                
                # Mock otros analizadores para que funcionen
                engine.api_detector.analyze_project = Mock()
                engine.api_detector.get_analysis_summary = Mock(return_value={"total_endpoints": 0})
                engine.frontend_analyzer.analyze_project = Mock()
                engine.frontend_analyzer.get_analysis_summary = Mock(return_value={"total_components": 0})
                engine.security_mapper.analyze_project = Mock()
                engine.security_mapper.get_analysis_summary = Mock(return_value={"security_score": 50})
                engine.pattern_recognizer.analyze_patterns = Mock()
                engine.pattern_recognizer.get_analysis_summary = Mock(return_value={"patterns_detected": 0})
                
                result = engine.discover_architecture(mock_project_structure, verbose=False)
                
                # Debería continuar a pesar del error
                assert isinstance(result, DiscoveryResult)
                assert result.metrics.errors_encountered >= 1
                assert "error" in result.database_analysis
    
    def test_analyze_integration_basic(self):
        """Test análisis básico de integración"""
        engine = DiscoveryEngine()
        
        # Crear resultado mock
        result = DiscoveryResult()
        result.database_analysis = {"multi_tenant": True}
        result.api_analysis = {"total_endpoints": 10}
        result.frontend_analysis = {"framework": "React", "total_components": 20}
        result.security_analysis = {"uses_jwt": True, "multi_tenant_security": False}
        
        insights = engine._analyze_integration(result)
        
        assert isinstance(insights, list)
        assert len(insights) > 0
        
        # Debería detectar inconsistencia multi-tenant
        multi_tenant_issues = [i for i in insights if "multi-tenant" in i.title.lower()]
        assert len(multi_tenant_issues) > 0
    
    def test_generate_cross_component_recommendations(self):
        """Test generación de recomendaciones cross-component"""
        engine = DiscoveryEngine()
        
        result = DiscoveryResult()
        result.database_analysis = {"total_models": 10}
        result.api_analysis = {"total_endpoints": 20, "uses_openapi": False}
        result.frontend_analysis = {"total_components": 50}
        result.security_analysis = {"security_score": 60}
        
        recommendations = engine._generate_cross_component_recommendations(result)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Verificar que incluye recomendaciones relevantes
        rec_text = " ".join(recommendations)
        assert "testing" in rec_text or "monitoreo" in rec_text or "documentación" in rec_text
    
    def test_create_architecture_summary(self):
        """Test creación de resumen de arquitectura"""
        engine = DiscoveryEngine()
        
        result = DiscoveryResult()
        result.database_analysis = {
            "total_models": 5,
            "multi_tenant": True,
            "patterns": ["Repository Pattern"]
        }
        result.api_analysis = {
            "total_endpoints": 15,
            "uses_openapi": True,
            "auth_type": "JWT"
        }
        result.frontend_analysis = {
            "framework": "React",
            "total_components": 30,
            "typescript_usage": True
        }
        result.security_analysis = {
            "security_score": 80,
            "uses_jwt": True,
            "uses_rls": True
        }
        result.pattern_analysis = {"patterns_detected": 4}
        result.integration_insights = []
        
        summary = engine._create_architecture_summary(result)
        
        assert isinstance(summary, dict)
        assert "architecture_type" in summary
        assert "complexity_level" in summary
        assert "maturity_level" in summary
        assert "technology_stack" in summary
        assert "key_features" in summary
        assert "key_metrics" in summary
        assert "strengths" in summary
        assert "areas_for_improvement" in summary
        
        # Verificar contenido
        assert summary["key_metrics"]["total_models"] == 5
        assert summary["key_metrics"]["total_endpoints"] == 15
        assert summary["key_metrics"]["security_score"] == 80
        
        assert "Multi-tenant Architecture" in summary["key_features"]
        assert "TypeScript" in summary["key_features"]
    
    def test_calculate_overall_metrics(self):
        """Test cálculo de métricas generales"""
        engine = DiscoveryEngine()
        
        metrics = AnalysisMetrics(start_time=1000.0)
        result = DiscoveryResult()
        result.database_analysis = {"total_models": 5}
        result.api_analysis = {"total_endpoints": 20, "uses_openapi": True}
        result.frontend_analysis = {"total_components": 30, "typescript_usage": True}
        result.security_analysis = {"security_score": 80}
        result.pattern_analysis = {
            "maintainability_score": 7.5,
            "consistency_score": 8.0
        }
        
        engine._calculate_overall_metrics(metrics, result)
        
        assert metrics.overall_architecture_score > 0
        assert metrics.overall_architecture_score <= 10
        assert metrics.maintainability_score == 7.5
        assert metrics.security_score == 8.0  # 80/10
        assert metrics.consistency_score == 8.0
    
    def test_generate_spanish_report(self):
        """Test generación de reporte en español"""
        engine = DiscoveryEngine()
        
        # Crear resultado completo mock
        result = DiscoveryResult()
        result.timestamp = "2024-01-01 12:00:00"
        result.project_path = "/test/project"
        result.metrics = AnalysisMetrics(
            start_time=1000.0,
            end_time=1001.0,
            duration_seconds=1.0,
            overall_architecture_score=8.5,
            maintainability_score=7.5,
            security_score=8.0,
            consistency_score=8.5
        )
        result.database_analysis = {
            "total_models": 5,
            "multi_tenant": True,
            "uses_uuid": True,
            "has_relationships": True
        }
        result.api_analysis = {
            "total_endpoints": 20,
            "uses_openapi": True,
            "auth_type": "JWT",
            "api_version": "v1"
        }
        result.frontend_analysis = {
            "framework": "React",
            "total_components": 30,
            "total_pages": 10,
            "typescript_usage": True,
            "styling_approach": "tailwind"
        }
        result.security_analysis = {
            "uses_rls": True,
            "uses_jwt": True,
            "uses_rbac": True,
            "uses_cors": True,
            "security_score": 85,
            "total_roles": 4,
            "total_rls_policies": 6
        }
        result.pattern_analysis = {"patterns_detected": 4}
        result.architecture_summary = {
            "architecture_type": "Full-Stack Enterprise",
            "complexity_level": "Media",
            "maturity_level": "Madura",
            "technology_stack": {
                "backend": "FastAPI + SQLAlchemy",
                "frontend": "React",
                "database": "PostgreSQL"
            },
            "key_features": ["Multi-tenant Architecture", "TypeScript"],
            "key_metrics": {
                "total_models": 5,
                "total_endpoints": 20,
                "total_components": 30,
                "security_score": 85
            }
        }
        result.cross_component_recommendations = [
            "Implementar testing de integración",
            "Configurar monitoreo distribuido"
        ]
        result.integration_insights = []
        
        report = engine._generate_spanish_report(result)
        
        assert isinstance(report, str)
        assert len(report) > 1000  # Reporte substancial
        assert "Análisis de Arquitectura" in report
        assert "Resumen Ejecutivo" in report
        assert "Stack Tecnológico" in report
        assert "Capa de Base de Datos" in report
        assert "Capa de API" in report
        assert "Capa Frontend" in report
        assert "Modelo de Seguridad" in report
        assert "Recomendaciones" in report
        assert "Métricas de Calidad" in report
        
        # Verificar contenido específico
        assert "8.5/10" in report  # Score general
        assert "FastAPI" in report
        assert "React" in report
        assert "TypeScript" in report
        assert "Multi-tenant" in report
    
    def test_save_results(self, mock_project_structure):
        """Test guardado de resultados"""
        engine = DiscoveryEngine()
        
        # Crear análisis mock
        result = DiscoveryResult()
        result.spanish_report = "# Test Report\nContent"
        result.english_report = "# Test Report EN\nContent"
        result.json_summary = {"test": "data"}
        engine.current_analysis = result
        
        with tempfile.TemporaryDirectory() as temp_dir:
            files = engine.save_results(temp_dir, formats=['json', 'md', 'txt'])
            
            assert 'json' in files
            assert 'md' in files
            assert 'txt' in files
            
            # Verificar que los archivos existen
            assert Path(files['json']).exists()
            assert Path(files['md']).exists()
            assert Path(files['txt']).exists()
            
            # Verificar contenido JSON
            with open(files['json'], 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                assert loaded['test'] == 'data'
    
    def test_save_results_no_analysis(self):
        """Test error al guardar sin análisis"""
        engine = DiscoveryEngine()
        
        with pytest.raises(RuntimeError, match="No hay análisis para guardar"):
            engine.save_results("/tmp")
    
    def test_get_current_analysis(self):
        """Test obtener análisis actual"""
        engine = DiscoveryEngine()
        
        assert engine.get_current_analysis() is None
        
        result = DiscoveryResult()
        engine.current_analysis = result
        
        assert engine.get_current_analysis() == result
    
    def test_clear_analysis(self):
        """Test limpiar análisis actual"""
        engine = DiscoveryEngine()
        
        result = DiscoveryResult()
        engine.current_analysis = result
        
        engine.clear_analysis()
        
        assert engine.current_analysis is None


class TestDiscoveryIntegration:
    """Pruebas de integración del sistema completo"""
    
    @pytest.fixture
    def comprehensive_project_structure(self):
        """Fixture con estructura de proyecto más completa"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Backend structure
            backend_dir = project_path / "backend" / "app"
            backend_dir.mkdir(parents=True)
            
            (backend_dir / "main.py").write_text("""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Test API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"])

@app.get("/api/v1/users")
def get_users():
    return {"users": []}

@app.post("/api/v1/users") 
def create_user():
    return {"created": True}
""")
            
            models_dir = backend_dir / "models"
            models_dir.mkdir()
            
            (models_dir / "user.py").write_text("""
from sqlalchemy import Column, String, Boolean, UUID
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
""")
            
            security_dir = backend_dir / "core"
            security_dir.mkdir()
            
            (security_dir / "security.py").write_text("""
from fastapi import Depends, HTTPException
from jose import jwt
import bcrypt

def get_current_user():
    pass

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

def create_access_token(data: dict):
    return jwt.encode(data, "secret", algorithm="HS256")
""")
            
            # Frontend structure
            frontend_dir = project_path / "frontend" / "src"
            frontend_dir.mkdir(parents=True)
            
            (frontend_dir / "App.tsx").write_text("""
import React, { useState, useEffect } from 'react';

interface User {
  id: string;
  email: string;
}

const App: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  
  useEffect(() => {
    // Fetch users
  }, []);

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold">User Management</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {users.map(user => (
          <div key={user.id} className="bg-white shadow rounded p-4">
            {user.email}
          </div>
        ))}
      </div>
    </div>
  );
};

export default App;
""")
            
            (frontend_dir / "hooks" / "useAuth.ts").write_text("""
import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  
  const login = async (email: string, password: string) => {
    // Login logic
  };
  
  const logout = () => {
    setToken(null);
    setIsAuthenticated(false);
  };
  
  return { isAuthenticated, token, login, logout };
};
""")
            
            # Package.json
            (project_path / "frontend" / "package.json").write_text(json.dumps({
                "name": "test-frontend",
                "dependencies": {
                    "react": "^18.0.0",
                    "next": "^14.0.0",
                    "tailwindcss": "^3.0.0",
                    "@types/react": "^18.0.0",
                    "typescript": "^5.0.0"
                }
            }))
            
            yield str(project_path)
    
    def test_end_to_end_analysis(self, comprehensive_project_structure):
        """Test análisis end-to-end completo"""
        result = discover_project_architecture(
            project_path=comprehensive_project_structure,
            locale="es",
            verbose=False
        )
        
        assert isinstance(result, DiscoveryResult)
        assert result.project_path == comprehensive_project_structure
        
        # Verificar que encontró componentes
        assert result.database_analysis.get("total_models", 0) > 0
        assert result.api_analysis.get("total_endpoints", 0) > 0
        assert result.frontend_analysis.get("total_components", 0) > 0
        
        # Verificar métricas
        assert result.metrics.overall_architecture_score > 0
        assert result.metrics.duration_seconds > 0
        
        # Verificar reporte
        assert len(result.spanish_report) > 500
        assert "Análisis de Arquitectura" in result.spanish_report
        
        # Verificar JSON summary
        assert isinstance(result.json_summary, dict)
        assert "metadata" in result.json_summary
        assert "architecture_summary" in result.json_summary


class TestHelperFunctions:
    """Pruebas de funciones helper"""
    
    def test_discover_project_architecture_function(self):
        """Test función de conveniencia discover_project_architecture"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Crear estructura mínima
            (project_path / "backend").mkdir()
            (project_path / "backend" / "main.py").write_text("# FastAPI app")
            
            with patch('core.discovery.discovery_engine.DiscoveryEngine') as MockEngine:
                mock_engine = MockEngine.return_value
                mock_result = DiscoveryResult()
                mock_engine.discover_architecture.return_value = mock_result
                mock_engine.save_results.return_value = {}
                
                result = discover_project_architecture(
                    project_path=str(project_path),
                    save_to=str(project_path / "results")
                )
                
                assert result == mock_result
                MockEngine.assert_called_once_with(locale="es")
                mock_engine.discover_architecture.assert_called_once()
                mock_engine.save_results.assert_called_once()


if __name__ == "__main__":
    # Ejecutar tests básicos si se ejecuta directamente
    test_instance = TestDiscoveryEngine()
    
    print("🧪 Ejecutando pruebas del Discovery Engine...")
    
    try:
        test_instance.test_initialization_default()
        print("✓ Test inicialización por defecto")
        
        test_instance.test_initialization_custom_locale()
        print("✓ Test inicialización con idioma personalizado")
        
        print("🎉 Pruebas básicas del Discovery Engine pasaron!")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        raise