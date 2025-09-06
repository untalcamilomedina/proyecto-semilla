# Architecture Discovery Engine - Documentación Técnica

## 🏗️ Arquitectura del Sistema

### Visión General

El Architecture Discovery Engine es un sistema modular de análisis de arquitectura que utiliza múltiples analizadores especializados coordinados por un motor central. Diseñado siguiendo principios SOLID y patrones de arquitectura limpia.

```
┌─────────────────────────────────────────────────────────────┐
│                    Discovery Engine                          │
│                  (Orquestador Central)                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   I18n Manager  │  │ Pattern Recog.  │  │ Integration     │ │
│  │   (es/en)       │  │ (AI Engine)     │  │ Analyzer        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│              Analizadores Especializados                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │  Database   │ │     API     │ │  Frontend   │ │  Security   │ │
│  │  Analyzer   │ │   Pattern   │ │  Analyzer   │ │   Mapper    │ │
│  │             │ │  Detector   │ │             │ │             │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                  Capa de Resultados                         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │   Spanish   │ │   English   │ │    JSON     │ │   Metrics   │ │
│  │   Report    │ │   Report    │ │  Summary    │ │ Dashboard   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Patrones Arquitectónicos Aplicados

#### 1. **Strategy Pattern** - Analizadores Intercambiables
```python
class AnalyzerStrategy:
    def analyze_project(self, path: str) -> AnalysisResult:
        raise NotImplementedError
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        raise NotImplementedError

class DatabaseAnalyzer(AnalyzerStrategy):
    # Implementación específica para base de datos
    pass

class APIPatternDetector(AnalyzerStrategy):
    # Implementación específica para API
    pass
```

#### 2. **Observer Pattern** - Sistema de Eventos
```python
class AnalysisEventManager:
    def __init__(self):
        self.observers = []
    
    def notify(self, event: AnalysisEvent):
        for observer in self.observers:
            observer.on_analysis_event(event)

class ProgressReporter(AnalysisObserver):
    def on_analysis_event(self, event):
        if event.type == "component_analyzed":
            print(f"Componente {event.component} analizado")
```

#### 3. **Factory Pattern** - Creación de Analizadores
```python
class AnalyzerFactory:
    @staticmethod
    def create_analyzer(analyzer_type: str) -> AnalyzerStrategy:
        if analyzer_type == "database":
            return DatabaseAnalyzer()
        elif analyzer_type == "api":
            return APIPatternDetector()
        # ... más tipos
```

#### 4. **Decorator Pattern** - Extensibilidad de Análisis
```python
class TimingAnalyzerDecorator:
    def __init__(self, analyzer: AnalyzerStrategy):
        self.analyzer = analyzer
        self.timing_data = {}
    
    def analyze_project(self, path: str):
        start = time.time()
        result = self.analyzer.analyze_project(path)
        end = time.time()
        self.timing_data['duration'] = end - start
        return result
```

## 🔧 Componentes Principales

### DiscoveryEngine - Motor Central

**Responsabilidades:**
- Coordinar ejecución de todos los analizadores
- Gestionar flujo de análisis y dependencias
- Generar insights de integración cross-component
- Calcular métricas unificadas de calidad
- Producir reportes ejecutivos

**Algoritmo de Análisis:**
```python
def discover_architecture(self, project_path: str) -> DiscoveryResult:
    # 1. Validación y configuración inicial
    self._validate_project_path(project_path)
    metrics = AnalysisMetrics(start_time=time.time())
    
    # 2. Análisis paralelo de componentes independientes
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(self.database_analyzer.analyze_project, project_path): 'database',
            executor.submit(self.api_detector.analyze_project, project_path): 'api',
            executor.submit(self.frontend_analyzer.analyze_project, project_path): 'frontend'
        }
        
        # 3. Recolectar resultados
        component_results = {}
        for future in as_completed(futures):
            component_type = futures[future]
            try:
                component_results[component_type] = future.result()
            except Exception as e:
                logger.error(f"Error en análisis de {component_type}: {e}")
                component_results[component_type] = {"error": str(e)}
    
    # 4. Análisis de seguridad (dependiente de otros componentes)
    security_result = self.security_mapper.analyze_project(
        project_path, component_results
    )
    
    # 5. Reconocimiento de patrones con IA
    pattern_result = self.pattern_recognizer.analyze_patterns(
        component_results['database'],
        component_results['api'],
        component_results['frontend'],
        security_result,
        project_path
    )
    
    # 6. Análisis de integración y síntesis
    integration_insights = self._analyze_cross_component_integration(component_results)
    
    # 7. Generación de reportes y métricas finales
    return self._synthesize_results(component_results, integration_insights, metrics)
```

### I18nManager - Sistema de Internacionalización

**Arquitectura de Localización:**
```python
class I18nManager:
    def __init__(self, default_locale="es"):
        self.translations = self._load_translations()
        self.fallback_chain = self._build_fallback_chain(default_locale)
        self.interpolation_engine = MessageInterpolator()
    
    def _load_translations(self) -> Dict[str, Dict]:
        """Carga traducciones con cache inteligente y lazy loading"""
        translations = {}
        for locale_file in self.locales_dir.glob("*.json"):
            locale_code = locale_file.stem
            translations[locale_code] = self._load_locale_file(locale_file)
        return translations
    
    def t(self, key: str, **kwargs) -> str:
        """Traducción con fallback automático y validación"""
        for locale in self.fallback_chain:
            if translation := self._get_translation_for_locale(key, locale):
                return self.interpolation_engine.interpolate(translation, **kwargs)
        
        # Fallback final: devolver la clave para debugging
        logger.warning(f"Traducción no encontrada: {key}")
        return f"[{key}]"
```

**Sistema de Fallback:**
```
Español (es) → Inglés (en) → Clave original → Error
```

### DatabaseAnalyzer - Analizador de Base de Datos

**Técnicas de Análisis:**

1. **AST Parsing** para análisis estático de código Python:
```python
def _analyze_model_file(self, file_path: Path) -> List[ModelInfo]:
    with open(file_path) as f:
        source = f.read()
    
    tree = ast.parse(source)
    models = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if self._is_sqlalchemy_model(node, source):
                model_info = self._extract_model_metadata(node, source)
                models.append(model_info)
    
    return models
```

2. **Introspección de SQLAlchemy** para modelos ya cargados:
```python
def _introspect_loaded_models(self) -> List[ModelInfo]:
    """Analiza modelos SQLAlchemy ya cargados en memoria"""
    models = []
    for cls in Base.__subclasses__():
        model_info = self._analyze_sqlalchemy_class(cls)
        models.append(model_info)
    return models
```

3. **Detección de Patrones Arquitectónicos:**
```python
def _detect_architectural_patterns(self, models: List[ModelInfo]) -> List[str]:
    patterns = []
    
    # Multi-tenancy
    if self._has_tenant_isolation(models):
        patterns.append("Multi-Tenant Architecture")
    
    # UUID Pattern
    if self._uses_uuid_consistently(models):
        patterns.append("UUID Primary Keys")
    
    # Soft Delete Pattern
    if self._has_soft_delete(models):
        patterns.append("Soft Delete Pattern")
    
    return patterns
```

### APIPatternDetector - Detector de Patrones de API

**Análisis Multi-Nivel:**

1. **Nivel de Aplicación** - Configuración FastAPI:
```python
def _analyze_fastapi_app_config(self, main_file: Path) -> Dict[str, Any]:
    config = {
        "openapi_config": self._extract_openapi_config(),
        "middleware_stack": self._analyze_middleware_stack(),
        "cors_configuration": self._analyze_cors_setup(),
        "exception_handling": self._analyze_exception_handlers()
    }
    return config
```

2. **Nivel de Router** - Organización de endpoints:
```python
def _analyze_router_structure(self, router_files: List[Path]) -> List[RouterInfo]:
    routers = []
    for router_file in router_files:
        router_info = RouterInfo(
            name=router_file.stem,
            prefix=self._extract_router_prefix(router_file),
            endpoints=self._analyze_router_endpoints(router_file),
            middleware=self._detect_router_middleware(router_file)
        )
        routers.append(router_info)
    return routers
```

3. **Nivel de Endpoint** - Análisis individual de rutas:
```python
def _analyze_endpoint_function(self, func_node: ast.FunctionDef, context: str) -> EndpointInfo:
    endpoint = EndpointInfo(
        path=self._extract_route_path(func_node),
        method=self._extract_http_method(func_node),
        authentication=self._detect_auth_requirements(func_node),
        validation=self._analyze_input_validation(func_node),
        serialization=self._detect_response_serialization(func_node)
    )
    return endpoint
```

### FrontendAnalyzer - Analizador de Frontend

**Estrategias de Análisis:**

1. **Análisis de Componentes React:**
```python
def _analyze_react_component(self, component_file: Path) -> ComponentInfo:
    with open(component_file) as f:
        source = f.read()
    
    component = ComponentInfo(
        name=self._extract_component_name(source),
        hooks_used=self._detect_react_hooks(source),
        props_interface=self._analyze_props_typescript(source),
        state_management=self._detect_state_patterns(source),
        styling_approach=self._analyze_styling_method(source)
    )
    
    return component
```

2. **Análisis de Arquitectura Next.js:**
```python
def _analyze_nextjs_structure(self, frontend_path: Path) -> Dict[str, Any]:
    structure = {
        "routing_type": self._detect_routing_pattern(frontend_path),
        "app_directory": self._analyze_app_directory(frontend_path),
        "pages_directory": self._analyze_pages_directory(frontend_path),
        "api_routes": self._detect_api_routes(frontend_path),
        "middleware": self._analyze_nextjs_middleware(frontend_path)
    }
    return structure
```

3. **Análisis de Dependencias y Tecnologías:**
```python
def _analyze_technology_stack(self, package_json: Dict) -> TechnologyStack:
    dependencies = package_json.get("dependencies", {})
    dev_dependencies = package_json.get("devDependencies", {})
    
    stack = TechnologyStack(
        framework=self._detect_react_framework(dependencies),
        typescript=self._has_typescript(dependencies, dev_dependencies),
        styling=self._detect_styling_solution(dependencies),
        state_management=self._detect_state_management(dependencies),
        testing=self._detect_testing_framework(dev_dependencies)
    )
    
    return stack
```

### SecurityMapper - Mapeador de Seguridad

**Metodología de Análisis:**

1. **Análisis de Superficie de Ataque:**
```python
def _analyze_attack_surface(self, project_path: str) -> AttackSurface:
    surface = AttackSurface(
        exposed_endpoints=self._find_public_endpoints(),
        authentication_points=self._identify_auth_boundaries(),
        data_access_points=self._map_data_access_patterns(),
        external_integrations=self._detect_external_apis()
    )
    return surface
```

2. **Análisis de Controles de Seguridad:**
```python
def _evaluate_security_controls(self) -> SecurityControlsAssessment:
    controls = SecurityControlsAssessment(
        authentication=self._assess_authentication_strength(),
        authorization=self._assess_authorization_model(),
        data_protection=self._assess_data_protection(),
        input_validation=self._assess_input_validation(),
        session_management=self._assess_session_security()
    )
    return controls
```

3. **Detección de Vulnerabilidades:**
```python
def _scan_for_vulnerabilities(self, codebase: str) -> List[SecurityVulnerability]:
    vulnerabilities = []
    
    # OWASP Top 10 patterns
    for pattern_name, pattern_config in self.vulnerability_patterns.items():
        matches = self._scan_pattern(codebase, pattern_config)
        for match in matches:
            vuln = SecurityVulnerability(
                type=pattern_name,
                severity=self._assess_severity(match),
                location=match.location,
                description=pattern_config["description"],
                mitigation=self._generate_mitigation_advice(pattern_name)
            )
            vulnerabilities.append(vuln)
    
    return vulnerabilities
```

### PatternRecognizer - Motor de IA

**Algoritmo de Reconocimiento de Patrones:**

1. **Extracción de Características:**
```python
def _extract_architectural_features(self, codebase_analysis: Dict) -> FeatureVector:
    features = FeatureVector()
    
    # Características estructurales
    features.add("model_count", codebase_analysis["database"]["total_models"])
    features.add("endpoint_count", codebase_analysis["api"]["total_endpoints"])
    features.add("component_count", codebase_analysis["frontend"]["total_components"])
    
    # Características relacionales
    features.add("relationship_density", self._calculate_relationship_density())
    features.add("coupling_score", self._calculate_coupling_score())
    features.add("cohesion_score", self._calculate_cohesion_score())
    
    # Características de calidad
    features.add("test_coverage", self._estimate_test_coverage())
    features.add("documentation_score", self._assess_documentation_quality())
    
    return features
```

2. **Clasificación de Patrones:**
```python
def _classify_architectural_patterns(self, features: FeatureVector) -> List[PatternMatch]:
    pattern_matches = []
    
    for pattern_name, pattern_definition in self.pattern_knowledge_base.items():
        confidence = self._calculate_pattern_confidence(features, pattern_definition)
        
        if confidence > self.confidence_threshold:
            match = PatternMatch(
                pattern=pattern_name,
                confidence=confidence,
                evidence=self._collect_evidence(features, pattern_definition),
                benefits=pattern_definition.benefits,
                implementation_quality=self._assess_implementation_quality(features, pattern_definition)
            )
            pattern_matches.append(match)
    
    return sorted(pattern_matches, key=lambda x: x.confidence, reverse=True)
```

3. **Generación de Recomendaciones:**
```python
def _generate_smart_recommendations(self, analysis_context: AnalysisContext) -> List[SmartRecommendation]:
    recommendations = []
    
    # Reglas basadas en contexto
    for rule in self.recommendation_rules:
        if rule.condition(analysis_context):
            rec = SmartRecommendation(
                title=rule.title,
                description=rule.description,
                priority=rule.calculate_priority(analysis_context),
                implementation_steps=rule.generate_steps(analysis_context),
                estimated_effort=rule.estimate_effort(analysis_context),
                expected_impact=rule.calculate_impact(analysis_context)
            )
            recommendations.append(rec)
    
    # Análisis de gaps arquitectónicos
    gaps = self._identify_architectural_gaps(analysis_context)
    for gap in gaps:
        recommendations.extend(self._generate_gap_recommendations(gap))
    
    # Priorización basada en valor/esfuerzo
    return self._prioritize_recommendations(recommendations)
```

## 🔍 Algoritmos Clave

### Algoritmo de Detección Multi-Tenant

```python
def _detect_multitenant_architecture(self, models: List[ModelInfo]) -> MultiTenantAnalysis:
    """
    Detecta arquitectura multi-tenant usando múltiples heurísticas
    """
    evidence = MultiTenantEvidence()
    
    # 1. Análisis de columnas tenant
    for model in models:
        tenant_columns = [col for col in model.columns 
                         if any(pattern in col.name.lower() 
                               for pattern in ['tenant', 'org', 'company'])]
        if tenant_columns:
            evidence.add_model_evidence(model.name, tenant_columns)
    
    # 2. Análisis de políticas RLS
    rls_policies = self._detect_rls_policies()
    if rls_policies:
        evidence.add_rls_evidence(rls_policies)
    
    # 3. Análisis de middleware tenant-aware
    tenant_middleware = self._detect_tenant_middleware()
    if tenant_middleware:
        evidence.add_middleware_evidence(tenant_middleware)
    
    # 4. Calcular confianza
    confidence = evidence.calculate_confidence()
    
    return MultiTenantAnalysis(
        is_multitenant=confidence > 0.7,
        confidence=confidence,
        evidence=evidence,
        isolation_method=self._determine_isolation_method(evidence),
        recommendations=self._generate_multitenant_recommendations(evidence)
    )
```

### Algoritmo de Análisis de Calidad

```python
def _calculate_architecture_quality_score(self, analysis_results: Dict) -> QualityMetrics:
    """
    Calcula métricas de calidad usando modelo ponderado
    """
    weights = {
        'maintainability': 0.25,
        'scalability': 0.20,
        'security': 0.20,
        'performance': 0.15,
        'testability': 0.10,
        'documentation': 0.10
    }
    
    scores = {}
    
    # Mantenibilidad
    scores['maintainability'] = self._calculate_maintainability_score(
        complexity=analysis_results['complexity_metrics'],
        coupling=analysis_results['coupling_metrics'],
        patterns_used=analysis_results['architectural_patterns']
    )
    
    # Escalabilidad
    scores['scalability'] = self._calculate_scalability_score(
        architecture_type=analysis_results['architecture_type'],
        database_design=analysis_results['database_analysis'],
        api_design=analysis_results['api_analysis']
    )
    
    # Seguridad
    scores['security'] = analysis_results['security_analysis']['security_score'] / 10
    
    # Performance
    scores['performance'] = self._estimate_performance_score(
        api_structure=analysis_results['api_analysis'],
        frontend_structure=analysis_results['frontend_analysis'],
        caching_strategy=analysis_results['caching_evidence']
    )
    
    # Testabilidad
    scores['testability'] = self._calculate_testability_score(
        test_coverage=analysis_results['test_coverage'],
        dependency_injection=analysis_results['di_usage'],
        mocking_capability=analysis_results['mock_evidence']
    )
    
    # Documentación
    scores['documentation'] = self._calculate_documentation_score(
        api_docs=analysis_results['api_documentation'],
        code_comments=analysis_results['code_comments'],
        readme_quality=analysis_results['readme_analysis']
    )
    
    # Score final ponderado
    overall_score = sum(scores[metric] * weights[metric] for metric in scores)
    
    return QualityMetrics(
        overall_score=overall_score,
        individual_scores=scores,
        weights=weights,
        recommendations=self._generate_quality_recommendations(scores)
    )
```

## 🚀 Optimizaciones de Performance

### Análisis Paralelo
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

class ParallelAnalysisEngine:
    def __init__(self):
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        self.process_pool = ProcessPoolExecutor(max_workers=2)
    
    async def analyze_project_parallel(self, project_path: str) -> DiscoveryResult:
        # I/O intensive tasks en threads
        io_tasks = [
            self._run_in_thread(self.database_analyzer.analyze_project, project_path),
            self._run_in_thread(self.api_detector.analyze_project, project_path),
            self._run_in_thread(self.frontend_analyzer.analyze_project, project_path)
        ]
        
        # CPU intensive tasks en procesos separados
        cpu_tasks = [
            self._run_in_process(self.pattern_recognizer.analyze_patterns, analysis_data),
            self._run_in_process(self.security_mapper.scan_vulnerabilities, project_path)
        ]
        
        # Ejecutar en paralelo
        io_results = await asyncio.gather(*io_tasks)
        cpu_results = await asyncio.gather(*cpu_tasks)
        
        return self._combine_results(io_results, cpu_results)
```

### Cache Inteligente
```python
class AnalysisCache:
    def __init__(self):
        self.file_hash_cache = {}
        self.analysis_cache = {}
        self.ttl = 3600  # 1 hora
    
    def get_cached_analysis(self, project_path: str, analyzer_type: str) -> Optional[Any]:
        cache_key = self._generate_cache_key(project_path, analyzer_type)
        
        if cache_key in self.analysis_cache:
            cached_data = self.analysis_cache[cache_key]
            
            # Verificar TTL
            if time.time() - cached_data['timestamp'] < self.ttl:
                # Verificar si los archivos han cambiado
                if self._files_unchanged(project_path, cached_data['file_hashes']):
                    return cached_data['result']
        
        return None
    
    def cache_analysis(self, project_path: str, analyzer_type: str, result: Any):
        cache_key = self._generate_cache_key(project_path, analyzer_type)
        file_hashes = self._calculate_file_hashes(project_path)
        
        self.analysis_cache[cache_key] = {
            'result': result,
            'timestamp': time.time(),
            'file_hashes': file_hashes
        }
```

## 🧪 Estrategia de Testing

### Pirámide de Testing
```
                    /\
                   /  \
              E2E /    \ Integration Tests
                 /      \  (15%)
                /________\
               /          \
              / Unit Tests \
             /     (70%)    \
            /________________\
```

### Fixtures Realistas
```python
@pytest.fixture(scope="session")
def realistic_enterprise_project():
    """Genera proyecto empresarial completo para testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project = EnterpriseProjectGenerator(tmpdir)
        
        # Backend con 50+ modelos
        project.generate_backend_structure(
            models_count=50,
            api_endpoints=200,
            authentication="JWT",
            authorization="RBAC",
            database="PostgreSQL"
        )
        
        # Frontend con 100+ componentes
        project.generate_frontend_structure(
            framework="Next.js",
            components_count=100,
            pages_count=30,
            typescript=True,
            ui_library="Radix UI"
        )
        
        # Configuración empresarial
        project.add_enterprise_features(
            docker_setup=True,
            ci_cd_pipeline=True,
            monitoring=True,
            documentation=True
        )
        
        yield tmpdir
```

### Property-Based Testing
```python
from hypothesis import given, strategies as st

class TestPatternRecognition:
    @given(st.integers(min_value=1, max_value=100))
    def test_pattern_confidence_always_between_0_and_1(self, model_count):
        """La confianza de patrones siempre debe estar entre 0 y 1"""
        recognizer = PatternRecognizer()
        
        # Generar datos de análisis aleatorios pero válidos
        analysis_data = {
            "total_models": model_count,
            "has_relationships": model_count > 5,
            "uses_uuid": True
        }
        
        patterns = recognizer._recognize_patterns(analysis_data)
        
        for pattern in patterns:
            assert 0.0 <= pattern.confidence <= 1.0
    
    @given(st.text(min_size=10, max_size=1000))
    def test_code_analysis_never_crashes(self, code_sample):
        """El análisis de código nunca debe crashear, sin importar el input"""
        analyzer = DatabaseAnalyzer()
        
        try:
            # Debería manejar gracefully cualquier código
            result = analyzer._analyze_code_sample(code_sample)
            assert isinstance(result, (dict, type(None)))
        except Exception as e:
            # Solo permitir excepciones esperadas
            assert isinstance(e, (SyntaxError, UnicodeError))
```

## 📊 Métricas y Observabilidad

### Métricas de Performance
```python
class PerformanceMetrics:
    def __init__(self):
        self.metrics = {
            'analysis_duration_seconds': Histogram('analysis_duration', 'Duración del análisis'),
            'files_processed_total': Counter('files_processed', 'Archivos procesados'),
            'errors_encountered_total': Counter('errors_encountered', 'Errores encontrados'),
            'memory_usage_bytes': Gauge('memory_usage', 'Uso de memoria'),
            'cache_hit_ratio': Histogram('cache_hit_ratio', 'Ratio de cache hits')
        }
    
    @contextmanager
    def track_analysis_time(self, analyzer_type: str):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        try:
            yield
        finally:
            duration = time.time() - start_time
            end_memory = psutil.Process().memory_info().rss
            memory_delta = end_memory - start_memory
            
            self.metrics['analysis_duration_seconds'].labels(
                analyzer=analyzer_type
            ).observe(duration)
            
            self.metrics['memory_usage_bytes'].labels(
                analyzer=analyzer_type
            ).set(memory_delta)
```

### Health Checks
```python
class DiscoveryEngineHealthCheck:
    def __init__(self, engine: DiscoveryEngine):
        self.engine = engine
    
    async def health_check(self) -> HealthStatus:
        checks = {
            'i18n_system': self._check_i18n_system(),
            'analyzers': self._check_analyzers(),
            'file_system': self._check_file_system_access(),
            'memory': self._check_memory_usage(),
            'dependencies': self._check_external_dependencies()
        }
        
        all_healthy = all(check.status == 'healthy' for check in checks.values())
        
        return HealthStatus(
            overall_status='healthy' if all_healthy else 'degraded',
            checks=checks,
            timestamp=datetime.utcnow()
        )
    
    def _check_analyzers(self) -> CheckResult:
        """Verifica que todos los analizadores estén funcionando"""
        try:
            # Test rápido con proyecto mínimo
            with tempfile.TemporaryDirectory() as tmpdir:
                test_result = self.engine.discover_architecture(
                    tmpdir, 
                    timeout=5  # 5 segundos máximo
                )
                
            return CheckResult(status='healthy', message='Analizadores funcionando')
        except Exception as e:
            return CheckResult(status='unhealthy', message=f'Error en analizadores: {e}')
```

## 🔐 Consideraciones de Seguridad

### Análisis Seguro de Código
```python
class SecureCodeAnalyzer:
    def __init__(self):
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.sql'}
        self.dangerous_patterns = [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'open\s*\([\'"][/\\]'
        ]
    
    def analyze_file_safely(self, file_path: Path) -> Optional[Dict]:
        # Validaciones de seguridad
        if not self._is_safe_file(file_path):
            logger.warning(f"Archivo rechazado por seguridad: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(self.max_file_size)
                
            # Escanear patrones peligrosos
            if self._contains_dangerous_patterns(content):
                logger.warning(f"Patrones peligrosos detectados en: {file_path}")
                return {"warning": "dangerous_patterns_detected"}
            
            return self._analyze_content(content)
            
        except Exception as e:
            logger.error(f"Error analizando {file_path}: {e}")
            return None
    
    def _is_safe_file(self, file_path: Path) -> bool:
        # Verificar tamaño
        if file_path.stat().st_size > self.max_file_size:
            return False
        
        # Verificar extensión
        if file_path.suffix not in self.allowed_extensions:
            return False
        
        # Verificar que no sea symlink malicioso
        if file_path.is_symlink():
            real_path = file_path.resolve()
            if not str(real_path).startswith(str(file_path.parent.resolve())):
                return False
        
        return True
```

### Sandboxing para Análisis
```python
class SandboxedAnalyzer:
    def __init__(self):
        self.resource_limits = {
            'max_memory': 512 * 1024 * 1024,  # 512MB
            'max_cpu_time': 30,  # 30 segundos
            'max_files_open': 100,
            'max_processes': 1
        }
    
    def analyze_in_sandbox(self, project_path: str) -> DiscoveryResult:
        """Ejecuta análisis en ambiente sandboxed"""
        import resource
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Análisis excedió tiempo límite")
        
        # Configurar límites de recursos
        resource.setrlimit(resource.RLIMIT_AS, (
            self.resource_limits['max_memory'],
            self.resource_limits['max_memory']
        ))
        
        resource.setrlimit(resource.RLIMIT_CPU, (
            self.resource_limits['max_cpu_time'],
            self.resource_limits['max_cpu_time']
        ))
        
        # Configurar timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(self.resource_limits['max_cpu_time'] + 5)
        
        try:
            # Ejecutar análisis con restricciones
            return self._execute_restricted_analysis(project_path)
        finally:
            signal.alarm(0)  # Cancelar timeout
```

---

Esta documentación técnica proporciona una visión completa de la arquitectura interna del Discovery Engine, incluyendo patrones de diseño aplicados, algoritmos clave, optimizaciones de performance y consideraciones de seguridad. El sistema está diseñado para ser extensible, mantenible y enterprise-ready.