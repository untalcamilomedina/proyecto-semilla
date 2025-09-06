"""
Test Analyzers - Pruebas de Analizadores Especializados

Pruebas para todos los analizadores especializados del Discovery Engine:
- DatabaseAnalyzer
- APIPatternDetector  
- FrontendAnalyzer
- SecurityMapper
- PatternRecognizer
"""

import pytest
import tempfile
from pathlib import Path
import json
from unittest.mock import Mock, patch

from ..analyzers.database_analyzer import DatabaseAnalyzer, ModelInfo
from ..analyzers.api_pattern_detector import APIPatternDetector, EndpointInfo
from ..analyzers.frontend_analyzer import FrontendAnalyzer, ComponentInfo
from ..analyzers.security_mapper import SecurityMapper, AuthenticationMethod
from ..analyzers.pattern_recognizer import PatternRecognizer, ArchitecturalPattern


class TestDatabaseAnalyzer:
    """Pruebas del analizador de base de datos"""
    
    @pytest.fixture
    def sample_model_file(self):
        """Fixture con archivo de modelo SQLAlchemy de ejemplo"""
        content = '''
"""User model for authentication"""
from sqlalchemy import Column, String, Boolean, UUID, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from uuid import uuid4

Base = declarative_base()

class User(Base):
    """User model representing system users"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary="user_roles")

class Tenant(Base):
    """Tenant model for multi-tenancy"""
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(100), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
'''
        return content
    
    def test_initialization(self):
        """Test inicialización del analizador"""
        analyzer = DatabaseAnalyzer()
        assert analyzer.i18n is not None
        assert analyzer.models_cache == {}
        assert analyzer.analysis_result is None
    
    def test_is_sqlalchemy_model_detection(self, sample_model_file):
        """Test detección de modelos SQLAlchemy"""
        analyzer = DatabaseAnalyzer()
        
        import ast
        tree = ast.parse(sample_model_file)
        
        # Encontrar clases User y Tenant
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        user_class = next(c for c in classes if c.name == "User")
        tenant_class = next(c for c in classes if c.name == "Tenant")
        
        assert analyzer._is_sqlalchemy_model(user_class, sample_model_file)
        assert analyzer._is_sqlalchemy_model(tenant_class, sample_model_file)
    
    def test_extract_model_info(self, sample_model_file):
        """Test extracción de información de modelos"""
        analyzer = DatabaseAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_model_file)
            temp_file = Path(f.name)
        
        try:
            models = analyzer._analyze_model_file(temp_file)
            
            assert len(models) == 2  # User y Tenant
            
            user_model = next(m for m in models if m.name == "User")
            assert user_model.table_name == "users"
            assert user_model.uses_uuid is True
            assert user_model.is_multi_tenant is True
            assert user_model.tenant_column == "tenant_id"
            assert len(user_model.columns) > 0
            assert len(user_model.relationships) > 0
            
        finally:
            temp_file.unlink()
    
    def test_analyze_project_with_mock_files(self):
        """Test análisis de proyecto con archivos mock"""
        analyzer = DatabaseAnalyzer()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            models_dir = project_path / "backend" / "app" / "models"
            models_dir.mkdir(parents=True)
            
            # Crear archivo de modelo
            model_file = models_dir / "user.py"
            model_file.write_text('''
from sqlalchemy import Column, String, UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(100))
''')
            
            result = analyzer.analyze_project(str(project_path))
            
            assert result.total_models >= 1
            assert len(result.models) >= 1
            
            user_model = next((m for m in result.models if m.name == "User"), None)
            assert user_model is not None
            assert user_model.table_name == "users"
    
    def test_generate_report(self):
        """Test generación de reporte"""
        analyzer = DatabaseAnalyzer()
        
        # Mock analysis result
        from ..analyzers.database_analyzer import DatabaseAnalysisResult
        analyzer.analysis_result = DatabaseAnalysisResult()
        analyzer.analysis_result.total_models = 5
        analyzer.analysis_result.multi_tenant_models = 3
        analyzer.analysis_result.uuid_models = 5
        analyzer.analysis_result.patterns_detected = ["Multi-tenant", "UUID Pattern"]
        
        report = analyzer.generate_report()
        
        assert isinstance(report, str)
        assert "Base de Datos" in report
        assert "5" in report  # total models
        assert len(report) > 100


class TestAPIPatternDetector:
    """Pruebas del detector de patrones de API"""
    
    @pytest.fixture
    def sample_fastapi_file(self):
        """Fixture con archivo FastAPI de ejemplo"""
        return '''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user

router = APIRouter()

@router.get("/users/")
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all users"""
    return {"users": []}

@router.post("/users/")
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create new user"""
    return {"created": True}

@router.put("/users/{user_id}")
async def update_user(user_id: str):
    """Update user"""
    return {"updated": True}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user"""
    return {"deleted": True}
'''
    
    def test_initialization(self):
        """Test inicialización del detector"""
        detector = APIPatternDetector()
        assert detector.i18n is not None
        assert detector.analysis_result is None
        assert len(detector.http_methods) > 0
        assert "GET" in detector.http_methods
    
    def test_analyze_endpoint_function(self, sample_fastapi_file):
        """Test análisis de función endpoint"""
        detector = APIPatternDetector()
        
        import ast
        tree = ast.parse(sample_fastapi_file)
        
        # Encontrar función read_users
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        read_users_func = next(f for f in functions if f.name == "read_users")
        
        endpoint_info = detector._analyze_endpoint_function(read_users_func, sample_fastapi_file)
        
        assert endpoint_info is not None
        assert endpoint_info.path == "/users/"
        assert endpoint_info.method == "GET"
        assert endpoint_info.function_name == "read_users"
        assert endpoint_info.requires_auth is True  # Tiene get_current_user
        assert len(endpoint_info.parameters) > 0
        assert len(endpoint_info.dependencies) > 0
    
    def test_analyze_main_file_fastapi_config(self):
        """Test análisis de configuración FastAPI en main.py"""
        detector = APIPatternDetector()
        
        main_content = '''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Test API",
    description="Test API Description", 
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/api/v1/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True
)

app.include_router(api_router, prefix="/api/v1", tags=["api"])
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(main_content)
            temp_file = Path(f.name)
        
        try:
            config = detector._analyze_main_file(temp_file)
            
            assert config["title"] == "Test API"
            assert config["description"] == "Test API Description"
            assert config["version"] == "1.0.0"
            assert config["docs_url"] == "/docs"
            assert config["cors_enabled"] is True
            assert "CORSMiddleware" in config["middleware"]
            
        finally:
            temp_file.unlink()
    
    def test_detect_crud_operations(self, sample_fastapi_file):
        """Test detección de operaciones CRUD"""
        detector = APIPatternDetector()
        
        import ast
        tree = ast.parse(sample_fastapi_file)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        crud_operations = []
        for func in functions:
            endpoint_info = detector._analyze_endpoint_function(func, sample_fastapi_file)
            if endpoint_info:
                crud_operations.append((endpoint_info.method, endpoint_info.function_name))
        
        methods = [op[0] for op in crud_operations]
        assert "GET" in methods
        assert "POST" in methods  
        assert "PUT" in methods
        assert "DELETE" in methods
    
    def test_generate_report(self):
        """Test generación de reporte de API"""
        detector = APIPatternDetector()
        
        # Mock analysis result
        from ..analyzers.api_pattern_detector import APIAnalysisResult
        detector.analysis_result = APIAnalysisResult()
        detector.analysis_result.total_endpoints = 15
        detector.analysis_result.uses_openapi = True
        detector.analysis_result.auth_type = "JWT"
        detector.analysis_result.api_version = "v1"
        detector.analysis_result.patterns_detected = ["RESTful API", "JWT Auth"]
        
        report = detector.generate_report()
        
        assert isinstance(report, str)
        assert "API" in report
        assert "15" in report  # endpoints count
        assert "JWT" in report
        assert len(report) > 100


class TestFrontendAnalyzer:
    """Pruebas del analizador de frontend"""
    
    @pytest.fixture
    def sample_react_component(self):
        """Fixture con componente React de ejemplo"""
        return '''
import React, { useState, useEffect, useContext } from 'react';
import { useRouter } from 'next/router';

interface User {
  id: string;
  name: string;
}

const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  
  useEffect(() => {
    fetchUsers();
  }, []);
  
  const fetchUsers = async () => {
    setLoading(true);
    // Fetch logic
    setLoading(false);
  };
  
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold text-gray-800">Users</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {users.map(user => (
          <div key={user.id} className="bg-white shadow-md rounded p-4">
            <h2 className="text-lg font-semibold">{user.name}</h2>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UserList;
'''
    
    def test_initialization(self):
        """Test inicialización del analizador"""
        analyzer = FrontendAnalyzer()
        assert analyzer.i18n is not None
        assert analyzer.analysis_result is None
        assert len(analyzer.react_hooks) > 0
        assert "useState" in analyzer.react_hooks
    
    def test_is_component_file(self):
        """Test detección de archivos de componentes"""
        analyzer = FrontendAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as f:
            f.write("import React from 'react'; export default App;")
            temp_file = Path(f.name)
        
        try:
            assert analyzer._is_component_file(temp_file) is True
        finally:
            temp_file.unlink()
        
        # Test archivo no componente
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("print('hello')")
            temp_file = Path(f.name)
        
        try:
            assert analyzer._is_component_file(temp_file) is False
        finally:
            temp_file.unlink()
    
    def test_extract_component_details(self, sample_react_component):
        """Test extracción de detalles de componente"""
        analyzer = FrontendAnalyzer()
        
        component_info = ComponentInfo(
            name="UserList",
            file_path="UserList.tsx",
            component_type="functional"
        )
        
        analyzer._extract_component_details(component_info, sample_react_component)
        
        assert component_info.has_state is True  # usa useState
        assert "useState" in component_info.hooks_used
        assert "useEffect" in component_info.hooks_used
        assert "useRouter" in component_info.hooks_used
        assert component_info.styling_approach == "tailwind"  # tiene clases tw-
        assert len(component_info.imports) > 0
    
    def test_analyze_tsx_content(self, sample_react_component):
        """Test análisis de contenido TSX"""
        analyzer = FrontendAnalyzer()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tsx', delete=False) as f:
            f.write(sample_react_component)
            temp_file = Path(f.name)
        
        try:
            components = analyzer._analyze_tsx_content(
                sample_react_component, 
                temp_file, 
                temp_file.parent
            )
            
            assert len(components) >= 1
            
            user_list = next(c for c in components if c.name == "UserList")
            assert user_list.component_type == "functional"
            assert user_list.styling_approach == "tailwind"
            
        finally:
            temp_file.unlink()
    
    def test_analyze_package_json(self):
        """Test análisis de package.json"""
        analyzer = FrontendAnalyzer()
        
        package_data = {
            "name": "test-frontend",
            "dependencies": {
                "react": "^18.0.0",
                "next": "^14.0.0",
                "tailwindcss": "^3.0.0"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "@types/react": "^18.0.0"
            }
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            package_file = Path(temp_dir) / "package.json"
            with open(package_file, 'w') as f:
                json.dump(package_data, f)
            
            result = analyzer._analyze_package_json(Path(temp_dir))
            
            assert result["name"] == "test-frontend"
            assert "react" in result["dependencies"]
            assert "typescript" in result["devDependencies"]
    
    def test_generate_report(self):
        """Test generación de reporte de frontend"""
        analyzer = FrontendAnalyzer()
        
        # Mock analysis result
        from ..analyzers.frontend_analyzer import FrontendAnalysisResult
        analyzer.analysis_result = FrontendAnalysisResult()
        analyzer.analysis_result.framework = "Next.js"
        analyzer.analysis_result.total_components = 25
        analyzer.analysis_result.total_pages = 10
        analyzer.analysis_result.typescript_usage = True
        analyzer.analysis_result.styling_approach = "tailwind"
        analyzer.analysis_result.patterns_detected = ["React Hooks", "TypeScript"]
        
        report = analyzer.generate_report()
        
        assert isinstance(report, str)
        assert "Frontend" in report
        assert "Next.js" in report
        assert "25" in report  # components count
        assert "TypeScript" in report
        assert len(report) > 100


class TestSecurityMapper:
    """Pruebas del mapeador de seguridad"""
    
    @pytest.fixture
    def sample_security_file(self):
        """Fixture con archivo de seguridad de ejemplo"""
        return '''
from jose import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    return jwt.encode(data, "secret", algorithm="HS256")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, "secret", algorithms=["HS256"])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401)
'''
    
    def test_initialization(self):
        """Test inicialización del mapeador"""
        mapper = SecurityMapper()
        assert mapper.i18n is not None
        assert mapper.analysis_result is None
        assert len(mapper.auth_patterns) > 0
        assert "jwt" in mapper.auth_patterns
    
    def test_analyze_authentication_file(self, sample_security_file):
        """Test análisis de archivo de autenticación"""
        mapper = SecurityMapper()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(sample_security_file)
            temp_file = Path(f.name)
        
        try:
            auth_methods = mapper._analyze_authentication_file(temp_file)
            
            assert len(auth_methods) > 0
            
            jwt_method = next((m for m in auth_methods if m.type == "jwt"), None)
            assert jwt_method is not None
            assert "secure_hashing" in jwt_method.features
            assert jwt_method.security_level in ["medium", "high"]
            
        finally:
            temp_file.unlink()
    
    def test_detect_vulnerabilities(self):
        """Test detección de vulnerabilidades"""
        mapper = SecurityMapper()
        
        vulnerable_code = '''
# SQL Injection vulnerability
query = "SELECT * FROM users WHERE id = " + user_id
result = execute(query)

# Hardcoded secret
SECRET_KEY = "hardcoded-secret-123"
password = "admin123"

# Weak crypto
import hashlib
hashed = hashlib.md5(password.encode()).hexdigest()
'''
        
        with tempfile.TemporaryDirectory() as temp_dir:
            vuln_file = Path(temp_dir) / "vulnerable.py"
            vuln_file.write_text(vulnerable_code)
            
            vulnerabilities = mapper._detect_vulnerabilities(temp_dir)
            
            assert len(vulnerabilities) > 0
            
            # Verificar tipos de vulnerabilidades detectadas
            vuln_types = [v.type for v in vulnerabilities]
            assert any("hardcoded" in vtype for vtype in vuln_types)
            assert any("weak_crypto" in vtype for vtype in vuln_types)
    
    def test_extract_rls_policies(self):
        """Test extracción de políticas RLS"""
        mapper = SecurityMapper()
        
        sql_content = '''
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY tenant_isolation ON users
    FOR ALL TO authenticated
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Another policy
CREATE POLICY user_own_data ON profiles
    FOR SELECT TO authenticated
    USING (user_id = current_setting('app.current_user_id')::uuid);
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False) as f:
            f.write(sql_content)
            temp_file = Path(f.name)
        
        try:
            policies = mapper._extract_rls_policies_from_content(sql_content, temp_file)
            
            assert len(policies) >= 2
            
            tenant_policy = next(p for p in policies if p.policy_name == "tenant_isolation")
            assert tenant_policy.table_name == "users"
            assert tenant_policy.command == "ALL"
            
        finally:
            temp_file.unlink()
    
    def test_generate_report(self):
        """Test generación de reporte de seguridad"""
        mapper = SecurityMapper()
        
        # Mock analysis result
        from ..analyzers.security_mapper import SecurityAnalysisResult
        mapper.analysis_result = SecurityAnalysisResult()
        mapper.analysis_result.uses_jwt = True
        mapper.analysis_result.uses_rls = True
        mapper.analysis_result.uses_rbac = True
        mapper.analysis_result.security_score = 85
        mapper.analysis_result.total_roles = 4
        mapper.analysis_result.total_rls_policies = 6
        mapper.analysis_result.patterns_detected = ["JWT Auth", "RLS", "RBAC"]
        
        report = mapper.generate_report()
        
        assert isinstance(report, str)
        assert "Seguridad" in report
        assert "JWT" in report
        assert "RLS" in report
        assert "85/100" in report  # security score
        assert len(report) > 100


class TestPatternRecognizer:
    """Pruebas del reconocedor de patrones con IA"""
    
    def test_initialization(self):
        """Test inicialización del reconocedor"""
        recognizer = PatternRecognizer()
        assert recognizer.i18n is not None
        assert recognizer.analysis_result is None
        assert len(recognizer.architectural_patterns) > 0
        assert "Repository Pattern" in recognizer.architectural_patterns
    
    def test_combine_analyses(self):
        """Test combinación de análisis de diferentes componentes"""
        recognizer = PatternRecognizer()
        
        db_analysis = {"total_models": 5, "multi_tenant": True}
        api_analysis = {"total_endpoints": 15, "uses_openapi": True}
        frontend_analysis = {"framework": "React", "total_components": 30}
        security_analysis = {"security_score": 80, "uses_jwt": True}
        
        combined = recognizer._combine_analyses(
            db_analysis, api_analysis, frontend_analysis, security_analysis
        )
        
        assert combined["total_models"] == 5
        assert combined["multi_tenant"] is True
        assert combined["total_endpoints"] == 15
        assert combined["uses_fastapi"] is False  # No framework info
        assert combined["security_score"] == 80
    
    def test_detect_code_duplication(self):
        """Test detección de duplicación de código"""
        recognizer = PatternRecognizer()
        
        # Código con duplicación
        duplicated_code = '''
def process_user_data(data):
    validated = validate_data(data)
    cleaned = clean_data(validated)
    return cleaned

def process_order_data(data):
    validated = validate_data(data)
    cleaned = clean_data(validated) 
    return cleaned

def process_product_data(data):
    validated = validate_data(data)
    cleaned = clean_data(validated)
    return cleaned
'''
        
        assert recognizer._detect_code_duplication(duplicated_code) is True
        
        # Código sin duplicación significativa
        unique_code = '''
def process_users():
    return get_users()
    
def process_orders():
    return get_orders()
    
def process_products():
    return get_products()
'''
        
        assert recognizer._detect_code_duplication(unique_code) is False
    
    def test_detect_complex_control_flow(self):
        """Test detección de flujo de control complejo"""
        recognizer = PatternRecognizer()
        
        # Código con anidamiento complejo
        complex_code = '''
def complex_function(data):
    if data:
        for item in data:
            if item.valid:
                try:
                    for subitem in item.children:
                        if subitem.active:
                            while subitem.processing:
                                if subitem.ready:
                                    process(subitem)
                except Exception as e:
                    handle_error(e)
'''
        
        assert recognizer._detect_complex_control_flow(complex_code) is True
        
        # Código con flujo simple
        simple_code = '''
def simple_function(data):
    if data:
        return process_data(data)
    return None
'''
        
        assert recognizer._detect_complex_control_flow(simple_code) is False
    
    def test_generate_smart_recommendations(self):
        """Test generación de recomendaciones inteligentes"""
        recognizer = PatternRecognizer()
        
        # Análisis que debería generar recomendaciones
        analysis = {
            "total_models": 10,
            "security_score": 50,  # Score bajo
            "total_endpoints": 30,
            "total_components": 60,
            "code_duplication": 0.4  # Alta duplicación
        }
        
        # Mock patterns y anti-patterns
        patterns = []
        anti_patterns = []
        
        recommendations = recognizer._generate_smart_recommendations(
            analysis, patterns, anti_patterns
        )
        
        assert len(recommendations) > 0
        
        # Verificar que incluye recomendaciones relevantes
        rec_titles = [r.title for r in recommendations]
        security_recs = [r for r in rec_titles if "seguridad" in r.lower()]
        assert len(security_recs) > 0  # Debería recomendar mejorar seguridad
    
    def test_calculate_quality_metrics(self):
        """Test cálculo de métricas de calidad"""
        recognizer = PatternRecognizer()
        
        # Mock analysis result con algunos datos
        from ..analyzers.pattern_recognizer import PatternRecognitionResult
        recognizer.analysis_result = PatternRecognitionResult()
        recognizer.analysis_result.architectural_patterns = [
            ArchitecturalPattern("Repository", "design", 0.8),
            ArchitecturalPattern("MVC", "architectural", 0.7)
        ]
        recognizer.analysis_result.anti_patterns = []
        recognizer.analysis_result.consistency_issues = []
        
        analysis = {"uses_typescript": True, "total_models": 5}
        
        recognizer._calculate_quality_metrics(analysis)
        
        assert recognizer.analysis_result.architecture_score > 0
        assert recognizer.analysis_result.maintainability_score > 0
        assert recognizer.analysis_result.consistency_score > 0
        
        # Con TypeScript debería tener mejor puntuación de mantenibilidad
        assert recognizer.analysis_result.maintainability_score >= 7.0


class TestAnalyzersIntegration:
    """Pruebas de integración entre analizadores"""
    
    def test_analyzers_consistent_output_format(self):
        """Test que todos los analizadores producen formato consistente"""
        # Inicializar todos los analizadores
        db_analyzer = DatabaseAnalyzer()
        api_detector = APIPatternDetector()
        frontend_analyzer = FrontendAnalyzer()
        security_mapper = SecurityMapper()
        
        # Todos deberían tener método get_analysis_summary
        assert hasattr(db_analyzer, 'get_analysis_summary')
        assert hasattr(api_detector, 'get_analysis_summary')
        assert hasattr(frontend_analyzer, 'get_analysis_summary')
        assert hasattr(security_mapper, 'get_analysis_summary')
        
        # Todos deberían tener método generate_report
        assert hasattr(db_analyzer, 'generate_report')
        assert hasattr(api_detector, 'generate_report')
        assert hasattr(frontend_analyzer, 'generate_report')
        assert hasattr(security_mapper, 'generate_report')
    
    def test_i18n_consistency(self):
        """Test que todos los analizadores usan i18n consistentemente"""
        analyzers = [
            DatabaseAnalyzer(),
            APIPatternDetector(),
            FrontendAnalyzer(),
            SecurityMapper(),
            PatternRecognizer()
        ]
        
        for analyzer in analyzers:
            assert hasattr(analyzer, 'i18n')
            assert analyzer.i18n is not None
            
            # Test que pueden generar mensajes en español
            if hasattr(analyzer, 'generate_report'):
                # Mock some basic analysis result
                if hasattr(analyzer, 'analysis_result'):
                    # Set up minimal mock data
                    pass  # Each analyzer has different result structure
    
    @pytest.fixture
    def mini_project_structure(self):
        """Fixture con estructura de proyecto mínima para testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir)
            
            # Backend minimal
            backend_dir = project_path / "backend" / "app"
            backend_dir.mkdir(parents=True)
            
            (backend_dir / "main.py").write_text('''
from fastapi import FastAPI
app = FastAPI(title="Test API")
@app.get("/test")
def test(): return {"test": True}
''')
            
            (backend_dir / "models.py").write_text('''
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class TestModel(Base):
    __tablename__ = "test"
    id = Column(String, primary_key=True)
''')
            
            # Frontend minimal
            frontend_dir = project_path / "frontend" / "src"
            frontend_dir.mkdir(parents=True)
            
            (frontend_dir / "App.tsx").write_text('''
import React from 'react';
const App = () => <div>Test</div>;
export default App;
''')
            
            (project_path / "frontend" / "package.json").write_text(json.dumps({
                "name": "test-app",
                "dependencies": {"react": "^18.0.0"}
            }))
            
            yield str(project_path)
    
    def test_all_analyzers_work_with_mini_project(self, mini_project_structure):
        """Test que todos los analizadores pueden procesar proyecto mínimo"""
        analyzers = [
            ("Database", DatabaseAnalyzer()),
            ("API", APIPatternDetector()),
            ("Frontend", FrontendAnalyzer()),
            ("Security", SecurityMapper())
        ]
        
        for name, analyzer in analyzers:
            try:
                result = analyzer.analyze_project(mini_project_structure)
                assert result is not None
                
                summary = analyzer.get_analysis_summary()
                assert isinstance(summary, dict)
                
                report = analyzer.generate_report()
                assert isinstance(report, str)
                assert len(report) > 0
                
            except Exception as e:
                pytest.fail(f"{name} analyzer failed: {e}")


if __name__ == "__main__":
    # Ejecutar tests básicos si se ejecuta directamente
    print("🧪 Ejecutando pruebas de analizadores...")
    
    try:
        # Test básicos de inicialización
        db_analyzer = TestDatabaseAnalyzer()
        db_analyzer.test_initialization()
        print("✓ DatabaseAnalyzer initialization")
        
        api_detector = TestAPIPatternDetector()
        api_detector.test_initialization()
        print("✓ APIPatternDetector initialization")
        
        frontend_analyzer = TestFrontendAnalyzer()
        frontend_analyzer.test_initialization()
        print("✓ FrontendAnalyzer initialization")
        
        security_mapper = TestSecurityMapper()
        security_mapper.test_initialization()
        print("✓ SecurityMapper initialization")
        
        pattern_recognizer = TestPatternRecognizer()
        pattern_recognizer.test_initialization()
        print("✓ PatternRecognizer initialization")
        
        print("🎉 Todas las pruebas básicas de analizadores pasaron!")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        raise