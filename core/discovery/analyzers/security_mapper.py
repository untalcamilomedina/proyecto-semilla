"""
Security Mapper - Mapeador de Seguridad

Mapea y analiza el modelo de seguridad completo de la aplicación, incluyendo
autenticación, autorización, Row-Level Security (RLS), y políticas de seguridad.

Características:
- Análisis de esquemas de autenticación (JWT, OAuth, API Keys)
- Mapeo de sistema de roles y permisos (RBAC)
- Detección de Row-Level Security (RLS) y políticas
- Análisis de middleware de seguridad
- Identificación de vulnerabilidades comunes
- Mapeo de flujos de autenticación y autorización
- Análisis de configuración de CORS y CSP
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
class AuthenticationMethod:
    """Información de método de autenticación"""
    type: str  # jwt, oauth, api_key, session, basic
    implementation: str
    file_path: str
    features: List[str] = field(default_factory=list)  # refresh_tokens, multi_factor, etc.
    security_level: str = "medium"  # low, medium, high
    description: Optional[str] = None


@dataclass
class RoleInfo:
    """Información de roles del sistema"""
    name: str
    permissions: List[str] = field(default_factory=list)
    description: Optional[str] = None
    hierarchy_level: int = 0
    is_admin: bool = False
    is_system: bool = False


@dataclass
class PermissionInfo:
    """Información de permisos del sistema"""
    name: str
    resource: str
    action: str  # create, read, update, delete, execute
    scope: str = "global"  # global, tenant, user
    description: Optional[str] = None


@dataclass
class RLSPolicy:
    """Información de política Row-Level Security"""
    table_name: str
    policy_name: str
    policy_type: str  # permissive, restrictive
    command: str  # SELECT, INSERT, UPDATE, DELETE, ALL
    roles: List[str] = field(default_factory=list)
    expression: str = ""
    file_path: str = ""


@dataclass
class SecurityMiddleware:
    """Información de middleware de seguridad"""
    name: str
    type: str  # cors, csrf, rate_limiting, authentication, authorization
    file_path: str
    configuration: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    description: Optional[str] = None


@dataclass
class SecurityVulnerability:
    """Vulnerabilidad de seguridad detectada"""
    type: str
    severity: str  # low, medium, high, critical
    description: str
    file_path: str
    line_number: Optional[int] = None
    recommendation: str = ""


@dataclass
class SecurityAnalysisResult:
    """Resultado completo del análisis de seguridad"""
    authentication_methods: List[AuthenticationMethod] = field(default_factory=list)
    roles: List[RoleInfo] = field(default_factory=list)
    permissions: List[PermissionInfo] = field(default_factory=list)
    rls_policies: List[RLSPolicy] = field(default_factory=list)
    middleware: List[SecurityMiddleware] = field(default_factory=list)
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    
    # Estadísticas
    total_roles: int = 0
    total_permissions: int = 0
    total_rls_policies: int = 0
    total_middleware: int = 0
    total_vulnerabilities: int = 0
    
    # Características de seguridad
    uses_jwt: bool = False
    uses_refresh_tokens: bool = False
    uses_rbac: bool = False
    uses_rls: bool = False
    uses_cors: bool = False
    uses_rate_limiting: bool = False
    uses_encryption: bool = False
    multi_tenant_security: bool = False
    
    # Configuración de seguridad
    password_policy: Dict[str, Any] = field(default_factory=dict)
    session_config: Dict[str, Any] = field(default_factory=dict)
    cors_config: Dict[str, Any] = field(default_factory=dict)
    
    # Patrones y recomendaciones
    patterns_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    security_score: int = 0  # 0-100


class SecurityMapper:
    """Mapeador de arquitectura de seguridad"""
    
    def __init__(self):
        self.i18n = get_i18n()
        self.analysis_result: Optional[SecurityAnalysisResult] = None
        
        # Patrones de autenticación
        self.auth_patterns = {
            'jwt': ['jwt', 'jsonwebtoken', 'jose', 'pyjwt'],
            'oauth': ['oauth', 'oauth2', 'openid'],
            'api_key': ['api_key', 'apikey', 'x-api-key'],
            'session': ['session', 'cookie', 'flask-login'],
            'basic': ['basic_auth', 'httpbasic']
        }
        
        # Patrones de middleware de seguridad
        self.security_middleware_patterns = {
            'cors': ['cors', 'cross-origin'],
            'csrf': ['csrf', 'cross-site'],
            'rate_limiting': ['rate_limit', 'rate-limit', 'throttle'],
            'helmet': ['helmet', 'security-headers'],
            'auth': ['auth', 'authenticate', 'authorization'],
            'encryption': ['encrypt', 'decrypt', 'crypto'],
            'validation': ['validate', 'sanitize', 'input_validation']
        }
        
        # Vulnerabilidades comunes
        self.vulnerability_patterns = {
            'sql_injection': {
                'patterns': [r'SELECT.*\+.*', r'execute\s*\([\'"].+[\'"]\s*\+', r'format.*SELECT'],
                'severity': 'high',
                'description': 'Posible vulnerabilidad de SQL Injection'
            },
            'hardcoded_secrets': {
                'patterns': [r'password\s*=\s*[\'"][^\'"]{8,}[\'"]', r'secret\s*=\s*[\'"][^\'"]+[\'"]'],
                'severity': 'high',
                'description': 'Secreto hardcodeado detectado'
            },
            'weak_crypto': {
                'patterns': [r'md5\(', r'sha1\(', r'des', r'rc4'],
                'severity': 'medium',
                'description': 'Algoritmo criptográfico débil'
            },
            'missing_auth': {
                'patterns': [r'@app\.route.*methods.*POST.*(?!.*auth)', r'def\s+\w+.*(?!.*auth).*:'],
                'severity': 'medium',
                'description': 'Endpoint sin autenticación'
            }
        }
        
        # Patrones RLS
        self.rls_patterns = [
            r'CREATE POLICY\s+(\w+)\s+ON\s+(\w+)',
            r'ALTER TABLE\s+(\w+)\s+ENABLE ROW LEVEL SECURITY',
            r'set_config\s*\(\s*[\'"]app\.current_tenant_id[\'"]',
            r'current_setting\s*\(\s*[\'"]app\.'
        ]
    
    def analyze_project(self, project_path: str) -> SecurityAnalysisResult:
        """
        Analiza el modelo completo de seguridad de un proyecto.
        
        Args:
            project_path: Ruta al directorio raíz del proyecto
            
        Returns:
            Resultado completo del análisis de seguridad
        """
        logger.info(self.i18n.t('security.analyzing'))
        
        try:
            # Analizar archivos de seguridad
            security_files = self._find_security_files(project_path)
            
            # Analizar métodos de autenticación
            auth_methods = []
            for file_path in security_files:
                try:
                    methods = self._analyze_authentication_file(file_path)
                    auth_methods.extend(methods)
                except Exception as e:
                    logger.warning(f"Error analizando autenticación en {file_path}: {e}")
            
            # Analizar modelos de roles
            roles = self._analyze_role_models(project_path)
            
            # Analizar permisos
            permissions = self._analyze_permissions(project_path)
            
            # Analizar políticas RLS
            rls_policies = self._analyze_rls_policies(project_path)
            
            # Analizar middleware de seguridad
            middleware = self._analyze_security_middleware(project_path)
            
            # Detectar vulnerabilidades
            vulnerabilities = self._detect_vulnerabilities(project_path)
            
            # Crear resultado del análisis
            self.analysis_result = self._create_security_analysis_result(
                auth_methods, roles, permissions, rls_policies, 
                middleware, vulnerabilities
            )
            
            # Detectar patrones y generar recomendaciones
            self._detect_security_patterns()
            self._generate_security_recommendations()
            self._calculate_security_score()
            
            logger.info(f"Análisis de seguridad completado. Score: {self.analysis_result.security_score}/100")
            return self.analysis_result
            
        except Exception as e:
            logger.error(f"Error durante análisis de seguridad: {e}")
            raise
    
    def _find_security_files(self, project_path: str) -> List[Path]:
        """Busca archivos relacionados con seguridad"""
        security_files = []
        
        search_patterns = [
            "**/core/security*.py",
            "**/security/**/*.py",
            "**/auth/**/*.py",
            "**/middleware/**/*.py",
            "**/models/user*.py",
            "**/models/role*.py",
            "**/models/*auth*.py",
            "**/*security*.py",
            "**/*auth*.py",
            "**/config*.py"
        ]
        
        project_path = Path(project_path)
        
        for pattern in search_patterns:
            for file_path in project_path.glob(pattern):
                if (file_path.is_file() and 
                    file_path.suffix == ".py" and
                    "test" not in file_path.name.lower()):
                    security_files.append(file_path)
        
        return list(set(security_files))  # Eliminar duplicados
    
    def _analyze_authentication_file(self, file_path: Path) -> List[AuthenticationMethod]:
        """Analiza un archivo en busca de métodos de autenticación"""
        auth_methods = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detectar diferentes tipos de autenticación
            for auth_type, patterns in self.auth_patterns.items():
                if any(pattern in content.lower() for pattern in patterns):
                    features = self._extract_auth_features(content, auth_type)
                    
                    auth_method = AuthenticationMethod(
                        type=auth_type,
                        implementation=self._detect_auth_implementation(content, auth_type),
                        file_path=str(file_path),
                        features=features,
                        security_level=self._assess_auth_security_level(content, auth_type)
                    )
                    
                    auth_methods.append(auth_method)
        
        except Exception as e:
            logger.error(f"Error analizando autenticación en {file_path}: {e}")
        
        return auth_methods
    
    def _extract_auth_features(self, content: str, auth_type: str) -> List[str]:
        """Extrae características del método de autenticación"""
        features = []
        
        # Características JWT
        if auth_type == 'jwt':
            if 'refresh' in content.lower():
                features.append('refresh_tokens')
            if 'access_token' in content.lower():
                features.append('access_tokens')
            if 'tenant_id' in content:
                features.append('multi_tenant')
        
        # Características generales
        if 'expire' in content.lower():
            features.append('token_expiration')
        if 'revoke' in content.lower():
            features.append('token_revocation')
        if 'bcrypt' in content.lower() or 'scrypt' in content.lower():
            features.append('secure_hashing')
        if 'mfa' in content.lower() or 'two_factor' in content.lower():
            features.append('multi_factor_auth')
        
        return features
    
    def _detect_auth_implementation(self, content: str, auth_type: str) -> str:
        """Detecta la implementación específica del método de autenticación"""
        if auth_type == 'jwt':
            if 'jose' in content:
                return 'python-jose'
            elif 'pyjwt' in content:
                return 'PyJWT'
            elif 'authlib' in content:
                return 'Authlib'
        elif auth_type == 'oauth':
            if 'authlib' in content:
                return 'Authlib'
            elif 'oauthlib' in content:
                return 'OAuthLib'
        
        return 'custom'
    
    def _assess_auth_security_level(self, content: str, auth_type: str) -> str:
        """Evalúa el nivel de seguridad del método de autenticación"""
        score = 0
        
        # Puntos positivos
        if 'bcrypt' in content.lower() or 'scrypt' in content.lower():
            score += 2
        if 'expire' in content.lower():
            score += 1
        if 'refresh' in content.lower():
            score += 1
        if 'revoke' in content.lower():
            score += 1
        if auth_type == 'jwt':
            score += 1
        
        # Puntos negativos
        if 'md5' in content.lower() or 'sha1' in content.lower():
            score -= 2
        if 'password' in content and '123' in content:
            score -= 3
        
        if score >= 4:
            return 'high'
        elif score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _analyze_role_models(self, project_path: str) -> List[RoleInfo]:
        """Analiza modelos de roles del sistema"""
        roles = []
        
        # Buscar archivos de modelos de roles
        role_files = list(Path(project_path).glob("**/models/*role*.py"))
        
        for file_path in role_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar definiciones de roles
                roles.extend(self._extract_roles_from_content(content, file_path))
                
            except Exception as e:
                logger.warning(f"Error analizando roles en {file_path}: {e}")
        
        return roles
    
    def _extract_roles_from_content(self, content: str, file_path: Path) -> List[RoleInfo]:
        """Extrae información de roles desde el contenido de un archivo"""
        roles = []
        
        # Buscar clases Role
        tree = None
        try:
            tree = ast.parse(content)
        except:
            pass
        
        if tree:
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and 'role' in node.name.lower():
                    role_info = RoleInfo(
                        name=node.name,
                        description=ast.get_docstring(node)
                    )
                    
                    # Buscar campos/atributos
                    for item in node.body:
                        if isinstance(item, ast.Assign):
                            for target in item.targets:
                                if isinstance(target, ast.Name):
                                    if 'permission' in target.id.lower():
                                        # Extraer permisos si están definidos
                                        pass
                    
                    roles.append(role_info)
        
        # Buscar patrones de texto para roles predefinidos
        role_patterns = [
            r'ADMIN|admin|Admin',
            r'USER|user|User', 
            r'MODERATOR|moderator|Moderator',
            r'GUEST|guest|Guest'
        ]
        
        for pattern in role_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                role_name = match.lower()
                if not any(r.name.lower() == role_name for r in roles):
                    roles.append(RoleInfo(
                        name=role_name.capitalize(),
                        is_admin=(role_name == 'admin'),
                        is_system=(role_name in ['admin', 'system'])
                    ))
        
        return roles
    
    def _analyze_permissions(self, project_path: str) -> List[PermissionInfo]:
        """Analiza permisos del sistema"""
        permissions = []
        
        # Buscar archivos que contengan definiciones de permisos
        permission_patterns = [
            "**/models/*permission*.py",
            "**/core/permissions.py",
            "**/auth/*permission*.py"
        ]
        
        project_path = Path(project_path)
        
        for pattern in permission_patterns:
            for file_path in project_path.glob(pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    permissions.extend(self._extract_permissions_from_content(content))
                    
                except Exception as e:
                    logger.warning(f"Error analizando permisos en {file_path}: {e}")
        
        return permissions
    
    def _extract_permissions_from_content(self, content: str) -> List[PermissionInfo]:
        """Extrae permisos desde el contenido de un archivo"""
        permissions = []
        
        # Patrones CRUD comunes
        crud_patterns = [
            r'create_(\w+)', r'read_(\w+)', r'update_(\w+)', r'delete_(\w+)',
            r'(\w+)_create', r'(\w+)_read', r'(\w+)_update', r'(\w+)_delete'
        ]
        
        for pattern in crud_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                resource = match if isinstance(match, str) else match[0]
                action = 'create' if 'create' in pattern else \
                        'read' if 'read' in pattern else \
                        'update' if 'update' in pattern else 'delete'
                
                permission = PermissionInfo(
                    name=f"{action}_{resource}",
                    resource=resource,
                    action=action,
                    scope="tenant" if "tenant" in content.lower() else "global"
                )
                permissions.append(permission)
        
        return permissions
    
    def _analyze_rls_policies(self, project_path: str) -> List[RLSPolicy]:
        """Analiza políticas Row-Level Security"""
        policies = []
        
        # Buscar archivos SQL y Python que contengan RLS
        search_patterns = [
            "**/*.sql",
            "**/alembic/versions/*.py",
            "**/migrations/*.py",
            "**/models/*.py"
        ]
        
        project_path = Path(project_path)
        
        for pattern in search_patterns:
            for file_path in project_path.glob(pattern):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    policies.extend(self._extract_rls_policies_from_content(content, file_path))
                    
                except Exception as e:
                    logger.warning(f"Error analizando RLS en {file_path}: {e}")
        
        return policies
    
    def _extract_rls_policies_from_content(self, content: str, file_path: Path) -> List[RLSPolicy]:
        """Extrae políticas RLS desde el contenido de un archivo"""
        policies = []
        
        # Buscar CREATE POLICY
        policy_matches = re.findall(
            r'CREATE POLICY\s+(\w+)\s+ON\s+(\w+)(?:\s+FOR\s+(\w+))?(?:\s+TO\s+([\w,\s]+))?(?:\s+USING\s*\(([^)]+)\))?',
            content, re.IGNORECASE | re.MULTILINE
        )
        
        for match in policy_matches:
            policy_name, table_name, command, roles, expression = match
            
            policy = RLSPolicy(
                table_name=table_name,
                policy_name=policy_name,
                policy_type="permissive",  # Por defecto
                command=command or "ALL",
                roles=roles.split(',') if roles else [],
                expression=expression or "",
                file_path=str(file_path)
            )
            policies.append(policy)
        
        # Buscar habilitación de RLS
        rls_enable_matches = re.findall(
            r'ALTER TABLE\s+(\w+)\s+ENABLE ROW LEVEL SECURITY',
            content, re.IGNORECASE
        )
        
        for table_name in rls_enable_matches:
            # Solo agregar si no existe ya una política para esta tabla
            if not any(p.table_name == table_name for p in policies):
                policy = RLSPolicy(
                    table_name=table_name,
                    policy_name="enable_rls",
                    policy_type="enable",
                    command="ALL",
                    file_path=str(file_path)
                )
                policies.append(policy)
        
        # Buscar uso de configuración de contexto (PostgreSQL)
        context_matches = re.findall(
            r'set_config\s*\(\s*[\'"]app\.(\w+)[\'"]',
            content
        )
        
        if context_matches:
            for context_var in context_matches:
                policy = RLSPolicy(
                    table_name="context",
                    policy_name=f"set_{context_var}",
                    policy_type="context",
                    command="SET",
                    expression=context_var,
                    file_path=str(file_path)
                )
                policies.append(policy)
        
        return policies
    
    def _analyze_security_middleware(self, project_path: str) -> List[SecurityMiddleware]:
        """Analiza middleware de seguridad"""
        middleware = []
        
        # Buscar archivos de middleware
        middleware_files = list(Path(project_path).glob("**/middleware/**/*.py"))
        middleware_files.extend(Path(project_path).glob("**/core/*middleware*.py"))
        middleware_files.extend(Path(project_path).glob("**/main.py"))
        
        for file_path in middleware_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                middleware.extend(self._extract_middleware_from_content(content, file_path))
                
            except Exception as e:
                logger.warning(f"Error analizando middleware en {file_path}: {e}")
        
        return middleware
    
    def _extract_middleware_from_content(self, content: str, file_path: Path) -> List[SecurityMiddleware]:
        """Extrae middleware de seguridad desde el contenido"""
        middleware = []
        
        # Detectar CORS
        if 'CORSMiddleware' in content or 'cors' in content.lower():
            config = {}
            if 'allow_origins' in content:
                config['has_origins'] = True
            if 'allow_credentials' in content:
                config['allows_credentials'] = True
            
            middleware.append(SecurityMiddleware(
                name="CORS",
                type="cors",
                file_path=str(file_path),
                configuration=config
            ))
        
        # Detectar Rate Limiting
        if any(pattern in content.lower() for pattern in ['rate_limit', 'throttle', 'slowapi']):
            middleware.append(SecurityMiddleware(
                name="Rate Limiting",
                type="rate_limiting", 
                file_path=str(file_path)
            ))
        
        # Detectar middleware de autenticación
        if any(pattern in content.lower() for pattern in ['auth', 'jwt', 'bearer']):
            middleware.append(SecurityMiddleware(
                name="Authentication",
                type="authentication",
                file_path=str(file_path)
            ))
        
        # Detectar middleware de compresión (puede tener implicaciones de seguridad)
        if 'compression' in content.lower() or 'gzip' in content.lower():
            middleware.append(SecurityMiddleware(
                name="Compression",
                type="compression",
                file_path=str(file_path)
            ))
        
        # Detectar middleware de logging de seguridad
        if 'audit' in content.lower() or 'security_log' in content.lower():
            middleware.append(SecurityMiddleware(
                name="Security Logging",
                type="logging",
                file_path=str(file_path)
            ))
        
        return middleware
    
    def _detect_vulnerabilities(self, project_path: str) -> List[SecurityVulnerability]:
        """Detecta vulnerabilidades comunes de seguridad"""
        vulnerabilities = []
        
        # Buscar en archivos Python
        python_files = list(Path(project_path).rglob("*.py"))
        
        for file_path in python_files:
            if any(excluded in str(file_path) for excluded in ['test', 'venv', 'node_modules', '.git']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for vuln_type, vuln_info in self.vulnerability_patterns.items():
                        for pattern in vuln_info['patterns']:
                            if re.search(pattern, line, re.IGNORECASE):
                                vulnerability = SecurityVulnerability(
                                    type=vuln_type,
                                    severity=vuln_info['severity'],
                                    description=vuln_info['description'],
                                    file_path=str(file_path),
                                    line_number=line_num,
                                    recommendation=self._get_vulnerability_recommendation(vuln_type)
                                )
                                vulnerabilities.append(vulnerability)
                
            except Exception as e:
                logger.warning(f"Error escaneando vulnerabilidades en {file_path}: {e}")
        
        return vulnerabilities
    
    def _get_vulnerability_recommendation(self, vuln_type: str) -> str:
        """Obtiene recomendación para un tipo de vulnerabilidad"""
        recommendations = {
            'sql_injection': 'Usar consultas parametrizadas o ORM para evitar SQL injection',
            'hardcoded_secrets': 'Mover secretos a variables de entorno o sistemas de gestión de secretos',
            'weak_crypto': 'Usar algoritmos criptográficos seguros como SHA-256, bcrypt o scrypt',
            'missing_auth': 'Agregar autenticación requerida a endpoints sensibles'
        }
        
        return recommendations.get(vuln_type, 'Revisar y corregir la vulnerabilidad detectada')
    
    def _create_security_analysis_result(self, auth_methods: List[AuthenticationMethod],
                                       roles: List[RoleInfo], permissions: List[PermissionInfo],
                                       rls_policies: List[RLSPolicy], middleware: List[SecurityMiddleware],
                                       vulnerabilities: List[SecurityVulnerability]) -> SecurityAnalysisResult:
        """Crea el resultado del análisis con estadísticas"""
        result = SecurityAnalysisResult()
        
        result.authentication_methods = auth_methods
        result.roles = roles  
        result.permissions = permissions
        result.rls_policies = rls_policies
        result.middleware = middleware
        result.vulnerabilities = vulnerabilities
        
        # Estadísticas
        result.total_roles = len(roles)
        result.total_permissions = len(permissions)
        result.total_rls_policies = len(rls_policies)
        result.total_middleware = len(middleware)
        result.total_vulnerabilities = len(vulnerabilities)
        
        # Características de seguridad
        result.uses_jwt = any(auth.type == 'jwt' for auth in auth_methods)
        result.uses_refresh_tokens = any('refresh_tokens' in auth.features for auth in auth_methods)
        result.uses_rbac = len(roles) > 0 and len(permissions) > 0
        result.uses_rls = len(rls_policies) > 0
        result.uses_cors = any(mw.type == 'cors' for mw in middleware)
        result.uses_rate_limiting = any(mw.type == 'rate_limiting' for mw in middleware)
        result.multi_tenant_security = any('multi_tenant' in auth.features for auth in auth_methods)
        result.uses_encryption = any('secure_hashing' in auth.features for auth in auth_methods)
        
        return result
    
    def _detect_security_patterns(self):
        """Detecta patrones de seguridad en la aplicación"""
        if not self.analysis_result:
            return
        
        patterns = []
        
        # JWT Authentication
        if self.analysis_result.uses_jwt:
            patterns.append(self.i18n.t('patterns.detected', pattern='JWT Authentication'))
        
        # Refresh Tokens
        if self.analysis_result.uses_refresh_tokens:
            patterns.append(self.i18n.t('patterns.detected', pattern='Refresh Token Mechanism'))
        
        # RBAC
        if self.analysis_result.uses_rbac:
            patterns.append(self.i18n.t('patterns.detected', pattern='Role-Based Access Control (RBAC)'))
        
        # Row-Level Security
        if self.analysis_result.uses_rls:
            patterns.append(self.i18n.t('patterns.detected', pattern='Row-Level Security (RLS)'))
        
        # Multi-tenant Security
        if self.analysis_result.multi_tenant_security:
            patterns.append(self.i18n.t('patterns.detected', pattern='Multi-Tenant Security Model'))
        
        # CORS
        if self.analysis_result.uses_cors:
            patterns.append(self.i18n.t('patterns.detected', pattern='CORS Configuration'))
        
        # Rate Limiting
        if self.analysis_result.uses_rate_limiting:
            patterns.append(self.i18n.t('patterns.detected', pattern='Rate Limiting'))
        
        self.analysis_result.patterns_detected = patterns
    
    def _generate_security_recommendations(self):
        """Genera recomendaciones de seguridad"""
        if not self.analysis_result:
            return
        
        recommendations = []
        
        # Autenticación
        if not self.analysis_result.uses_jwt:
            recommendations.append("Implementar autenticación JWT para mayor seguridad")
        
        if not self.analysis_result.uses_refresh_tokens:
            recommendations.append("Añadir mecanismo de refresh tokens para sesiones seguras")
        
        # Autorización  
        if not self.analysis_result.uses_rbac:
            recommendations.append("Implementar sistema de roles y permisos (RBAC)")
        
        # Multi-tenancy
        if not self.analysis_result.uses_rls and self.analysis_result.multi_tenant_security:
            recommendations.append(self.i18n.t('recommendations.rls_policies'))
        
        # Middleware de seguridad
        if not self.analysis_result.uses_cors:
            recommendations.append("Configurar CORS apropiadamente para el frontend")
        
        if not self.analysis_result.uses_rate_limiting:
            recommendations.append("Implementar rate limiting para prevenir abuse")
        
        # Vulnerabilidades
        if self.analysis_result.total_vulnerabilities > 0:
            high_vulns = sum(1 for v in self.analysis_result.vulnerabilities if v.severity == 'high')
            if high_vulns > 0:
                recommendations.append(f"Corregir {high_vulns} vulnerabilidades de alta severidad")
        
        # Encriptación
        if not self.analysis_result.uses_encryption:
            recommendations.append("Implementar hashing seguro de contraseñas (bcrypt/scrypt)")
        
        self.analysis_result.recommendations = recommendations
    
    def _calculate_security_score(self):
        """Calcula puntuación de seguridad (0-100)"""
        if not self.analysis_result:
            return
        
        score = 0
        
        # Puntos por características de seguridad implementadas
        if self.analysis_result.uses_jwt:
            score += 15
        if self.analysis_result.uses_refresh_tokens:
            score += 10
        if self.analysis_result.uses_rbac:
            score += 15
        if self.analysis_result.uses_rls:
            score += 10
        if self.analysis_result.uses_cors:
            score += 5
        if self.analysis_result.uses_rate_limiting:
            score += 10
        if self.analysis_result.uses_encryption:
            score += 15
        if self.analysis_result.multi_tenant_security:
            score += 10
        
        # Puntos por middleware de seguridad
        score += min(self.analysis_result.total_middleware * 2, 10)
        
        # Penalizaciones por vulnerabilidades (limitadas para evitar scores negativos excesivos)
        critical_count = sum(1 for vuln in self.analysis_result.vulnerabilities if vuln.severity == 'critical')
        high_count = sum(1 for vuln in self.analysis_result.vulnerabilities if vuln.severity == 'high')
        medium_count = sum(1 for vuln in self.analysis_result.vulnerabilities if vuln.severity == 'medium')
        low_count = sum(1 for vuln in self.analysis_result.vulnerabilities if vuln.severity == 'low')
        
        # Aplicar penalizaciones escaladas para evitar scores excesivamente bajos
        score -= min(critical_count * 15, 30)  # Máximo 30 puntos por vulnerabilidades críticas
        score -= min(high_count * 10, 20)     # Máximo 20 puntos por vulnerabilidades altas
        score -= min(medium_count * 2, 15)    # Máximo 15 puntos por vulnerabilidades medias
        score -= min(low_count * 0.5, 10)     # Máximo 10 puntos por vulnerabilidades bajas
        
        # Asegurar que el score esté entre 0-100
        self.analysis_result.security_score = max(0, min(100, score))
    
    def generate_report(self) -> str:
        """Genera un reporte en español del análisis de seguridad"""
        if not self.analysis_result:
            return "No hay análisis de seguridad disponible"
        
        report = []
        report.append(self.i18n.t('security.title'))
        
        # Características principales
        if self.analysis_result.uses_rls:
            report.append(f"- {self.i18n.t('security.rls')}")
        
        if self.analysis_result.uses_jwt:
            report.append(f"- {self.i18n.t('security.jwt')}")
        
        if self.analysis_result.uses_rbac:
            report.append(f"- {self.i18n.t('security.rbac')}")
        
        # Estadísticas
        if self.analysis_result.total_rls_policies > 0:
            report.append(f"- {self.i18n.t('security.policies', count=self.analysis_result.total_rls_policies)}")
        
        if self.analysis_result.total_roles > 0:
            report.append(f"- {self.i18n.t('security.roles', count=self.analysis_result.total_roles)}")
        
        # Score de seguridad
        report.append(f"- Puntuación de seguridad: {self.analysis_result.security_score}/100")
        
        # Vulnerabilidades críticas
        critical_vulns = sum(1 for v in self.analysis_result.vulnerabilities if v.severity == 'critical')
        if critical_vulns > 0:
            report.append(f"- ⚠️ {critical_vulns} vulnerabilidades críticas encontradas")
        
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
            "security_score": self.analysis_result.security_score,
            "uses_jwt": self.analysis_result.uses_jwt,
            "uses_refresh_tokens": self.analysis_result.uses_refresh_tokens,
            "uses_rbac": self.analysis_result.uses_rbac,
            "uses_rls": self.analysis_result.uses_rls,
            "uses_cors": self.analysis_result.uses_cors,
            "uses_rate_limiting": self.analysis_result.uses_rate_limiting,
            "multi_tenant_security": self.analysis_result.multi_tenant_security,
            "total_roles": self.analysis_result.total_roles,
            "total_permissions": self.analysis_result.total_permissions,
            "total_rls_policies": self.analysis_result.total_rls_policies,
            "total_vulnerabilities": self.analysis_result.total_vulnerabilities,
            "patterns": self.analysis_result.patterns_detected,
            "recommendations": self.analysis_result.recommendations,
            "vulnerabilities_by_severity": {
                "critical": sum(1 for v in self.analysis_result.vulnerabilities if v.severity == 'critical'),
                "high": sum(1 for v in self.analysis_result.vulnerabilities if v.severity == 'high'),
                "medium": sum(1 for v in self.analysis_result.vulnerabilities if v.severity == 'medium'),
                "low": sum(1 for v in self.analysis_result.vulnerabilities if v.severity == 'low')
            }
        }


if __name__ == "__main__":
    # Ejemplo de uso
    mapper = SecurityMapper()
    project_path = "/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla"
    
    try:
        result = mapper.analyze_project(project_path)
        print(mapper.generate_report())
        print("\n=== Resumen Técnico ===")
        summary = mapper.get_analysis_summary()
        for key, value in summary.items():
            if key not in ["patterns", "recommendations", "vulnerabilities_by_severity"]:
                print(f"{key}: {value}")
        
        if summary.get("vulnerabilities_by_severity"):
            print("\nVulnerabilidades por severidad:")
            for sev, count in summary["vulnerabilities_by_severity"].items():
                if count > 0:
                    print(f"  {sev}: {count}")
                    
    except Exception as e:
        print(f"Error: {e}")