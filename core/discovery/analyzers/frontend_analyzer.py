"""
Frontend Analyzer - Analizador de Arquitectura Frontend

Analiza componentes React/Next.js, patrones de estado, estilos, y arquitectura
general del frontend.

Características:
- Detección de componentes React/Next.js
- Análisis de hooks y estado local vs global
- Identificación de patrones de estilo (Tailwind, CSS Modules, etc.)
- Mapeo de rutas y pages
- Análisis de gestión de estado (Context API, Zustand, etc.)
- Detección de librerías UI utilizadas
- Identificación de patrones de formularios
"""

import ast
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass, field

from ..i18n_manager import get_i18n

logger = logging.getLogger(__name__)


@dataclass
class ComponentInfo:
    """Información detallada de un componente React"""
    name: str
    file_path: str
    component_type: str  # functional, class, page, layout
    props: List[str] = field(default_factory=list)
    hooks_used: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    children_components: List[str] = field(default_factory=list)
    styling_approach: str = "unknown"  # tailwind, css-modules, styled-components, etc.
    has_state: bool = False
    uses_context: bool = False
    is_server_component: bool = False
    is_client_component: bool = False
    description: Optional[str] = None


@dataclass
class PageInfo:
    """Información de páginas Next.js"""
    path: str
    file_path: str
    route: str
    layout: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_dynamic: bool = False
    params: List[str] = field(default_factory=list)


@dataclass
class HookInfo:
    """Información de hooks personalizados"""
    name: str
    file_path: str
    dependencies: List[str] = field(default_factory=list)
    returns_type: str = "unknown"
    description: Optional[str] = None


@dataclass
class FrontendAnalysisResult:
    """Resultado completo del análisis de frontend"""
    components: List[ComponentInfo] = field(default_factory=list)
    pages: List[PageInfo] = field(default_factory=list)
    hooks: List[HookInfo] = field(default_factory=list)
    
    # Estadísticas
    total_components: int = 0
    functional_components: int = 0
    class_components: int = 0
    total_pages: int = 0
    total_hooks: int = 0
    
    # Tecnologías detectadas
    framework: str = ""  # Next.js, React, etc.
    ui_libraries: List[str] = field(default_factory=list)
    styling_approach: str = ""  # tailwind, css-modules, etc.
    state_management: List[str] = field(default_factory=list)
    form_libraries: List[str] = field(default_factory=list)
    testing_libraries: List[str] = field(default_factory=list)
    
    # Configuración
    typescript_usage: bool = False
    next_config: Dict[str, Any] = field(default_factory=dict)
    package_json: Dict[str, Any] = field(default_factory=dict)
    
    # Patrones detectados
    patterns_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Arquitectura
    routing_type: str = ""  # app-router, pages-router
    internationalization: bool = False
    pwa_support: bool = False


class FrontendAnalyzer:
    """Analizador de arquitectura frontend React/Next.js"""
    
    def __init__(self):
        self.i18n = get_i18n()
        self.analysis_result: Optional[FrontendAnalysisResult] = None
        
        # Patrones de componentes React
        self.react_patterns = [
            r'function\s+(\w+)\s*\(',
            r'const\s+(\w+)\s*=\s*\(',
            r'export\s+default\s+function\s+(\w+)',
            r'class\s+(\w+)\s+extends\s+React\.Component',
            r'class\s+(\w+)\s+extends\s+Component'
        ]
        
        # Hooks React
        self.react_hooks = [
            'useState', 'useEffect', 'useContext', 'useReducer',
            'useCallback', 'useMemo', 'useRef', 'useImperativeHandle',
            'useLayoutEffect', 'useDebugValue'
        ]
        
        # Next.js hooks
        self.nextjs_hooks = [
            'useRouter', 'usePathname', 'useSearchParams',
            'useParams', 'useSelectedLayoutSegment'
        ]
        
        # Librerías UI comunes
        self.ui_libraries = {
            '@radix-ui': 'Radix UI',
            '@mui/material': 'Material-UI',
            '@chakra-ui': 'Chakra UI',
            'antd': 'Ant Design',
            '@mantine': 'Mantine',
            'react-bootstrap': 'React Bootstrap'
        }
        
        # Gestión de estado
        self.state_management = {
            'zustand': 'Zustand',
            'redux': 'Redux',
            '@reduxjs/toolkit': 'Redux Toolkit',
            'recoil': 'Recoil',
            'jotai': 'Jotai',
            'valtio': 'Valtio'
        }
        
        # Librerías de formularios
        self.form_libraries = {
            'react-hook-form': 'React Hook Form',
            'formik': 'Formik',
            'react-final-form': 'React Final Form'
        }
        
        # Librerías de testing
        self.testing_libraries = {
            '@testing-library': 'React Testing Library',
            'jest': 'Jest',
            'playwright': 'Playwright',
            'cypress': 'Cypress',
            'enzyme': 'Enzyme'
        }
    
    def analyze_project(self, project_path: str) -> FrontendAnalysisResult:
        """
        Analiza toda la estructura de frontend de un proyecto.
        
        Args:
            project_path: Ruta al directorio raíz del proyecto
            
        Returns:
            Resultado completo del análisis de frontend
        """
        logger.info(self.i18n.t('frontend.analyzing'))
        
        try:
            # Encontrar directorio de frontend
            frontend_path = self._find_frontend_directory(project_path)
            if not frontend_path:
                raise FileNotFoundError("No se encontró directorio de frontend")
            
            # Analizar package.json
            package_json = self._analyze_package_json(frontend_path)
            
            # Analizar configuración Next.js
            next_config = self._analyze_next_config(frontend_path)
            
            # Encontrar archivos de componentes
            component_files = self._find_component_files(frontend_path)
            components = []
            
            for file_path in component_files:
                try:
                    component_info = self._analyze_component_file(file_path, frontend_path)
                    if component_info:
                        components.extend(component_info)
                except Exception as e:
                    logger.warning(f"Error analizando componente {file_path}: {e}")
                    continue
            
            # Analizar páginas (Next.js)
            pages = self._analyze_pages(frontend_path)
            
            # Analizar hooks personalizados
            hooks = self._analyze_custom_hooks(frontend_path)
            
            # Crear resultado del análisis
            self.analysis_result = self._create_analysis_result(
                components, pages, hooks, package_json, next_config
            )
            
            # Detectar patrones y generar recomendaciones
            self._detect_frontend_patterns()
            self._generate_frontend_recommendations()
            
            logger.info(f"Análisis de frontend completado: {len(components)} componentes encontrados")
            return self.analysis_result
            
        except Exception as e:
            logger.error(f"Error durante análisis de frontend: {e}")
            raise
    
    def _find_frontend_directory(self, project_path: str) -> Optional[Path]:
        """Busca el directorio de frontend"""
        possible_paths = [
            Path(project_path) / "frontend",
            Path(project_path) / "client",
            Path(project_path) / "web",
            Path(project_path) / "app",
            Path(project_path) / "ui"
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                # Verificar que tenga package.json
                if (path / "package.json").exists():
                    logger.debug(f"Directorio de frontend encontrado: {path}")
                    return path
        
        return None
    
    def _analyze_package_json(self, frontend_path: Path) -> Dict[str, Any]:
        """Analiza el package.json del frontend"""
        package_json_path = frontend_path / "package.json"
        
        if not package_json_path.exists():
            return {}
        
        try:
            with open(package_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error leyendo package.json: {e}")
            return {}
    
    def _analyze_next_config(self, frontend_path: Path) -> Dict[str, Any]:
        """Analiza la configuración de Next.js"""
        config_files = [
            "next.config.js",
            "next.config.mjs",
            "next.config.ts"
        ]
        
        for config_file in config_files:
            config_path = frontend_path / config_file
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Extracción básica de configuración
                        return self._parse_next_config(content)
                except Exception as e:
                    logger.warning(f"Error leyendo {config_file}: {e}")
        
        return {}
    
    def _parse_next_config(self, content: str) -> Dict[str, Any]:
        """Parser básico para configuración Next.js"""
        config = {}
        
        # Detectar configuraciones comunes
        if "experimental" in content:
            config["has_experimental"] = True
        
        if "appDir" in content:
            config["app_directory"] = True
        
        if "images" in content:
            config["image_optimization"] = True
        
        if "i18n" in content:
            config["internationalization"] = True
        
        return config
    
    def _find_component_files(self, frontend_path: Path) -> List[Path]:
        """Busca archivos de componentes React"""
        component_files = []
        
        # Patrones de búsqueda
        patterns = [
            "**/*.tsx",
            "**/*.jsx",
            "**/*.ts",  # Solo si contienen JSX
            "**/*.js"   # Solo si contienen JSX
        ]
        
        for pattern in patterns:
            for file_path in frontend_path.glob(pattern):
                if self._is_component_file(file_path):
                    component_files.append(file_path)
        
        return component_files
    
    def _is_component_file(self, file_path: Path) -> bool:
        """Determina si un archivo contiene componentes React"""
        # Excluir ciertos directorios
        excluded_dirs = {
            'node_modules', '.next', 'dist', 'build',
            '__pycache__', '.git', 'coverage'
        }
        
        if any(excluded in file_path.parts for excluded in excluded_dirs):
            return False
        
        # Verificar extensión
        if file_path.suffix not in {'.tsx', '.jsx', '.ts', '.js'}:
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Buscar indicadores de componentes React
                react_indicators = [
                    'import React', 'from "react"', "from 'react'",
                    'import { ', 'export default function',
                    'export function', '</', 'jsx', 'tsx'
                ]
                
                return any(indicator in content for indicator in react_indicators)
                
        except Exception:
            return False
    
    def _analyze_component_file(self, file_path: Path, frontend_path: Path) -> List[ComponentInfo]:
        """Analiza un archivo de componente React"""
        components = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detectar si es TypeScript
            is_typescript = file_path.suffix in {'.tsx', '.ts'}
            
            # Parsear AST si es posible
            try:
                # Para archivos TypeScript, solo análisis de texto
                if is_typescript:
                    components.extend(self._analyze_tsx_content(content, file_path, frontend_path))
                else:
                    # Análisis AST para JavaScript
                    tree = ast.parse(content)
                    components.extend(self._analyze_ast_components(tree, content, file_path, frontend_path))
            except:
                # Fallback a análisis de texto
                components.extend(self._analyze_text_components(content, file_path, frontend_path))
                
        except Exception as e:
            logger.error(f"Error analizando componente {file_path}: {e}")
        
        return components
    
    def _analyze_tsx_content(self, content: str, file_path: Path, frontend_path: Path) -> List[ComponentInfo]:
        """Analiza contenido TSX usando expresiones regulares"""
        components = []
        
        # Buscar componentes funcionales
        patterns = [
            r'export\s+default\s+function\s+(\w+)',
            r'function\s+(\w+)\s*\([^)]*\)\s*{',
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>\s*{',
            r'const\s+(\w+):\s*React\.FC'
        ]
        
        found_components = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                component_name = match.group(1)
                if component_name and component_name[0].isupper():  # Componentes empiezan con mayúscula
                    if component_name not in found_components:
                        found_components.add(component_name)
                        
                        component_info = ComponentInfo(
                            name=component_name,
                            file_path=str(file_path.relative_to(frontend_path)),
                            component_type="functional"
                        )
                        
                        # Analizar detalles del componente
                        self._extract_component_details(component_info, content)
                        components.append(component_info)
        
        return components
    
    def _analyze_ast_components(self, tree: ast.AST, content: str, 
                               file_path: Path, frontend_path: Path) -> List[ComponentInfo]:
        """Analiza componentes usando AST de Python (limitado para JS/TS)"""
        components = []
        
        # Esto es limitado para JavaScript/TypeScript, pero puede detectar algunas funciones
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name and node.name[0].isupper():  # Componentes empiezan con mayúscula
                    component_info = ComponentInfo(
                        name=node.name,
                        file_path=str(file_path.relative_to(frontend_path)),
                        component_type="functional",
                        description=ast.get_docstring(node)
                    )
                    self._extract_component_details(component_info, content)
                    components.append(component_info)
        
        return components
    
    def _analyze_text_components(self, content: str, file_path: Path, frontend_path: Path) -> List[ComponentInfo]:
        """Análisis de texto como fallback"""
        components = []
        
        # Buscar export default
        export_match = re.search(r'export\s+default\s+(\w+)', content)
        if export_match:
            component_name = export_match.group(1)
            if component_name[0].isupper():
                component_info = ComponentInfo(
                    name=component_name,
                    file_path=str(file_path.relative_to(frontend_path)),
                    component_type="functional"
                )
                self._extract_component_details(component_info, content)
                components.append(component_info)
        
        return components
    
    def _extract_component_details(self, component_info: ComponentInfo, content: str):
        """Extrae detalles adicionales del componente"""
        # Detectar hooks utilizados
        for hook in self.react_hooks + self.nextjs_hooks:
            if hook in content:
                component_info.hooks_used.append(hook)
        
        # Detectar si tiene estado
        if any(hook in content for hook in ['useState', 'useReducer']):
            component_info.has_state = True
        
        # Detectar uso de Context
        if 'useContext' in content or 'Context' in content:
            component_info.uses_context = True
        
        # Detectar enfoque de estilos
        if 'className=' in content and ('tw-' in content or 'bg-' in content or 'text-' in content):
            component_info.styling_approach = "tailwind"
        elif '.module.css' in content:
            component_info.styling_approach = "css-modules"
        elif 'styled-components' in content:
            component_info.styling_approach = "styled-components"
        elif 'className=' in content:
            component_info.styling_approach = "css"
        
        # Detectar directivas Next.js
        if "'use client'" in content or '"use client"' in content:
            component_info.is_client_component = True
        elif "'use server'" in content or '"use server"' in content:
            component_info.is_server_component = True
        
        # Extraer imports
        import_matches = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
        component_info.imports = import_matches
    
    def _analyze_pages(self, frontend_path: Path) -> List[PageInfo]:
        """Analiza páginas Next.js"""
        pages = []
        
        # Buscar en app directory (App Router)
        app_dir = frontend_path / "src" / "app"
        if not app_dir.exists():
            app_dir = frontend_path / "app"
        
        if app_dir.exists():
            pages.extend(self._analyze_app_router_pages(app_dir, frontend_path))
        
        # Buscar en pages directory (Pages Router)
        pages_dir = frontend_path / "src" / "pages"
        if not pages_dir.exists():
            pages_dir = frontend_path / "pages"
        
        if pages_dir.exists():
            pages.extend(self._analyze_pages_router_pages(pages_dir, frontend_path))
        
        return pages
    
    def _analyze_app_router_pages(self, app_dir: Path, frontend_path: Path) -> List[PageInfo]:
        """Analiza páginas del App Router de Next.js"""
        pages = []
        
        for page_file in app_dir.rglob("page.*"):
            if page_file.suffix in {'.tsx', '.jsx', '.ts', '.js'}:
                relative_path = page_file.relative_to(app_dir)
                route = self._convert_app_router_path_to_route(relative_path)
                
                page_info = PageInfo(
                    path=str(page_file.relative_to(frontend_path)),
                    file_path=str(page_file),
                    route=route,
                    is_dynamic="[" in str(relative_path)
                )
                
                # Extraer parámetros dinámicos
                if page_info.is_dynamic:
                    page_info.params = self._extract_dynamic_params(str(relative_path))
                
                pages.append(page_info)
        
        return pages
    
    def _analyze_pages_router_pages(self, pages_dir: Path, frontend_path: Path) -> List[PageInfo]:
        """Analiza páginas del Pages Router de Next.js"""
        pages = []
        
        for page_file in pages_dir.rglob("*"):
            if (page_file.suffix in {'.tsx', '.jsx', '.ts', '.js'} and
                not page_file.name.startswith('_')):
                
                relative_path = page_file.relative_to(pages_dir)
                route = self._convert_pages_router_path_to_route(relative_path)
                
                page_info = PageInfo(
                    path=str(page_file.relative_to(frontend_path)),
                    file_path=str(page_file),
                    route=route,
                    is_dynamic="[" in str(relative_path)
                )
                
                if page_info.is_dynamic:
                    page_info.params = self._extract_dynamic_params(str(relative_path))
                
                pages.append(page_info)
        
        return pages
    
    def _convert_app_router_path_to_route(self, path: Path) -> str:
        """Convierte path del App Router a ruta URL"""
        parts = path.parts[:-1]  # Excluir 'page.tsx'
        route_parts = []
        
        for part in parts:
            if part.startswith('(') and part.endswith(')'):
                continue  # Route groups
            elif part.startswith('[') and part.endswith(']'):
                route_parts.append(f"/{part}")  # Dynamic route
            else:
                route_parts.append(f"/{part}")
        
        return "".join(route_parts) or "/"
    
    def _convert_pages_router_path_to_route(self, path: Path) -> str:
        """Convierte path del Pages Router a ruta URL"""
        path_str = str(path)
        
        # Remover extensión
        path_str = re.sub(r'\.(tsx|jsx|ts|js)$', '', path_str)
        
        # Convertir index a /
        if path_str == "index":
            return "/"
        
        # Agregar / al inicio
        route = "/" + path_str.replace("\\", "/")  # Windows compatibility
        
        return route
    
    def _extract_dynamic_params(self, path: str) -> List[str]:
        """Extrae parámetros dinámicos de una ruta"""
        params = []
        matches = re.findall(r'\[([^\]]+)\]', path)
        
        for match in matches:
            if match.startswith('...'):
                params.append(f"...{match[3:]}")  # Catch-all route
            else:
                params.append(match)
        
        return params
    
    def _analyze_custom_hooks(self, frontend_path: Path) -> List[HookInfo]:
        """Analiza hooks personalizados"""
        hooks = []
        
        # Buscar archivos que contengan hooks (empiezan con 'use')
        hook_patterns = [
            "**/use*.tsx",
            "**/use*.ts",
            "**/hooks/**/*.tsx",
            "**/hooks/**/*.ts"
        ]
        
        for pattern in hook_patterns:
            for file_path in frontend_path.glob(pattern):
                if self._is_hook_file(file_path):
                    try:
                        hook_info = self._analyze_hook_file(file_path, frontend_path)
                        if hook_info:
                            hooks.extend(hook_info)
                    except Exception as e:
                        logger.warning(f"Error analizando hook {file_path}: {e}")
        
        return hooks
    
    def _is_hook_file(self, file_path: Path) -> bool:
        """Determina si un archivo contiene hooks personalizados"""
        return (file_path.stem.startswith('use') and 
                file_path.suffix in {'.tsx', '.ts', '.jsx', '.js'})
    
    def _analyze_hook_file(self, file_path: Path, frontend_path: Path) -> List[HookInfo]:
        """Analiza archivo de hook personalizado"""
        hooks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar funciones que empiecen con 'use'
            hook_matches = re.findall(r'export\s+(?:const\s+|function\s+)(use\w+)', content)
            
            for hook_name in hook_matches:
                hook_info = HookInfo(
                    name=hook_name,
                    file_path=str(file_path.relative_to(frontend_path))
                )
                
                # Buscar dependencias (otros hooks utilizados)
                for react_hook in self.react_hooks + self.nextjs_hooks:
                    if react_hook in content:
                        hook_info.dependencies.append(react_hook)
                
                hooks.append(hook_info)
                
        except Exception as e:
            logger.error(f"Error analizando hook {file_path}: {e}")
        
        return hooks
    
    def _create_analysis_result(self, components: List[ComponentInfo], 
                               pages: List[PageInfo], hooks: List[HookInfo],
                               package_json: Dict[str, Any], 
                               next_config: Dict[str, Any]) -> FrontendAnalysisResult:
        """Crea el resultado del análisis con estadísticas"""
        result = FrontendAnalysisResult()
        
        result.components = components
        result.pages = pages
        result.hooks = hooks
        result.package_json = package_json
        result.next_config = next_config
        
        # Estadísticas básicas
        result.total_components = len(components)
        result.functional_components = sum(1 for c in components if c.component_type == "functional")
        result.class_components = sum(1 for c in components if c.component_type == "class")
        result.total_pages = len(pages)
        result.total_hooks = len(hooks)
        
        # Detectar framework
        dependencies = package_json.get("dependencies", {})
        if "next" in dependencies:
            result.framework = "Next.js"
            
            # Detectar tipo de routing
            if any("app" in page.path for page in pages):
                result.routing_type = "app-router"
            else:
                result.routing_type = "pages-router"
        elif "react" in dependencies:
            result.framework = "React"
        
        # Detectar TypeScript
        dev_deps = package_json.get("devDependencies", {})
        result.typescript_usage = "typescript" in dependencies or "typescript" in dev_deps
        
        # Detectar librerías
        all_deps = {**dependencies, **dev_deps}
        
        # UI Libraries
        for dep, name in self.ui_libraries.items():
            if any(dep in d for d in all_deps.keys()):
                result.ui_libraries.append(name)
        
        # State Management
        for dep, name in self.state_management.items():
            if dep in all_deps:
                result.state_management.append(name)
        
        # Form Libraries
        for dep, name in self.form_libraries.items():
            if dep in all_deps:
                result.form_libraries.append(name)
        
        # Testing Libraries
        for dep, name in self.testing_libraries.items():
            if any(dep in d for d in all_deps.keys()):
                result.testing_libraries.append(name)
        
        # Detectar enfoque de estilos
        if "tailwindcss" in all_deps:
            result.styling_approach = "tailwind"
        elif any(".module.css" in c.styling_approach for c in components):
            result.styling_approach = "css-modules"
        elif "styled-components" in all_deps:
            result.styling_approach = "styled-components"
        else:
            result.styling_approach = "css"
        
        # Detectar i18n
        if "next-intl" in all_deps or "react-i18next" in all_deps:
            result.internationalization = True
        
        return result
    
    def _detect_frontend_patterns(self):
        """Detecta patrones arquitectónicos en el frontend"""
        if not self.analysis_result:
            return
        
        patterns = []
        
        # Framework y arquitectura
        if self.analysis_result.framework:
            patterns.append(self.i18n.t('patterns.detected', pattern=self.analysis_result.framework))
        
        if self.analysis_result.typescript_usage:
            patterns.append(self.i18n.t('patterns.detected', pattern='TypeScript'))
        
        # Componentes funcionales vs clase
        if self.analysis_result.functional_components > self.analysis_result.class_components:
            patterns.append(self.i18n.t('patterns.detected', pattern='Functional Components'))
        
        # Estilos
        if self.analysis_result.styling_approach:
            patterns.append(self.i18n.t('patterns.detected', pattern=f'{self.analysis_result.styling_approach.title()} Styling'))
        
        # Gestión de estado
        if self.analysis_result.state_management:
            for sm in self.analysis_result.state_management:
                patterns.append(self.i18n.t('patterns.detected', pattern=f'{sm} State Management'))
        
        # Context API
        context_usage = sum(1 for c in self.analysis_result.components if c.uses_context)
        if context_usage > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='Context API'))
        
        # Hooks personalizados
        if self.analysis_result.total_hooks > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='Custom Hooks'))
        
        # Internacionalización
        if self.analysis_result.internationalization:
            patterns.append(self.i18n.t('patterns.detected', pattern='Internationalization'))
        
        self.analysis_result.patterns_detected = patterns
    
    def _generate_frontend_recommendations(self):
        """Genera recomendaciones basadas en el análisis"""
        if not self.analysis_result:
            return
        
        recommendations = []
        
        # TypeScript
        if not self.analysis_result.typescript_usage:
            recommendations.append("Considerar migrar a TypeScript para mejor type safety")
        
        # Testing
        if not self.analysis_result.testing_libraries:
            recommendations.append("Implementar testing con React Testing Library y Jest")
        
        # Performance
        if self.analysis_result.total_components > 50:
            recommendations.append("Considerar code splitting y lazy loading para componentes")
        
        # Estado
        component_with_state = sum(1 for c in self.analysis_result.components if c.has_state)
        if component_with_state > 10 and not self.analysis_result.state_management:
            recommendations.append("Considerar implementar gestión de estado global (Zustand, Redux)")
        
        # Estilos
        if self.analysis_result.styling_approach == "css":
            recommendations.append("Considerar adoptar Tailwind CSS o CSS-in-JS para mejor mantenibilidad")
        
        # Hooks personalizados
        if self.analysis_result.total_hooks == 0 and self.analysis_result.total_components > 20:
            recommendations.append("Crear hooks personalizados para lógica reutilizable")
        
        self.analysis_result.recommendations = recommendations
    
    def generate_report(self) -> str:
        """Genera un reporte en español del análisis de frontend"""
        if not self.analysis_result:
            return "No hay análisis de frontend disponible"
        
        report = []
        report.append(self.i18n.t('frontend.title'))
        
        # Framework y tecnologías
        if self.analysis_result.framework:
            if self.analysis_result.typescript_usage:
                report.append(f"- {self.i18n.t('frontend.react')} ({self.analysis_result.framework} con TypeScript)")
            else:
                report.append(f"- {self.analysis_result.framework}")
        
        report.append(f"- {self.i18n.t('frontend.components')}")
        
        # Estilos
        if self.analysis_result.styling_approach:
            styling_map = {
                "tailwind": "Tailwind CSS para estilos",
                "css-modules": "CSS Modules para estilos",
                "styled-components": "Styled Components para estilos",
                "css": "CSS tradicional para estilos"
            }
            report.append(f"- {styling_map.get(self.analysis_result.styling_approach, 'Sistema de estilos personalizado')}")
        
        # Gestión de estado
        if self.analysis_result.state_management:
            sm_text = " y ".join(self.analysis_result.state_management)
            report.append(f"- Gestión de estado con {sm_text}")
        else:
            report.append(f"- {self.i18n.t('frontend.state')}")
        
        # Estadísticas
        report.append(f"- {self.i18n.t('frontend.pages', count=self.analysis_result.total_pages)}")
        report.append(f"- {self.i18n.t('frontend.components_count', count=self.analysis_result.total_components)}")
        
        if self.analysis_result.total_hooks > 0:
            report.append(f"- {self.analysis_result.total_hooks} hooks personalizados")
        
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
            "framework": self.analysis_result.framework,
            "typescript_usage": self.analysis_result.typescript_usage,
            "total_components": self.analysis_result.total_components,
            "total_pages": self.analysis_result.total_pages,
            "total_hooks": self.analysis_result.total_hooks,
            "styling_approach": self.analysis_result.styling_approach,
            "state_management": self.analysis_result.state_management,
            "ui_libraries": self.analysis_result.ui_libraries,
            "form_libraries": self.analysis_result.form_libraries,
            "testing_libraries": self.analysis_result.testing_libraries,
            "routing_type": self.analysis_result.routing_type,
            "internationalization": self.analysis_result.internationalization,
            "patterns": self.analysis_result.patterns_detected,
            "recommendations": self.analysis_result.recommendations
        }


if __name__ == "__main__":
    # Ejemplo de uso
    analyzer = FrontendAnalyzer()
    project_path = "/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla"
    
    try:
        result = analyzer.analyze_project(project_path)
        print(analyzer.generate_report())
        print("\n=== Resumen Técnico ===")
        summary = analyzer.get_analysis_summary()
        for key, value in summary.items():
            if key not in ["patterns", "recommendations"]:
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")