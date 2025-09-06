"""
API Pattern Detector - Detector de Patrones de API

Analiza estructuras FastAPI, detecta patrones de API REST, autenticación,
middleware y arquitectura general de la API.

Características:
- Detección de routers y endpoints FastAPI
- Análisis de patrones RESTful
- Identificación de middleware personalizado
- Mapeo de esquemas de autenticación
- Análisis de dependencias y validación
- Detección de documentación OpenAPI
- Identificación de WebSockets
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass, field
import json

from ..i18n_manager import get_i18n

logger = logging.getLogger(__name__)


@dataclass
class EndpointInfo:
    """Información detallada de un endpoint"""
    path: str
    method: str
    function_name: str
    parameters: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    response_model: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    requires_auth: bool = False
    description: Optional[str] = None
    file_path: str = ""


@dataclass
class RouterInfo:
    """Información de un router FastAPI"""
    name: str
    prefix: str
    tags: List[str] = field(default_factory=list)
    endpoints: List[EndpointInfo] = field(default_factory=list)
    middleware: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    file_path: str = ""


@dataclass
class MiddlewareInfo:
    """Información de middleware personalizado"""
    name: str
    type: str  # http, websocket, custom
    file_path: str
    description: Optional[str] = None
    parameters: List[str] = field(default_factory=list)


@dataclass
class APIAnalysisResult:
    """Resultado completo del análisis de API"""
    routers: List[RouterInfo] = field(default_factory=list)
    endpoints: List[EndpointInfo] = field(default_factory=list)
    middleware: List[MiddlewareInfo] = field(default_factory=list)
    
    # Estadísticas
    total_routers: int = 0
    total_endpoints: int = 0
    total_middleware: int = 0
    authenticated_endpoints: int = 0
    crud_endpoints: int = 0
    websocket_endpoints: int = 0
    
    # Patrones detectados
    patterns_detected: List[str] = field(default_factory=list)
    api_version: str = "v1"
    uses_openapi: bool = False
    uses_cors: bool = False
    uses_auth: bool = False
    auth_type: str = ""
    
    # Recomendaciones
    recommendations: List[str] = field(default_factory=list)
    
    # Configuración
    fastapi_config: Dict[str, Any] = field(default_factory=dict)


class APIPatternDetector:
    """Detector de patrones de API FastAPI"""
    
    def __init__(self):
        self.i18n = get_i18n()
        self.analysis_result: Optional[APIAnalysisResult] = None
        
        # Patrones HTTP methods
        self.http_methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']
        
        # Patrones CRUD
        self.crud_patterns = {
            'create': ['post', 'create'],
            'read': ['get', 'read', 'list', 'retrieve'],
            'update': ['put', 'patch', 'update'],
            'delete': ['delete', 'remove']
        }
        
        # Patrones de autenticación
        self.auth_patterns = [
            'get_current_user', 'authenticate', 'verify_token',
            'check_permissions', 'require_auth', 'jwt', 'oauth'
        ]
        
        # Patrones de middleware
        self.middleware_patterns = [
            'middleware', 'cors', 'rate_limit', 'compression',
            'logging', 'security', 'auth'
        ]
    
    def analyze_project(self, project_path: str) -> APIAnalysisResult:
        """
        Analiza toda la estructura de API de un proyecto FastAPI.
        
        Args:
            project_path: Ruta al directorio raíz del proyecto
            
        Returns:
            Resultado completo del análisis de API
        """
        logger.info(self.i18n.t('api.analyzing'))
        
        try:
            # Encontrar archivos de API
            api_files = self._find_api_files(project_path)
            
            # Analizar main.py para configuración FastAPI
            main_file = self._find_main_file(project_path)
            fastapi_config = {}
            if main_file:
                fastapi_config = self._analyze_main_file(main_file)
            
            # Analizar routers
            routers = []
            for api_file in api_files:
                try:
                    router_info = self._analyze_router_file(api_file)
                    if router_info:
                        routers.append(router_info)
                except Exception as e:
                    logger.warning(f"Error analizando router {api_file}: {e}")
                    continue
            
            # Analizar middleware
            middleware_files = self._find_middleware_files(project_path)
            middleware = []
            for middleware_file in middleware_files:
                try:
                    middleware_info = self._analyze_middleware_file(middleware_file)
                    if middleware_info:
                        middleware.extend(middleware_info)
                except Exception as e:
                    logger.warning(f"Error analizando middleware {middleware_file}: {e}")
                    continue
            
            # Crear resultado del análisis
            self.analysis_result = self._create_analysis_result(
                routers, middleware, fastapi_config
            )
            
            # Detectar patrones y generar recomendaciones
            self._detect_api_patterns()
            self._generate_api_recommendations()
            
            logger.info(f"Análisis de API completado: {len(routers)} routers encontrados")
            return self.analysis_result
            
        except Exception as e:
            logger.error(f"Error durante análisis de API: {e}")
            raise
    
    def _find_api_files(self, project_path: str) -> List[Path]:
        """Busca archivos de API y routers"""
        api_files = []
        
        # Patrones de búsqueda
        search_patterns = [
            "**/api/**/*.py",
            "**/routers/**/*.py",
            "**/endpoints/**/*.py"
        ]
        
        project_path = Path(project_path)
        
        for pattern in search_patterns:
            for file_path in project_path.glob(pattern):
                if file_path.name not in ["__init__.py", "__pycache__"]:
                    api_files.append(file_path)
        
        return list(set(api_files))  # Eliminar duplicados
    
    def _find_main_file(self, project_path: str) -> Optional[Path]:
        """Busca el archivo main.py principal de FastAPI"""
        possible_locations = [
            Path(project_path) / "backend" / "app" / "main.py",
            Path(project_path) / "app" / "main.py",
            Path(project_path) / "src" / "main.py",
            Path(project_path) / "main.py"
        ]
        
        for location in possible_locations:
            if location.exists():
                return location
        
        return None
    
    def _find_middleware_files(self, project_path: str) -> List[Path]:
        """Busca archivos de middleware personalizado"""
        middleware_files = []
        
        search_patterns = [
            "**/middleware/**/*.py",
            "**/core/*middleware*.py",
            "**/middlewares/**/*.py"
        ]
        
        project_path = Path(project_path)
        
        for pattern in search_patterns:
            for file_path in project_path.glob(pattern):
                if file_path.name not in ["__init__.py", "__pycache__"]:
                    middleware_files.append(file_path)
        
        return middleware_files
    
    def _analyze_main_file(self, main_file: Path) -> Dict[str, Any]:
        """Analiza el archivo main.py para extraer configuración FastAPI"""
        config = {
            "title": "",
            "description": "",
            "version": "",
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json",
            "cors_enabled": False,
            "middleware": [],
            "routers": []
        }
        
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Buscar creación de la app FastAPI
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    # app = FastAPI(...)
                    if (any(isinstance(target, ast.Name) and target.id == "app" 
                           for target in node.targets) and 
                        isinstance(node.value, ast.Call)):
                        
                        call = node.value
                        if (isinstance(call.func, ast.Name) and 
                            call.func.id == "FastAPI"):
                            config.update(self._extract_fastapi_config(call))
                
                # Buscar middleware
                elif isinstance(node, ast.Expr):
                    if (isinstance(node.value, ast.Call) and
                        isinstance(node.value.func, ast.Attribute)):
                        
                        attr = node.value.func
                        if (isinstance(attr.value, ast.Name) and 
                            attr.value.id == "app" and
                            attr.attr == "add_middleware"):
                            
                            middleware_name = self._extract_middleware_name(node.value)
                            if middleware_name:
                                config["middleware"].append(middleware_name)
                
                # Buscar include_router
                elif isinstance(node, ast.Expr):
                    if (isinstance(node.value, ast.Call) and
                        isinstance(node.value.func, ast.Attribute)):
                        
                        attr = node.value.func
                        if (isinstance(attr.value, ast.Name) and 
                            attr.value.id == "app" and
                            attr.attr == "include_router"):
                            
                            router_info = self._extract_router_inclusion(node.value)
                            if router_info:
                                config["routers"].append(router_info)
            
            # Detectar CORS
            if "CORSMiddleware" in content:
                config["cors_enabled"] = True
            
        except Exception as e:
            logger.error(f"Error analizando main.py: {e}")
        
        return config
    
    def _extract_fastapi_config(self, call_node: ast.Call) -> Dict[str, Any]:
        """Extrae configuración de la instancia FastAPI"""
        config = {}
        
        for keyword in call_node.keywords:
            if keyword.arg == "title" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                config["title"] = self._extract_string_value(keyword.value)
            elif keyword.arg == "description" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                config["description"] = self._extract_string_value(keyword.value)
            elif keyword.arg == "version" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                config["version"] = self._extract_string_value(keyword.value)
            elif keyword.arg == "docs_url" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                config["docs_url"] = self._extract_string_value(keyword.value)
            elif keyword.arg == "redoc_url" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                config["redoc_url"] = self._extract_string_value(keyword.value)
            elif keyword.arg == "openapi_url" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                config["openapi_url"] = self._extract_string_value(keyword.value)
        
        return config
    
    def _extract_string_value(self, node: ast.AST) -> str:
        """Extrae valor string de un nodo AST"""
        if isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return ""
    
    def _extract_middleware_name(self, call_node: ast.Call) -> Optional[str]:
        """Extrae nombre del middleware de una llamada add_middleware"""
        if call_node.args:
            first_arg = call_node.args[0]
            if isinstance(first_arg, ast.Name):
                return first_arg.id
            elif isinstance(first_arg, ast.Attribute):
                return first_arg.attr
        return None
    
    def _extract_router_inclusion(self, call_node: ast.Call) -> Optional[Dict[str, Any]]:
        """Extrae información de include_router"""
        router_info = {}
        
        if call_node.args:
            first_arg = call_node.args[0]
            if isinstance(first_arg, ast.Attribute):
                router_info["name"] = first_arg.attr
        
        for keyword in call_node.keywords:
            if keyword.arg == "prefix" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                router_info["prefix"] = self._extract_string_value(keyword.value)
            elif keyword.arg == "tags" and isinstance(keyword.value, ast.List):
                tags = []
                for item in keyword.value.elts:
                    if isinstance(item, (ast.Str, ast.Constant)):
                        tags.append(self._extract_string_value(item))
                router_info["tags"] = tags
        
        return router_info if router_info else None
    
    def _analyze_router_file(self, router_file: Path) -> Optional[RouterInfo]:
        """Analiza un archivo de router FastAPI"""
        try:
            with open(router_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Crear información del router
            router_info = RouterInfo(
                name=router_file.stem,
                prefix="",
                file_path=str(router_file)
            )
            
            # Buscar creación del router
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if (isinstance(target, ast.Name) and 
                            target.id == "router" and
                            isinstance(node.value, ast.Call)):
                            
                            # Extraer configuración del router
                            call = node.value
                            if (isinstance(call.func, ast.Name) and
                                call.func.id == "APIRouter"):
                                router_config = self._extract_router_config(call)
                                router_info.prefix = router_config.get("prefix", "")
                                router_info.tags = router_config.get("tags", [])
            
            # Buscar endpoints decorados (incluyendo async functions)
            endpoints = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    endpoint_info = self._analyze_endpoint_function(node, content)
                    if endpoint_info:
                        endpoint_info.file_path = str(router_file)
                        endpoints.append(endpoint_info)
            
            router_info.endpoints = endpoints
            
            return router_info
            
        except Exception as e:
            logger.error(f"Error analizando router {router_file}: {e}")
            return None
    
    def _extract_router_config(self, call_node: ast.Call) -> Dict[str, Any]:
        """Extrae configuración de APIRouter"""
        config = {}
        
        for keyword in call_node.keywords:
            if keyword.arg == "prefix" and isinstance(keyword.value, (ast.Str, ast.Constant)):
                config["prefix"] = self._extract_string_value(keyword.value)
            elif keyword.arg == "tags" and isinstance(keyword.value, ast.List):
                tags = []
                for item in keyword.value.elts:
                    if isinstance(item, (ast.Str, ast.Constant)):
                        tags.append(self._extract_string_value(item))
                config["tags"] = tags
        
        return config
    
    def _analyze_endpoint_function(self, func_node: ast.AST, content: str) -> Optional[EndpointInfo]:
        """Analiza una función que puede ser un endpoint"""
        # Buscar decoradores de router
        http_method = None
        path = None
        response_model = None
        
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                # @router.get("/path")
                if (isinstance(decorator.func, ast.Attribute) and
                    isinstance(decorator.func.value, ast.Name) and
                    decorator.func.value.id == "router"):
                    
                    method = decorator.func.attr.upper()
                    if method in self.http_methods:
                        http_method = method
                        
                        # Extraer path
                        if decorator.args and isinstance(decorator.args[0], (ast.Str, ast.Constant)):
                            path = self._extract_string_value(decorator.args[0])
                        
                        # Buscar response_model
                        for keyword in decorator.keywords:
                            if keyword.arg == "response_model":
                                response_model = self._extract_response_model(keyword.value)
        
        if not http_method or not path:
            return None
        
        # Analizar parámetros de la función
        parameters = []
        dependencies = []
        requires_auth = False
        
        for arg in func_node.args.args:
            if arg.arg == "self":
                continue
            
            parameters.append(arg.arg)
            
            # Buscar anotación para detectar dependencias
            if arg.annotation:
                annotation_str = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else str(arg.annotation)
                
                if "Depends" in annotation_str:
                    dependencies.append(annotation_str)
                    
                    # Detectar autenticación
                    if any(auth_pattern in annotation_str for auth_pattern in self.auth_patterns):
                        requires_auth = True
        
        return EndpointInfo(
            path=path,
            method=http_method,
            function_name=func_node.name,
            parameters=parameters,
            dependencies=dependencies,
            response_model=response_model,
            requires_auth=requires_auth,
            description=ast.get_docstring(func_node)
        )
    
    def _extract_response_model(self, node: ast.AST) -> Optional[str]:
        """Extrae el response_model de un endpoint"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        elif isinstance(node, ast.Subscript):
            # List[SomeModel]
            return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
        return None
    
    def _analyze_middleware_file(self, middleware_file: Path) -> List[MiddlewareInfo]:
        """Analiza archivo de middleware personalizado"""
        middleware_list = []
        
        try:
            with open(middleware_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Buscar funciones de middleware
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if self._is_middleware_function(node, content):
                        middleware_info = MiddlewareInfo(
                            name=node.name,
                            type=self._detect_middleware_type(node, content),
                            file_path=str(middleware_file),
                            description=ast.get_docstring(node),
                            parameters=[arg.arg for arg in node.args.args if arg.arg != "self"]
                        )
                        middleware_list.append(middleware_info)
                
                elif isinstance(node, ast.ClassDef):
                    if self._is_middleware_class(node, content):
                        middleware_info = MiddlewareInfo(
                            name=node.name,
                            type="class",
                            file_path=str(middleware_file),
                            description=ast.get_docstring(node)
                        )
                        middleware_list.append(middleware_info)
        
        except Exception as e:
            logger.error(f"Error analizando middleware {middleware_file}: {e}")
        
        return middleware_list
    
    def _is_middleware_function(self, func_node: ast.FunctionDef, content: str) -> bool:
        """Determina si una función es middleware"""
        # Buscar patrones de middleware
        func_name_lower = func_node.name.lower()
        
        if any(pattern in func_name_lower for pattern in self.middleware_patterns):
            return True
        
        # Buscar parámetros típicos de middleware (request, call_next)
        arg_names = [arg.arg for arg in func_node.args.args]
        if "request" in arg_names and "call_next" in arg_names:
            return True
        
        return False
    
    def _is_middleware_class(self, class_node: ast.ClassDef, content: str) -> bool:
        """Determina si una clase es middleware"""
        class_name_lower = class_node.name.lower()
        return "middleware" in class_name_lower
    
    def _detect_middleware_type(self, func_node: ast.FunctionDef, content: str) -> str:
        """Detecta el tipo de middleware"""
        func_name_lower = func_node.name.lower()
        
        if "http" in func_name_lower:
            return "http"
        elif "websocket" in func_name_lower:
            return "websocket"
        elif "cors" in func_name_lower:
            return "cors"
        elif "auth" in func_name_lower:
            return "auth"
        elif "rate" in func_name_lower or "limit" in func_name_lower:
            return "rate_limiting"
        elif "log" in func_name_lower:
            return "logging"
        else:
            return "custom"
    
    def _create_analysis_result(self, routers: List[RouterInfo], 
                             middleware: List[MiddlewareInfo],
                             fastapi_config: Dict[str, Any]) -> APIAnalysisResult:
        """Crea el resultado del análisis con estadísticas"""
        result = APIAnalysisResult()
        
        result.routers = routers
        result.middleware = middleware
        result.fastapi_config = fastapi_config
        
        # Recopilar todos los endpoints
        all_endpoints = []
        for router in routers:
            all_endpoints.extend(router.endpoints)
        
        result.endpoints = all_endpoints
        
        # Calcular estadísticas
        result.total_routers = len(routers)
        result.total_endpoints = len(all_endpoints)
        result.total_middleware = len(middleware)
        result.authenticated_endpoints = sum(1 for ep in all_endpoints if ep.requires_auth)
        result.websocket_endpoints = sum(1 for ep in all_endpoints if "ws" in ep.path.lower())
        
        # Contar endpoints CRUD
        crud_count = 0
        for endpoint in all_endpoints:
            func_name_lower = endpoint.function_name.lower()
            if any(any(pattern in func_name_lower for pattern in patterns) 
                  for patterns in self.crud_patterns.values()):
                crud_count += 1
        result.crud_endpoints = crud_count
        
        # Detectar configuraciones
        result.uses_openapi = bool(fastapi_config.get("openapi_url"))
        result.uses_cors = fastapi_config.get("cors_enabled", False)
        result.uses_auth = result.authenticated_endpoints > 0
        
        # Detectar tipo de auth
        if result.uses_auth:
            # Buscar patrones de autenticación en dependencias
            auth_deps = []
            for endpoint in all_endpoints:
                for dep in endpoint.dependencies:
                    if any(auth_pattern in dep.lower() for auth_pattern in self.auth_patterns):
                        auth_deps.append(dep)
            
            if any("jwt" in dep.lower() for dep in auth_deps):
                result.auth_type = "JWT"
            elif any("oauth" in dep.lower() for dep in auth_deps):
                result.auth_type = "OAuth"
            else:
                result.auth_type = "Custom"
        
        # Detectar versión API
        if any("/v1/" in router.prefix for router in routers):
            result.api_version = "v1"
        elif any("/v2/" in router.prefix for router in routers):
            result.api_version = "v2"
        
        return result
    
    def _detect_api_patterns(self):
        """Detecta patrones arquitectónicos en la API"""
        if not self.analysis_result:
            return
        
        patterns = []
        
        # FastAPI con OpenAPI
        if self.analysis_result.uses_openapi:
            patterns.append(self.i18n.t('patterns.detected', pattern='FastAPI con OpenAPI'))
        
        # Patrón RESTful
        rest_methods = set()
        for endpoint in self.analysis_result.endpoints:
            rest_methods.add(endpoint.method)
        
        if len(rest_methods) >= 4:  # GET, POST, PUT, DELETE
            patterns.append(self.i18n.t('patterns.detected', pattern='RESTful API'))
        
        # Patrón Repository (si hay muchos endpoints CRUD)
        if self.analysis_result.crud_endpoints > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='CRUD Operations'))
        
        # Autenticación JWT
        if self.analysis_result.auth_type == "JWT":
            patterns.append(self.i18n.t('patterns.detected', pattern='JWT Authentication'))
        
        # CORS configurado
        if self.analysis_result.uses_cors:
            patterns.append(self.i18n.t('patterns.detected', pattern='CORS Configuration'))
        
        # Middleware personalizado
        if self.analysis_result.total_middleware > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='Custom Middleware'))
        
        # WebSocket support
        if self.analysis_result.websocket_endpoints > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='WebSocket Support'))
        
        self.analysis_result.patterns_detected = patterns
    
    def _generate_api_recommendations(self):
        """Genera recomendaciones basadas en el análisis de API"""
        if not self.analysis_result:
            return
        
        recommendations = []
        
        # Recomendaciones de documentación
        if not self.analysis_result.uses_openapi:
            recommendations.append(self.i18n.t('recommendations.documentation'))
        
        # Recomendaciones de autenticación
        if not self.analysis_result.uses_auth:
            recommendations.append("Considerar implementar autenticación para endpoints sensibles")
        
        # Recomendaciones de versionado
        if not self.analysis_result.api_version:
            recommendations.append("Implementar versionado de API (/api/v1/)")
        
        # Recomendaciones de estructura
        recommendations.append(self.i18n.t('recommendations.router_structure'))
        
        # Recomendaciones de testing
        recommendations.append(self.i18n.t('recommendations.testing'))
        
        # CORS si no está habilitado
        if not self.analysis_result.uses_cors:
            recommendations.append("Configurar CORS apropiadamente para frontend")
        
        self.analysis_result.recommendations = recommendations
    
    def generate_report(self) -> str:
        """Genera un reporte en español del análisis de API"""
        if not self.analysis_result:
            return "No hay análisis de API disponible"
        
        report = []
        report.append(self.i18n.t('api.title'))
        
        # Configuración FastAPI
        config = self.analysis_result.fastapi_config
        if config.get("title"):
            report.append(f"- {self.i18n.t('api.fastapi')}")
        
        if self.analysis_result.uses_auth:
            auth_msg = self.i18n.t('api.auth') + f" ({self.analysis_result.auth_type})"
            report.append(f"- {auth_msg}")
        
        # Endpoints RESTful
        if self.analysis_result.api_version:
            pattern = f"/api/{self.analysis_result.api_version}/{{resource}}"
            report.append(f"- {self.i18n.t('api.endpoints').format(pattern=pattern)}")
        
        # Estadísticas
        report.append(f"- {self.i18n.t('api.routes', count=self.analysis_result.total_endpoints)}")
        
        # Middleware
        if self.analysis_result.total_middleware > 0:
            middleware_types = list(set(mw.type for mw in self.analysis_result.middleware))
            types_str = ", ".join(middleware_types)
            report.append(f"- {self.i18n.t('api.middleware', types=types_str)}")
        
        # Patrones detectados
        if self.analysis_result.patterns_detected:
            report.append("")
            for pattern in self.analysis_result.patterns_detected:
                report.append(f"- {pattern}")
        
        return "\n".join(report)
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Retorna resumen del análisis para integración"""
        if not self.analysis_result:
            return {}
        
        return {
            "total_routers": self.analysis_result.total_routers,
            "total_endpoints": self.analysis_result.total_endpoints,
            "total_middleware": self.analysis_result.total_middleware,
            "authenticated_endpoints": self.analysis_result.authenticated_endpoints,
            "crud_endpoints": self.analysis_result.crud_endpoints,
            "websocket_endpoints": self.analysis_result.websocket_endpoints,
            "api_version": self.analysis_result.api_version,
            "uses_openapi": self.analysis_result.uses_openapi,
            "uses_cors": self.analysis_result.uses_cors,
            "uses_auth": self.analysis_result.uses_auth,
            "auth_type": self.analysis_result.auth_type,
            "patterns": self.analysis_result.patterns_detected,
            "recommendations": self.analysis_result.recommendations,
            "routers": [
                {
                    "name": router.name,
                    "prefix": router.prefix,
                    "tags": router.tags,
                    "endpoints_count": len(router.endpoints)
                }
                for router in self.analysis_result.routers
            ]
        }


if __name__ == "__main__":
    # Ejemplo de uso
    detector = APIPatternDetector()
    project_path = "/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla"
    
    try:
        result = detector.analyze_project(project_path)
        print(detector.generate_report())
        print("\n=== Resumen Técnico ===")
        summary = detector.get_analysis_summary()
        for key, value in summary.items():
            if key != "routers":
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")