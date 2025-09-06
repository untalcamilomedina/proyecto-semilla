"""
Pattern Recognizer - Reconocedor de Patrones con IA

Utiliza técnicas de inteligencia artificial para reconocer patrones arquitectónicos
complejos, hacer recomendaciones inteligentes y predecir posibles problemas.

Características:
- Reconocimiento de patrones arquitectónicos usando heurísticas avanzadas
- Análisis semántico de código para detectar intenciones de diseño
- Generación de recomendaciones contextuales inteligentes
- Detección de anti-patrones y code smells
- Predicción de áreas problemáticas futuras
- Análisis de consistencia arquitectónica
- Sugerencias de refactoring basadas en mejores prácticas
"""

import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
import logging
from dataclasses import dataclass, field
from collections import Counter, defaultdict
import json

from ..i18n_manager import get_i18n

logger = logging.getLogger(__name__)


@dataclass
class ArchitecturalPattern:
    """Patrón arquitectónico detectado"""
    name: str
    type: str  # design_pattern, architectural_pattern, integration_pattern
    confidence: float  # 0.0 - 1.0
    evidence: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    description: str = ""
    benefits: List[str] = field(default_factory=list)
    drawbacks: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class AntiPattern:
    """Anti-patrón o code smell detectado"""
    name: str
    severity: str  # low, medium, high, critical
    occurrences: int
    files: List[str] = field(default_factory=list)
    description: str = ""
    impact: str = ""
    refactoring_suggestion: str = ""
    examples: List[str] = field(default_factory=list)


@dataclass
class SmartRecommendation:
    """Recomendación inteligente generada por IA"""
    category: str  # architecture, performance, security, maintainability
    priority: str  # low, medium, high, critical
    title: str
    description: str
    rationale: str
    implementation_steps: List[str] = field(default_factory=list)
    estimated_effort: str = ""  # low, medium, high
    potential_impact: str = ""
    prerequisites: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)


@dataclass
class ConsistencyIssue:
    """Problema de consistencia arquitectónica"""
    type: str  # naming, structure, pattern_usage, technology_choice
    severity: str
    description: str
    inconsistent_elements: List[str] = field(default_factory=list)
    suggested_standard: str = ""
    files_affected: List[str] = field(default_factory=list)


@dataclass
class PatternRecognitionResult:
    """Resultado completo del reconocimiento de patrones"""
    architectural_patterns: List[ArchitecturalPattern] = field(default_factory=list)
    anti_patterns: List[AntiPattern] = field(default_factory=list)
    smart_recommendations: List[SmartRecommendation] = field(default_factory=list)
    consistency_issues: List[ConsistencyIssue] = field(default_factory=list)
    
    # Métricas de calidad
    architecture_score: float = 0.0  # 0.0 - 10.0
    maintainability_score: float = 0.0
    consistency_score: float = 0.0
    complexity_score: float = 0.0
    
    # Análisis predictivo
    risk_areas: List[str] = field(default_factory=list)
    growth_recommendations: List[str] = field(default_factory=list)
    technology_evolution: List[str] = field(default_factory=list)


class PatternRecognizer:
    """Reconocedor de patrones arquitectónicos con IA"""
    
    def __init__(self):
        self.i18n = get_i18n()
        self.analysis_result: Optional[PatternRecognitionResult] = None
        
        # Base de conocimiento de patrones arquitectónicos
        self.architectural_patterns = {
            "Repository Pattern": {
                "type": "design_pattern",
                "indicators": [
                    r"class\s+\w*Repository",
                    r"def\s+get_by_id",
                    r"def\s+create",
                    r"def\s+update",
                    r"def\s+delete",
                    r"@abstractmethod"
                ],
                "files": ["repository", "repo"],
                "benefits": ["Abstracción de acceso a datos", "Testabilidad", "Mantenibilidad"],
                "description": "Abstrae el acceso a la capa de datos"
            },
            
            "MVC Pattern": {
                "type": "architectural_pattern", 
                "indicators": [
                    r"class\s+\w*Controller",
                    r"class\s+\w*Model",
                    r"class\s+\w*View",
                    r"def\s+render",
                    r"templates?"
                ],
                "files": ["controller", "model", "view", "template"],
                "benefits": ["Separación de responsabilidades", "Reutilización", "Mantenimiento"],
                "description": "Separa la lógica de presentación, negocio y datos"
            },
            
            "Microservices": {
                "type": "architectural_pattern",
                "indicators": [
                    r"FastAPI",
                    r"@router\.",
                    r"ServiceRegistry",
                    r"docker",
                    r"kubernetes",
                    r"service_discovery"
                ],
                "files": ["service", "microservice", "api"],
                "benefits": ["Escalabilidad independiente", "Tecnologías heterogéneas", "Resiliencia"],
                "description": "Arquitectura basada en servicios pequeños e independientes"
            },
            
            "Dependency Injection": {
                "type": "design_pattern",
                "indicators": [
                    r"Depends\s*\(",
                    r"@inject",
                    r"Container",
                    r"dependency.*inject",
                    r"IoC"
                ],
                "files": ["container", "inject", "dependencies"],
                "benefits": ["Bajo acoplamiento", "Testabilidad", "Flexibilidad"],
                "description": "Inyecta dependencias en lugar de crearlas internamente"
            },
            
            "Factory Pattern": {
                "type": "design_pattern",
                "indicators": [
                    r"class\s+\w*Factory",
                    r"def\s+create_\w+",
                    r"def\s+make_\w+",
                    r"@staticmethod.*create"
                ],
                "files": ["factory"],
                "benefits": ["Flexibilidad en creación", "Extensibilidad", "Encapsulación"],
                "description": "Crea objetos sin especificar sus clases exactas"
            },
            
            "Observer Pattern": {
                "type": "design_pattern",
                "indicators": [
                    r"class\s+\w*Observer",
                    r"def\s+notify",
                    r"def\s+subscribe",
                    r"def\s+unsubscribe",
                    r"EventEmitter",
                    r"Signal"
                ],
                "files": ["observer", "event", "signal"],
                "benefits": ["Bajo acoplamiento", "Comunicación dinámica", "Extensibilidad"],
                "description": "Notifica cambios a múltiples objetos dependientes"
            },
            
            "CQRS": {
                "type": "architectural_pattern", 
                "indicators": [
                    r"CommandHandler",
                    r"QueryHandler", 
                    r"class\s+\w*Command",
                    r"class\s+\w*Query",
                    r"execute_command",
                    r"execute_query"
                ],
                "files": ["command", "query", "handler"],
                "benefits": ["Optimización independiente", "Escalabilidad", "Separación de concerns"],
                "description": "Separa operaciones de comando y consulta"
            },
            
            "Multi-Tenant Architecture": {
                "type": "architectural_pattern",
                "indicators": [
                    r"tenant_id",
                    r"multi.*tenant",
                    r"row.*level.*security",
                    r"RLS",
                    r"set_config.*tenant"
                ],
                "files": ["tenant", "multitenant"],
                "benefits": ["Aislamiento de datos", "Eficiencia de recursos", "Mantenimiento centralizado"],
                "description": "Una instancia sirve múltiples inquilinos con aislamiento"
            }
        }
        
        # Base de conocimiento de anti-patrones
        self.anti_patterns = {
            "God Object": {
                "severity": "high",
                "indicators": [
                    lambda file_content: len(file_content.split('\n')) > 1000,
                    lambda file_content: len(re.findall(r'def\s+\w+', file_content)) > 50,
                    lambda file_content: len(re.findall(r'class\s+\w+', file_content)) > 10
                ],
                "description": "Clase o módulo que hace demasiadas cosas",
                "impact": "Difícil mantenimiento, testing complejo, alto acoplamiento",
                "refactoring": "Dividir en clases/módulos más pequeños con responsabilidades específicas"
            },
            
            "Copy-Paste Programming": {
                "severity": "medium",
                "indicators": [
                    lambda file_content: self._detect_code_duplication(file_content)
                ],
                "description": "Código duplicado en múltiples lugares",
                "impact": "Mantenimiento difícil, inconsistencias, bugs propagados",
                "refactoring": "Extraer código común en funciones/clases reutilizables"
            },
            
            "Magic Numbers": {
                "severity": "low",
                "indicators": [
                    lambda file_content: len(re.findall(r'\b(?!0|1)\d{2,}\b', file_content)) > 10
                ],
                "description": "Números literales sin explicación en el código",
                "impact": "Código difícil de entender y mantener",
                "refactoring": "Usar constantes con nombres descriptivos"
            },
            
            "Shotgun Surgery": {
                "severity": "high",
                "indicators": [
                    lambda file_content: self._detect_scattered_functionality(file_content)
                ],
                "description": "Cambios pequeños requieren modificar muchos archivos",
                "impact": "Dificultad para hacer cambios, propenso a errores",
                "refactoring": "Reorganizar código para localizar funcionalidad relacionada"
            },
            
            "Spaghetti Code": {
                "severity": "high",
                "indicators": [
                    lambda file_content: self._detect_complex_control_flow(file_content)
                ],
                "description": "Código con estructura de control compleja y difícil de seguir",
                "impact": "Extremadamente difícil de mantener y debuggear",
                "refactoring": "Refactorizar usando funciones pequeñas y control de flujo claro"
            }
        }
        
        # Plantillas de recomendaciones inteligentes
        self.recommendation_templates = {
            "architecture": [
                {
                    "condition": lambda analysis: not analysis.get("uses_repository_pattern", False),
                    "title": "Implementar Repository Pattern",
                    "category": "architecture",
                    "priority": "medium",
                    "description": "Considera implementar el patrón Repository para abstraer el acceso a datos",
                    "rationale": "Mejora la testabilidad y mantenibilidad del código de acceso a datos"
                }
            ],
            "performance": [
                {
                    "condition": lambda analysis: analysis.get("large_files_count", 0) > 5,
                    "title": "Optimizar archivos grandes",
                    "category": "performance", 
                    "priority": "medium",
                    "description": "Varios archivos grandes detectados que pueden afectar el rendimiento",
                    "rationale": "Archivos grandes pueden impactar tiempos de carga y compilación"
                }
            ],
            "maintainability": [
                {
                    "condition": lambda analysis: analysis.get("code_duplication", 0) > 0.3,
                    "title": "Reducir duplicación de código",
                    "category": "maintainability",
                    "priority": "high", 
                    "description": "Alto nivel de duplicación de código detectado",
                    "rationale": "La duplicación aumenta el costo de mantenimiento y introduce bugs"
                }
            ]
        }
    
    def analyze_patterns(self, database_analysis: Dict[str, Any], 
                        api_analysis: Dict[str, Any],
                        frontend_analysis: Dict[str, Any],
                        security_analysis: Dict[str, Any],
                        project_path: str) -> PatternRecognitionResult:
        """
        Analiza patrones usando los resultados de otros analizadores y el código fuente.
        
        Args:
            database_analysis: Resultado del análisis de base de datos
            api_analysis: Resultado del análisis de API
            frontend_analysis: Resultado del análisis de frontend
            security_analysis: Resultado del análisis de seguridad
            project_path: Ruta al proyecto
            
        Returns:
            Resultado completo del reconocimiento de patrones
        """
        logger.info("Iniciando reconocimiento inteligente de patrones...")
        
        try:
            # Combinar todos los análisis
            combined_analysis = self._combine_analyses(
                database_analysis, api_analysis, frontend_analysis, security_analysis
            )
            
            # Reconocer patrones arquitectónicos
            architectural_patterns = self._recognize_architectural_patterns(
                combined_analysis, project_path
            )
            
            # Detectar anti-patrones
            anti_patterns = self._detect_anti_patterns(project_path)
            
            # Generar recomendaciones inteligentes
            smart_recommendations = self._generate_smart_recommendations(
                combined_analysis, architectural_patterns, anti_patterns
            )
            
            # Detectar problemas de consistencia
            consistency_issues = self._detect_consistency_issues(
                combined_analysis, project_path
            )
            
            # Crear resultado
            self.analysis_result = PatternRecognitionResult(
                architectural_patterns=architectural_patterns,
                anti_patterns=anti_patterns,
                smart_recommendations=smart_recommendations,
                consistency_issues=consistency_issues
            )
            
            # Calcular métricas de calidad
            self._calculate_quality_metrics(combined_analysis)
            
            # Generar análisis predictivo
            self._generate_predictive_analysis(combined_analysis)
            
            logger.info(f"Reconocimiento completado: {len(architectural_patterns)} patrones, "
                       f"{len(smart_recommendations)} recomendaciones")
            
            return self.analysis_result
            
        except Exception as e:
            logger.error(f"Error durante reconocimiento de patrones: {e}")
            raise
    
    def _combine_analyses(self, db_analysis: Dict, api_analysis: Dict,
                         frontend_analysis: Dict, security_analysis: Dict) -> Dict[str, Any]:
        """Combina resultados de todos los análisis"""
        combined = {
            # Base de datos
            "total_models": db_analysis.get("total_models", 0),
            "multi_tenant": db_analysis.get("multi_tenant", False),
            "uses_uuid": db_analysis.get("uses_uuid", False),
            "has_relationships": db_analysis.get("has_relationships", False),
            
            # API
            "total_endpoints": api_analysis.get("total_endpoints", 0),
            "uses_fastapi": "fastapi" in api_analysis.get("framework", "").lower(),
            "uses_openapi": api_analysis.get("uses_openapi", False),
            "auth_type": api_analysis.get("auth_type", ""),
            "crud_endpoints": api_analysis.get("crud_endpoints", 0),
            
            # Frontend
            "frontend_framework": frontend_analysis.get("framework", ""),
            "uses_typescript": frontend_analysis.get("typescript_usage", False),
            "total_components": frontend_analysis.get("total_components", 0),
            "styling_approach": frontend_analysis.get("styling_approach", ""),
            "state_management": frontend_analysis.get("state_management", []),
            
            # Seguridad
            "security_score": security_analysis.get("security_score", 0),
            "uses_jwt": security_analysis.get("uses_jwt", False),
            "uses_rbac": security_analysis.get("uses_rbac", False),
            "uses_rls": security_analysis.get("uses_rls", False),
            
            # Combinados
            "patterns": (db_analysis.get("patterns", []) + 
                        api_analysis.get("patterns", []) +
                        frontend_analysis.get("patterns", []) +
                        security_analysis.get("patterns", [])),
            
            "recommendations": (db_analysis.get("recommendations", []) +
                              api_analysis.get("recommendations", []) +
                              frontend_analysis.get("recommendations", []) +
                              security_analysis.get("recommendations", []))
        }
        
        return combined
    
    def _recognize_architectural_patterns(self, analysis: Dict[str, Any],
                                        project_path: str) -> List[ArchitecturalPattern]:
        """Reconoce patrones arquitectónicos usando IA heurística"""
        patterns = []
        
        # Obtener todos los archivos Python del proyecto
        project_files = self._get_project_files(project_path)
        
        for pattern_name, pattern_info in self.architectural_patterns.items():
            confidence = 0.0
            evidence = []
            matching_files = []
            
            # Verificar indicadores en archivos
            for file_path in project_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_matches = 0
                    for indicator in pattern_info["indicators"]:
                        if re.search(indicator, content, re.IGNORECASE | re.MULTILINE):
                            file_matches += 1
                            evidence.append(f"Indicador '{indicator}' encontrado en {file_path.name}")
                    
                    if file_matches > 0:
                        matching_files.append(str(file_path))
                        confidence += file_matches / len(pattern_info["indicators"]) * 0.1
                        
                except Exception as e:
                    logger.debug(f"Error leyendo {file_path}: {e}")
                    continue
            
            # Verificar nombres de archivos
            for file_path in project_files:
                if any(keyword in file_path.name.lower() for keyword in pattern_info.get("files", [])):
                    confidence += 0.2
                    evidence.append(f"Archivo con nombre indicativo: {file_path.name}")
                    if str(file_path) not in matching_files:
                        matching_files.append(str(file_path))
            
            # Verificar en análisis combinado
            confidence += self._check_pattern_in_analysis(pattern_name, analysis)
            
            # Solo incluir si la confianza es significativa
            if confidence > 0.3:
                architectural_pattern = ArchitecturalPattern(
                    name=pattern_name,
                    type=pattern_info["type"],
                    confidence=min(confidence, 1.0),
                    evidence=evidence[:5],  # Limitar evidencia
                    files=matching_files[:10],  # Limitar archivos
                    description=pattern_info["description"],
                    benefits=pattern_info["benefits"]
                )
                patterns.append(architectural_pattern)
        
        # Ordenar por confianza
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return patterns
    
    def _check_pattern_in_analysis(self, pattern_name: str, analysis: Dict[str, Any]) -> float:
        """Verifica indicios del patrón en el análisis combinado"""
        confidence_boost = 0.0
        
        if pattern_name == "Repository Pattern":
            if analysis.get("crud_endpoints", 0) > 5:
                confidence_boost += 0.3
            if "Repository" in str(analysis.get("patterns", [])):
                confidence_boost += 0.4
        
        elif pattern_name == "Multi-Tenant Architecture":
            if analysis.get("multi_tenant", False):
                confidence_boost += 0.5
            if analysis.get("uses_rls", False):
                confidence_boost += 0.3
        
        elif pattern_name == "Microservices":
            if analysis.get("uses_fastapi", False):
                confidence_boost += 0.2
            if analysis.get("total_endpoints", 0) > 20:
                confidence_boost += 0.2
        
        elif pattern_name == "Dependency Injection":
            if "fastapi" in analysis.get("frontend_framework", "").lower():
                confidence_boost += 0.3  # FastAPI usa DI
        
        elif pattern_name == "MVC Pattern":
            if "react" in analysis.get("frontend_framework", "").lower():
                confidence_boost += 0.2  # React puede seguir MVC-like patterns
        
        return confidence_boost
    
    def _detect_anti_patterns(self, project_path: str) -> List[AntiPattern]:
        """Detecta anti-patrones y code smells"""
        anti_patterns = []
        project_files = self._get_project_files(project_path)
        
        for anti_pattern_name, anti_pattern_info in self.anti_patterns.items():
            occurrences = 0
            affected_files = []
            examples = []
            
            for file_path in project_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Evaluar indicadores (lambdas)
                    file_has_anti_pattern = False
                    for indicator in anti_pattern_info["indicators"]:
                        if callable(indicator):
                            try:
                                if indicator(content):
                                    file_has_anti_pattern = True
                                    break
                            except Exception:
                                continue
                        else:
                            # Indicador de regex
                            if re.search(indicator, content, re.IGNORECASE):
                                file_has_anti_pattern = True
                                break
                    
                    if file_has_anti_pattern:
                        occurrences += 1
                        affected_files.append(str(file_path))
                        
                        # Crear ejemplo (primeras líneas del archivo)
                        lines = content.split('\n')[:5]
                        example = f"{file_path.name}: " + " ".join(lines)[:100] + "..."
                        examples.append(example)
                        
                except Exception as e:
                    logger.debug(f"Error analizando anti-patrón en {file_path}: {e}")
                    continue
            
            if occurrences > 0:
                anti_pattern = AntiPattern(
                    name=anti_pattern_name,
                    severity=anti_pattern_info["severity"],
                    occurrences=occurrences,
                    files=affected_files[:5],  # Limitar archivos mostrados
                    description=anti_pattern_info["description"],
                    impact=anti_pattern_info["impact"],
                    refactoring_suggestion=anti_pattern_info["refactoring"],
                    examples=examples[:3]  # Limitar ejemplos
                )
                anti_patterns.append(anti_pattern)
        
        return anti_patterns
    
    def _generate_smart_recommendations(self, analysis: Dict[str, Any],
                                      patterns: List[ArchitecturalPattern],
                                      anti_patterns: List[AntiPattern]) -> List[SmartRecommendation]:
        """Genera recomendaciones inteligentes basadas en el análisis"""
        recommendations = []
        
        # Recomendaciones basadas en plantillas
        for category, template_list in self.recommendation_templates.items():
            for template in template_list:
                try:
                    if template["condition"](analysis):
                        rec = SmartRecommendation(
                            category=template["category"],
                            priority=template["priority"],
                            title=template["title"],
                            description=template["description"],
                            rationale=template["rationale"],
                            estimated_effort="medium"
                        )
                        recommendations.append(rec)
                except Exception as e:
                    logger.debug(f"Error evaluando plantilla de recomendación: {e}")
        
        # Recomendaciones basadas en patrones faltantes
        pattern_names = [p.name for p in patterns]
        
        if "Repository Pattern" not in pattern_names and analysis.get("total_models", 0) > 3:
            recommendations.append(SmartRecommendation(
                category="architecture",
                priority="medium",
                title="Considerar implementar Repository Pattern",
                description="Con múltiples modelos de datos, el patrón Repository mejorará la arquitectura",
                rationale="Abstrae el acceso a datos y mejora la testabilidad",
                implementation_steps=[
                    "Crear interfaces de repositorio para cada entidad",
                    "Implementar repositorios concretos",
                    "Inyectar repositorios en servicios/controladores",
                    "Agregar tests unitarios para repositorios"
                ],
                estimated_effort="medium"
            ))
        
        if analysis.get("security_score", 0) < 70:
            recommendations.append(SmartRecommendation(
                category="security",
                priority="high",
                title="Mejorar puntuación de seguridad",
                description=f"Puntuación actual: {analysis.get('security_score', 0)}/100",
                rationale="Una mejor seguridad protege contra vulnerabilidades",
                implementation_steps=[
                    "Implementar autenticación JWT si no existe",
                    "Agregar rate limiting",
                    "Configurar CORS apropiadamente",
                    "Implementar logging de auditoría"
                ],
                estimated_effort="high"
            ))
        
        # Recomendaciones basadas en anti-patrones
        for anti_pattern in anti_patterns:
            if anti_pattern.severity in ["high", "critical"]:
                recommendations.append(SmartRecommendation(
                    category="maintainability",
                    priority="high" if anti_pattern.severity == "high" else "critical",
                    title=f"Corregir {anti_pattern.name}",
                    description=f"{anti_pattern.description} - {anti_pattern.occurrences} ocurrencias",
                    rationale=anti_pattern.impact,
                    implementation_steps=[anti_pattern.refactoring_suggestion],
                    related_files=anti_pattern.files,
                    estimated_effort="medium" if anti_pattern.severity == "high" else "high"
                ))
        
        # Recomendaciones de escalabilidad
        if analysis.get("total_endpoints", 0) > 30 and analysis.get("total_components", 0) > 50:
            recommendations.append(SmartRecommendation(
                category="performance",
                priority="medium",
                title="Considerar modularización para escalabilidad",
                description="El proyecto está creciendo, considera dividir en módulos",
                rationale="Facilita el mantenimiento y desarrollo en equipo",
                implementation_steps=[
                    "Identificar bounded contexts",
                    "Crear módulos separados por dominio",
                    "Establecer interfaces claras entre módulos",
                    "Considerar microservicios para el futuro"
                ],
                estimated_effort="high"
            ))
        
        # Ordenar por prioridad
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        recommendations.sort(key=lambda r: priority_order.get(r.priority, 0), reverse=True)
        
        return recommendations
    
    def _detect_consistency_issues(self, analysis: Dict[str, Any],
                                 project_path: str) -> List[ConsistencyIssue]:
        """Detecta problemas de consistencia arquitectónica"""
        issues = []
        
        # Detectar inconsistencias de naming
        naming_issues = self._detect_naming_inconsistencies(project_path)
        issues.extend(naming_issues)
        
        # Detectar inconsistencias de estructura
        structure_issues = self._detect_structure_inconsistencies(analysis)
        issues.extend(structure_issues)
        
        # Detectar inconsistencias de tecnología
        tech_issues = self._detect_technology_inconsistencies(analysis)
        issues.extend(tech_issues)
        
        return issues
    
    def _detect_naming_inconsistencies(self, project_path: str) -> List[ConsistencyIssue]:
        """Detecta inconsistencias en naming conventions"""
        issues = []
        project_files = self._get_project_files(project_path)
        
        # Análisis de nombres de archivos
        file_naming_styles = defaultdict(list)
        for file_path in project_files:
            name = file_path.stem
            if '_' in name:
                file_naming_styles['snake_case'].append(str(file_path))
            elif any(c.isupper() for c in name[1:]):
                file_naming_styles['camelCase'].append(str(file_path))
            else:
                file_naming_styles['lowercase'].append(str(file_path))
        
        # Si hay más de un estilo significativo, es inconsistente
        significant_styles = {style: files for style, files in file_naming_styles.items() if len(files) > 2}
        
        if len(significant_styles) > 1:
            issues.append(ConsistencyIssue(
                type="naming",
                severity="low",
                description="Inconsistencia en convención de nombres de archivos",
                inconsistent_elements=list(significant_styles.keys()),
                suggested_standard="snake_case (recomendado para Python)",
                files_affected=sum(significant_styles.values(), [])[:10]
            ))
        
        return issues
    
    def _detect_structure_inconsistencies(self, analysis: Dict[str, Any]) -> List[ConsistencyIssue]:
        """Detecta inconsistencias en estructura del proyecto"""
        issues = []
        
        # Ejemplo: Frontend y Backend usando diferentes patrones de autenticación
        if (analysis.get("uses_jwt", False) and 
            analysis.get("frontend_framework") and
            "jwt" not in str(analysis.get("state_management", []))):
            
            issues.append(ConsistencyIssue(
                type="structure", 
                severity="medium",
                description="Backend usa JWT pero frontend podría no estar configurado para ello",
                suggested_standard="Configurar gestión de tokens JWT en el frontend",
                inconsistent_elements=["Backend JWT auth", "Frontend auth handling"]
            ))
        
        return issues
    
    def _detect_technology_inconsistencies(self, analysis: Dict[str, Any]) -> List[ConsistencyIssue]:
        """Detecta inconsistencias en elecciones tecnológicas"""
        issues = []
        
        # Ejemplo: TypeScript en frontend pero JavaScript en scripts de backend
        if (analysis.get("uses_typescript", False) and
            analysis.get("frontend_framework") and
            not analysis.get("backend_typescript", False)):
            
            issues.append(ConsistencyIssue(
                type="technology_choice",
                severity="low", 
                description="Frontend usa TypeScript pero backend usa Python/JavaScript",
                suggested_standard="Considerar consistencia en lenguajes tipados",
                inconsistent_elements=["Frontend TypeScript", "Backend Python"]
            ))
        
        return issues
    
    def _calculate_quality_metrics(self, analysis: Dict[str, Any]):
        """Calcula métricas de calidad del código"""
        if not self.analysis_result:
            return
        
        # Puntuación de arquitectura (0-10)
        arch_score = 5.0  # Base
        
        # Bonificaciones por patrones
        arch_score += len(self.analysis_result.architectural_patterns) * 0.5
        
        # Penalizaciones por anti-patrones
        for anti_pattern in self.analysis_result.anti_patterns:
            if anti_pattern.severity == "critical":
                arch_score -= 2.0
            elif anti_pattern.severity == "high":
                arch_score -= 1.0
            elif anti_pattern.severity == "medium":
                arch_score -= 0.5
        
        self.analysis_result.architecture_score = max(0.0, min(10.0, arch_score))
        
        # Puntuación de mantenibilidad
        maint_score = 7.0  # Base más alta
        
        # Factores positivos
        if analysis.get("uses_typescript", False):
            maint_score += 1.0
        if analysis.get("total_models", 0) > 0:
            maint_score += 0.5
        
        # Factores negativos
        duplicated_code_penalty = min(len(self.analysis_result.anti_patterns) * 0.3, 3.0)
        maint_score -= duplicated_code_penalty
        
        self.analysis_result.maintainability_score = max(0.0, min(10.0, maint_score))
        
        # Puntuación de consistencia
        consistency_score = 8.0 - len(self.analysis_result.consistency_issues) * 0.5
        self.analysis_result.consistency_score = max(0.0, min(10.0, consistency_score))
        
        # Puntuación de complejidad (menor = mejor)
        complexity_factors = (
            analysis.get("total_endpoints", 0) * 0.01 +
            analysis.get("total_components", 0) * 0.02 +
            analysis.get("total_models", 0) * 0.05
        )
        self.analysis_result.complexity_score = min(10.0, complexity_factors)
    
    def _generate_predictive_analysis(self, analysis: Dict[str, Any]):
        """Genera análisis predictivo sobre el futuro del proyecto"""
        if not self.analysis_result:
            return
        
        # Identificar áreas de riesgo
        risk_areas = []
        
        if len(self.analysis_result.anti_patterns) > 3:
            risk_areas.append("Calidad del código - múltiples anti-patrones detectados")
        
        if analysis.get("security_score", 100) < 60:
            risk_areas.append("Seguridad - puntuación baja, vulnerable a ataques")
        
        if self.analysis_result.complexity_score > 7:
            risk_areas.append("Complejidad - proyecto volviéndose difícil de mantener")
        
        self.analysis_result.risk_areas = risk_areas
        
        # Recomendaciones de crecimiento
        growth_recs = []
        
        total_size = (analysis.get("total_endpoints", 0) + 
                     analysis.get("total_components", 0) + 
                     analysis.get("total_models", 0))
        
        if total_size > 100:
            growth_recs.append("Considerar arquitectura de microservicios para escalabilidad")
        
        if analysis.get("total_components", 0) > 50:
            growth_recs.append("Implementar lazy loading y code splitting en frontend")
        
        if not any(p.name == "CQRS" for p in self.analysis_result.architectural_patterns):
            if analysis.get("total_endpoints", 0) > 30:
                growth_recs.append("Evaluar CQRS para separar operaciones de lectura y escritura")
        
        self.analysis_result.growth_recommendations = growth_recs
        
        # Evolución tecnológica recomendada
        tech_evolution = []
        
        if not analysis.get("uses_typescript", False):
            tech_evolution.append("Migración gradual a TypeScript para mejor type safety")
        
        if "tailwind" not in analysis.get("styling_approach", ""):
            tech_evolution.append("Considerar adopción de Tailwind CSS para consistency")
        
        if not analysis.get("uses_openapi", False):
            tech_evolution.append("Implementar documentación automática con OpenAPI")
        
        self.analysis_result.technology_evolution = tech_evolution
    
    # Métodos auxiliares para detección de anti-patrones
    
    def _detect_code_duplication(self, content: str) -> bool:
        """Detecta duplicación de código básica"""
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        line_counts = Counter(lines)
        
        # Si más del 20% de las líneas están duplicadas
        total_lines = len(lines)
        duplicated_lines = sum(count - 1 for count in line_counts.values() if count > 1)
        
        return total_lines > 0 and (duplicated_lines / total_lines) > 0.2
    
    def _detect_scattered_functionality(self, content: str) -> bool:
        """Detecta funcionalidad dispersa"""
        # Heurística: muchos imports from diferentes módulos 
        imports = re.findall(r'from\s+(\w+)', content)
        unique_modules = set(imports)
        
        return len(unique_modules) > 15  # Muchas dependencias externas
    
    def _detect_complex_control_flow(self, content: str) -> bool:
        """Detecta flujo de control complejo"""
        # Contar estructuras de control anidadas
        nested_count = 0
        for line in content.split('\n'):
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['if', 'for', 'while', 'try']):
                # Contar nivel de indentación
                indent_level = (len(line) - len(line.lstrip())) // 4
                if indent_level > 3:  # Más de 3 niveles de anidamiento
                    nested_count += 1
        
        return nested_count > 5
    
    def _get_project_files(self, project_path: str) -> List[Path]:
        """Obtiene lista de archivos Python del proyecto"""
        files = []
        
        excluded_dirs = {'__pycache__', '.git', 'node_modules', '.next', 'venv', 'env', 'dist', 'build'}
        excluded_files = {'__init__.py'}
        
        for py_file in Path(project_path).rglob("*.py"):
            # Excluir directorios
            if any(excluded in py_file.parts for excluded in excluded_dirs):
                continue
            
            # Excluir archivos específicos
            if py_file.name in excluded_files:
                continue
            
            files.append(py_file)
        
        return files
    
    def generate_report(self) -> str:
        """Genera reporte completo del reconocimiento de patrones"""
        if not self.analysis_result:
            return "No hay análisis de patrones disponible"
        
        report = []
        report.append("🧠 **Análisis Inteligente de Patrones**")
        report.append("")
        
        # Métricas de calidad
        report.append("📊 **Métricas de Calidad**")
        report.append(f"- Arquitectura: {self.analysis_result.architecture_score:.1f}/10")
        report.append(f"- Mantenibilidad: {self.analysis_result.maintainability_score:.1f}/10") 
        report.append(f"- Consistencia: {self.analysis_result.consistency_score:.1f}/10")
        report.append(f"- Complejidad: {self.analysis_result.complexity_score:.1f}/10")
        report.append("")
        
        # Patrones detectados
        if self.analysis_result.architectural_patterns:
            report.append("🏗️ **Patrones Arquitectónicos Detectados**")
            for pattern in self.analysis_result.architectural_patterns[:5]:
                report.append(f"- {pattern.name} (confianza: {pattern.confidence:.0%})")
                if pattern.description:
                    report.append(f"  {pattern.description}")
            report.append("")
        
        # Recomendaciones top
        if self.analysis_result.smart_recommendations:
            report.append("💡 **Recomendaciones Inteligentes**")
            for rec in self.analysis_result.smart_recommendations[:5]:
                priority_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "💭"}
                emoji = priority_emoji.get(rec.priority, "📋")
                report.append(f"- {emoji} {rec.title}")
                report.append(f"  {rec.description}")
            report.append("")
        
        # Anti-patrones críticos
        critical_anti_patterns = [ap for ap in self.analysis_result.anti_patterns 
                                if ap.severity in ["critical", "high"]]
        if critical_anti_patterns:
            report.append("⚠️ **Anti-patrones Detectados**")
            for anti_pattern in critical_anti_patterns[:3]:
                severity_emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋"}
                emoji = severity_emoji.get(anti_pattern.severity, "📋")
                report.append(f"- {emoji} {anti_pattern.name} ({anti_pattern.occurrences} ocurrencias)")
            report.append("")
        
        # Análisis predictivo
        if self.analysis_result.risk_areas:
            report.append("🔮 **Áreas de Riesgo Futuro**")
            for risk in self.analysis_result.risk_areas:
                report.append(f"- ⚠️ {risk}")
            report.append("")
        
        return "\n".join(report)
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """Retorna resumen del análisis para integración"""
        if not self.analysis_result:
            return {}
        
        return {
            "architecture_score": self.analysis_result.architecture_score,
            "maintainability_score": self.analysis_result.maintainability_score,
            "consistency_score": self.analysis_result.consistency_score,
            "complexity_score": self.analysis_result.complexity_score,
            "patterns_detected": len(self.analysis_result.architectural_patterns),
            "anti_patterns_detected": len(self.analysis_result.anti_patterns),
            "smart_recommendations": len(self.analysis_result.smart_recommendations),
            "consistency_issues": len(self.analysis_result.consistency_issues),
            "risk_areas": self.analysis_result.risk_areas,
            "top_patterns": [
                {
                    "name": p.name,
                    "confidence": p.confidence,
                    "type": p.type
                }
                for p in self.analysis_result.architectural_patterns[:5]
            ],
            "top_recommendations": [
                {
                    "title": r.title,
                    "priority": r.priority,
                    "category": r.category
                }
                for r in self.analysis_result.smart_recommendations[:5]
            ]
        }


if __name__ == "__main__":
    # Ejemplo de uso
    recognizer = PatternRecognizer()
    
    # Datos de ejemplo para testing
    db_analysis = {"total_models": 5, "multi_tenant": True, "uses_uuid": True}
    api_analysis = {"total_endpoints": 25, "uses_openapi": True, "auth_type": "JWT"}
    frontend_analysis = {"framework": "Next.js", "typescript_usage": True, "total_components": 30}
    security_analysis = {"security_score": 75, "uses_jwt": True, "uses_rls": True}
    
    project_path = "/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla"
    
    try:
        result = recognizer.analyze_patterns(
            db_analysis, api_analysis, frontend_analysis, security_analysis, project_path
        )
        print(recognizer.generate_report())
    except Exception as e:
        print(f"Error: {e}")