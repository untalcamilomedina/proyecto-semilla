"""
Database Analyzer - Analizador de Base de Datos

Analiza modelos SQLAlchemy, esquemas de base de datos, relaciones y patrones
de arquitectura multi-tenant con Row-Level Security (RLS).

Características:
- Detección automática de modelos SQLAlchemy
- Análisis de relaciones entre entidades
- Identificación de patrones UUID
- Detección de arquitectura multi-tenant
- Análisis de índices y optimizaciones
- Identificación de políticas RLS
- Mapeo de dependencias entre modelos
"""

import ast
import inspect
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
from dataclasses import dataclass, field
import importlib.util
import sys

from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey, Index
from sqlalchemy import Column

from ..i18n_manager import get_i18n

logger = logging.getLogger(__name__)


@dataclass
class ColumnInfo:
    """Información detallada de una columna"""
    name: str
    type: str
    nullable: bool
    primary_key: bool
    foreign_key: Optional[str] = None
    unique: bool = False
    indexed: bool = False
    default: Any = None


@dataclass
class RelationshipInfo:
    """Información de relaciones entre modelos"""
    name: str
    model: str
    relationship_type: str  # one-to-many, many-to-one, many-to-many
    cascade: str = ""
    back_populates: Optional[str] = None


@dataclass
class ModelInfo:
    """Información completa de un modelo"""
    name: str
    table_name: str
    columns: List[ColumnInfo] = field(default_factory=list)
    relationships: List[RelationshipInfo] = field(default_factory=list)
    indexes: List[str] = field(default_factory=list)
    is_multi_tenant: bool = False
    tenant_column: Optional[str] = None
    uses_uuid: bool = False
    has_timestamps: bool = False
    docstring: Optional[str] = None


@dataclass
class DatabaseAnalysisResult:
    """Resultado completo del análisis de base de datos"""
    models: List[ModelInfo] = field(default_factory=list)
    total_models: int = 0
    total_tables: int = 0
    multi_tenant_models: int = 0
    uuid_models: int = 0
    models_with_timestamps: int = 0
    relationship_count: int = 0
    foreign_key_count: int = 0
    index_count: int = 0
    patterns_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    rls_policies: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)


class DatabaseAnalyzer:
    """Analizador de arquitectura de base de datos"""
    
    def __init__(self):
        self.i18n = get_i18n()
        self.models_cache: Dict[str, ModelInfo] = {}
        self.analysis_result: Optional[DatabaseAnalysisResult] = None
        
        # Patrones comunes para detectar
        self.uuid_patterns = ['UUID', 'uuid4', 'as_uuid=True']
        self.tenant_patterns = ['tenant_id', 'organization_id', 'company_id']
        self.timestamp_patterns = ['created_at', 'updated_at', 'timestamp']
        
    def analyze_project(self, project_path: str) -> DatabaseAnalysisResult:
        """
        Analiza todos los modelos de base de datos en un proyecto.
        
        Args:
            project_path: Ruta al directorio raíz del proyecto
            
        Returns:
            Resultado completo del análisis
        """
        logger.info(self.i18n.t('database.analyzing'))
        
        try:
            # Encontrar modelos SQLAlchemy
            models_path = self._find_models_directory(project_path)
            if not models_path:
                raise FileNotFoundError(f"No se encontró directorio de modelos en {project_path}")
            
            # Analizar cada archivo de modelo
            model_files = self._get_model_files(models_path)
            models_info = []
            
            for model_file in model_files:
                try:
                    model_info = self._analyze_model_file(model_file)
                    if model_info:
                        models_info.extend(model_info)
                except Exception as e:
                    logger.warning(f"Error analizando {model_file}: {e}")
                    continue
            
            # Crear resultado del análisis
            self.analysis_result = self._create_analysis_result(models_info)
            
            # Detectar patrones y generar recomendaciones
            self._detect_patterns()
            self._generate_recommendations()
            
            logger.info(f"Análisis completado: {len(models_info)} modelos encontrados")
            return self.analysis_result
            
        except Exception as e:
            logger.error(f"Error durante análisis de base de datos: {e}")
            raise
    
    def _find_models_directory(self, project_path: str) -> Optional[Path]:
        """Busca el directorio que contiene los modelos SQLAlchemy"""
        possible_paths = [
            Path(project_path) / "backend" / "app" / "models",
            Path(project_path) / "app" / "models", 
            Path(project_path) / "src" / "models",
            Path(project_path) / "models",
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_dir():
                # Verificar que contenga archivos Python
                py_files = list(path.glob("*.py"))
                if py_files and any(f.name != "__init__.py" for f in py_files):
                    logger.debug(f"Directorio de modelos encontrado: {path}")
                    return path
        
        return None
    
    def _get_model_files(self, models_path: Path) -> List[Path]:
        """Obtiene lista de archivos Python con modelos"""
        model_files = []
        
        for py_file in models_path.glob("*.py"):
            if py_file.name not in ["__init__.py", "__pycache__"]:
                model_files.append(py_file)
        
        return model_files
    
    def _analyze_model_file(self, file_path: Path) -> List[ModelInfo]:
        """Analiza un archivo Python buscando modelos SQLAlchemy"""
        models = []
        
        try:
            # Leer y parsear el archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parsear AST para encontrar clases
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Verificar si es un modelo SQLAlchemy
                    if self._is_sqlalchemy_model(node, content):
                        model_info = self._extract_model_info(node, content, file_path)
                        if model_info:
                            models.append(model_info)
                            
        except Exception as e:
            logger.error(f"Error parseando {file_path}: {e}")
            
        return models
    
    def _is_sqlalchemy_model(self, class_node: ast.ClassDef, content: str) -> bool:
        """Determina si una clase es un modelo SQLAlchemy"""
        # Buscar herencia de Base
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "Base":
                return True
        
        # Buscar __tablename__
        for item in class_node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == "__tablename__":
                        return True
        
        return False
    
    def _extract_model_info(self, class_node: ast.ClassDef, content: str, file_path: Path) -> Optional[ModelInfo]:
        """Extrae información completa de un modelo SQLAlchemy"""
        try:
            model_info = ModelInfo(
                name=class_node.name,
                table_name="",
                docstring=ast.get_docstring(class_node)
            )
            
            # Extraer información de la clase
            for item in class_node.body:
                if isinstance(item, ast.Assign):
                    self._process_assignment(item, model_info, content)
                elif isinstance(item, ast.FunctionDef) and item.name == "__repr__":
                    # El modelo tiene __repr__ personalizado
                    pass
            
            # Determinar nombre de tabla
            if not model_info.table_name:
                model_info.table_name = class_node.name.lower() + "s"
            
            # Detectar patrones
            self._detect_model_patterns(model_info)
            
            return model_info
            
        except Exception as e:
            logger.error(f"Error extrayendo info del modelo {class_node.name}: {e}")
            return None
    
    def _process_assignment(self, assign_node: ast.Assign, model_info: ModelInfo, content: str):
        """Procesa una asignación en el modelo (columnas, relaciones, etc.)"""
        for target in assign_node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                
                # __tablename__
                if var_name == "__tablename__":
                    if isinstance(assign_node.value, ast.Str):
                        model_info.table_name = assign_node.value.s
                    elif isinstance(assign_node.value, ast.Constant):
                        model_info.table_name = assign_node.value.value
                
                # Columnas
                elif isinstance(assign_node.value, ast.Call):
                    if self._is_column_definition(assign_node.value):
                        column_info = self._extract_column_info(var_name, assign_node.value, content)
                        if column_info:
                            model_info.columns.append(column_info)
                    
                    elif self._is_relationship_definition(assign_node.value):
                        rel_info = self._extract_relationship_info(var_name, assign_node.value)
                        if rel_info:
                            model_info.relationships.append(rel_info)
    
    def _is_column_definition(self, call_node: ast.Call) -> bool:
        """Determina si una llamada define una columna"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id == "Column"
        return False
    
    def _is_relationship_definition(self, call_node: ast.Call) -> bool:
        """Determina si una llamada define una relación"""
        if isinstance(call_node.func, ast.Name):
            return call_node.func.id == "relationship"
        return False
    
    def _extract_column_info(self, name: str, call_node: ast.Call, content: str) -> Optional[ColumnInfo]:
        """Extrae información de una columna"""
        try:
            column_info = ColumnInfo(
                name=name,
                type="Unknown",
                nullable=True,
                primary_key=False
            )
            
            # Analizar argumentos posicionales (tipo de columna)
            if call_node.args:
                first_arg = call_node.args[0]
                column_info.type = self._extract_column_type(first_arg)
            
            # Analizar argumentos con nombre
            for keyword in call_node.keywords:
                if keyword.arg == "nullable":
                    column_info.nullable = self._extract_bool_value(keyword.value)
                elif keyword.arg == "primary_key":
                    column_info.primary_key = self._extract_bool_value(keyword.value)
                elif keyword.arg == "unique":
                    column_info.unique = self._extract_bool_value(keyword.value)
                elif keyword.arg == "index":
                    column_info.indexed = self._extract_bool_value(keyword.value)
                elif keyword.arg == "default":
                    column_info.default = self._extract_default_value(keyword.value)
            
            # Detectar foreign keys
            if "ForeignKey" in content:
                # Buscar ForeignKey en argumentos
                for arg in call_node.args:
                    if isinstance(arg, ast.Call) and isinstance(arg.func, ast.Name):
                        if arg.func.id == "ForeignKey":
                            if arg.args and isinstance(arg.args[0], ast.Str):
                                column_info.foreign_key = arg.args[0].s
                            elif arg.args and isinstance(arg.args[0], ast.Constant):
                                column_info.foreign_key = arg.args[0].value
            
            return column_info
            
        except Exception as e:
            logger.warning(f"Error extrayendo info de columna {name}: {e}")
            return None
    
    def _extract_column_type(self, type_node: ast.AST) -> str:
        """Extrae el tipo de una columna"""
        if isinstance(type_node, ast.Name):
            return type_node.id
        elif isinstance(type_node, ast.Call):
            if isinstance(type_node.func, ast.Name):
                return type_node.func.id
            elif isinstance(type_node.func, ast.Attribute):
                return type_node.func.attr
        
        return "Unknown"
    
    def _extract_bool_value(self, node: ast.AST) -> bool:
        """Extrae valor booleano de un nodo AST"""
        if isinstance(node, ast.Constant):
            return bool(node.value)
        elif isinstance(node, ast.NameConstant):  # Python < 3.8
            return bool(node.value)
        return False
    
    def _extract_default_value(self, node: ast.AST) -> Any:
        """Extrae valor por defecto de un nodo AST"""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Num):
            return node.n
        return None
    
    def _extract_relationship_info(self, name: str, call_node: ast.Call) -> Optional[RelationshipInfo]:
        """Extrae información de una relación"""
        try:
            rel_info = RelationshipInfo(
                name=name,
                model="Unknown",
                relationship_type="unknown"
            )
            
            # Modelo relacionado (primer argumento)
            if call_node.args and isinstance(call_node.args[0], ast.Str):
                rel_info.model = call_node.args[0].s
            elif call_node.args and isinstance(call_node.args[0], ast.Constant):
                rel_info.model = call_node.args[0].value
            
            # Argumentos con nombre
            for keyword in call_node.keywords:
                if keyword.arg == "back_populates":
                    if isinstance(keyword.value, ast.Str):
                        rel_info.back_populates = keyword.value.s
                    elif isinstance(keyword.value, ast.Constant):
                        rel_info.back_populates = keyword.value.value
                elif keyword.arg == "cascade":
                    if isinstance(keyword.value, ast.Str):
                        rel_info.cascade = keyword.value.s
                    elif isinstance(keyword.value, ast.Constant):
                        rel_info.cascade = keyword.value.value
            
            return rel_info
            
        except Exception as e:
            logger.warning(f"Error extrayendo relación {name}: {e}")
            return None
    
    def _detect_model_patterns(self, model_info: ModelInfo):
        """Detecta patrones comunes en el modelo"""
        # Detectar multi-tenancy
        for column in model_info.columns:
            if any(pattern in column.name for pattern in self.tenant_patterns):
                model_info.is_multi_tenant = True
                model_info.tenant_column = column.name
                break
        
        # Detectar UUID
        for column in model_info.columns:
            if any(pattern in column.type for pattern in self.uuid_patterns):
                model_info.uses_uuid = True
                break
        
        # Detectar timestamps
        timestamp_columns = [col.name for col in model_info.columns]
        if any(pattern in timestamp_columns for pattern in self.timestamp_patterns):
            model_info.has_timestamps = True
    
    def _create_analysis_result(self, models_info: List[ModelInfo]) -> DatabaseAnalysisResult:
        """Crea el resultado del análisis con estadísticas"""
        result = DatabaseAnalysisResult()
        result.models = models_info
        result.total_models = len(models_info)
        
        # Calcular estadísticas
        for model in models_info:
            result.total_tables += 1
            result.relationship_count += len(model.relationships)
            result.index_count += len(model.indexes)
            
            if model.is_multi_tenant:
                result.multi_tenant_models += 1
            
            if model.uses_uuid:
                result.uuid_models += 1
                
            if model.has_timestamps:
                result.models_with_timestamps += 1
            
            # Contar foreign keys
            for column in model.columns:
                if column.foreign_key:
                    result.foreign_key_count += 1
        
        return result
    
    def _detect_patterns(self):
        """Detecta patrones arquitectónicos en la base de datos"""
        if not self.analysis_result:
            return
        
        patterns = []
        
        # Patrón multi-tenant
        if self.analysis_result.multi_tenant_models > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='Multi-Tenant Architecture'))
        
        # Patrón UUID
        if self.analysis_result.uuid_models > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='UUID Primary Keys'))
        
        # Timestamps automáticos
        if self.analysis_result.models_with_timestamps > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='Automatic Timestamps'))
        
        # Relaciones consistentes
        if self.analysis_result.relationship_count > 0:
            patterns.append(self.i18n.t('patterns.detected', pattern='Consistent Relationships'))
        
        self.analysis_result.patterns_detected = patterns
    
    def _generate_recommendations(self):
        """Genera recomendaciones basadas en el análisis"""
        if not self.analysis_result:
            return
        
        recommendations = []
        
        # Recomendaciones multi-tenant
        if self.analysis_result.multi_tenant_models > 0:
            recommendations.append(self.i18n.t('recommendations.rls_policies'))
            recommendations.append(self.i18n.t('recommendations.user_tenant_role'))
        
        # Recomendaciones de índices
        if self.analysis_result.foreign_key_count > self.analysis_result.index_count:
            recommendations.append("Considerar agregar índices adicionales para foreign keys")
        
        # Recomendaciones de patrones
        recommendations.append(self.i18n.t('recommendations.repository_pattern'))
        recommendations.append(self.i18n.t('recommendations.testing'))
        
        self.analysis_result.recommendations = recommendations
    
    def get_model_dependencies(self) -> Dict[str, List[str]]:
        """Analiza dependencias entre modelos"""
        if not self.analysis_result:
            return {}
        
        dependencies = {}
        
        for model in self.analysis_result.models:
            deps = []
            
            # Dependencias por foreign keys
            for column in model.columns:
                if column.foreign_key:
                    table_name = column.foreign_key.split('.')[0]
                    deps.append(table_name)
            
            # Dependencias por relaciones
            for rel in model.relationships:
                deps.append(rel.model)
            
            dependencies[model.name] = list(set(deps))
        
        return dependencies
    
    def generate_report(self) -> str:
        """Genera un reporte en español del análisis"""
        if not self.analysis_result:
            return "No hay análisis disponible"
        
        report = []
        report.append(self.i18n.t('analysis.title'))
        report.append("")
        report.append(self.i18n.t('database.title'))
        
        # Estadísticas generales
        if self.analysis_result.multi_tenant_models > 0:
            report.append(f"- {self.i18n.t('database.multitenant')}")
        
        if self.analysis_result.uuid_models > 0:
            report.append(f"- {self.i18n.t('database.uuid_pattern')}")
        
        report.append(f"- {self.i18n.t('database.entities', count=self.analysis_result.total_models)}")
        
        if self.analysis_result.relationship_count > 0:
            rel_types = "One-to-many, many-to-many"
            report.append(f"- {self.i18n.t('database.relationships', types=rel_types)}")
        
        # Patrones detectados
        if self.analysis_result.patterns_detected:
            report.append("")
            for pattern in self.analysis_result.patterns_detected:
                report.append(f"- {pattern}")
        
        return "\n".join(report)
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Retorna resumen del análisis para integración con otros componentes"""
        if not self.analysis_result:
            return {}
        
        return {
            "total_models": self.analysis_result.total_models,
            "multi_tenant": self.analysis_result.multi_tenant_models > 0,
            "uses_uuid": self.analysis_result.uuid_models > 0,
            "has_relationships": self.analysis_result.relationship_count > 0,
            "patterns": self.analysis_result.patterns_detected,
            "recommendations": self.analysis_result.recommendations,
            "models": [
                {
                    "name": model.name,
                    "table": model.table_name,
                    "columns": len(model.columns),
                    "relationships": len(model.relationships),
                    "multi_tenant": model.is_multi_tenant,
                    "uuid": model.uses_uuid,
                    "timestamps": model.has_timestamps
                }
                for model in self.analysis_result.models
            ]
        }


if __name__ == "__main__":
    # Ejemplo de uso
    analyzer = DatabaseAnalyzer()
    project_path = "/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla"
    
    try:
        result = analyzer.analyze_project(project_path)
        print(analyzer.generate_report())
        print("\n=== Resumen Técnico ===")
        summary = analyzer.get_analysis_summary()
        for key, value in summary.items():
            if key != "models":
                print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")