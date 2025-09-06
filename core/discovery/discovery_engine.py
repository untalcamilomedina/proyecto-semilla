"""
Discovery Engine - Motor Principal de Descubrimiento de Arquitectura

Orquesta todos los analizadores especializados para proporcionar un análisis
completo e integrado de la arquitectura del proyecto en español.

Este es el componente principal que coordina:
- DatabaseAnalyzer: Análisis de modelos y esquemas
- APIPatternDetector: Detección de patrones de API
- FrontendAnalyzer: Análisis de componentes React
- SecurityMapper: Mapeo de seguridad
- PatternRecognizer: Reconocimiento de patrones con IA
- I18nManager: Gestión de internacionalización

Características:
- Análisis integral y coordinado de toda la arquitectura
- Generación de reportes completos en español
- Recomendaciones contextualizadas e inteligentes
- Detección automática de problemas de integración
- Métricas de calidad unificadas
- Análisis predictivo para escalabilidad futura
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, field
import json

from .i18n_manager import get_i18n, setup_i18n
from .analyzers.database_analyzer import DatabaseAnalyzer
from .analyzers.api_pattern_detector import APIPatternDetector
from .analyzers.frontend_analyzer import FrontendAnalyzer
from .analyzers.security_mapper import SecurityMapper
from .analyzers.pattern_recognizer import PatternRecognizer

logger = logging.getLogger(__name__)


@dataclass
class AnalysisMetrics:
    """Métricas generales del análisis"""
    start_time: float
    end_time: Optional[float] = None
    duration_seconds: Optional[float] = None
    files_analyzed: int = 0
    errors_encountered: int = 0
    warnings_generated: int = 0
    
    # Métricas por componente
    database_models_found: int = 0
    api_endpoints_found: int = 0
    frontend_components_found: int = 0
    security_policies_found: int = 0
    patterns_detected: int = 0
    
    # Métricas de calidad
    overall_architecture_score: float = 0.0
    maintainability_score: float = 0.0
    security_score: float = 0.0
    consistency_score: float = 0.0


@dataclass
class IntegrationInsight:
    """Insight de integración entre componentes"""
    type: str  # consistency, integration, compatibility
    severity: str  # info, warning, error, critical
    title: str
    description: str
    components_involved: List[str] = field(default_factory=list)
    recommendation: str = ""
    impact: str = ""


@dataclass
class DiscoveryResult:
    """Resultado completo del análisis de descubrimiento"""
    # Resultados de analizadores individuales
    database_analysis: Dict[str, Any] = field(default_factory=dict)
    api_analysis: Dict[str, Any] = field(default_factory=dict)
    frontend_analysis: Dict[str, Any] = field(default_factory=dict)
    security_analysis: Dict[str, Any] = field(default_factory=dict)
    pattern_analysis: Dict[str, Any] = field(default_factory=dict)
    
    # Análisis integrado
    integration_insights: List[IntegrationInsight] = field(default_factory=list)
    cross_component_recommendations: List[str] = field(default_factory=list)
    architecture_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Métricas y reportes
    metrics: Optional[AnalysisMetrics] = None
    spanish_report: str = ""
    english_report: str = ""
    json_summary: Dict[str, Any] = field(default_factory=dict)
    
    # Configuración y metadatos
    project_path: str = ""
    discovery_version: str = "1.0.0"
    timestamp: str = ""


class DiscoveryEngine:
    """
    Motor Principal de Descubrimiento de Arquitectura
    
    Coordina todos los analizadores para proporcionar un análisis completo
    e integrado de la arquitectura del proyecto con reportes en español.
    """
    
    def __init__(self, locale: str = "es"):
        """
        Inicializa el motor de descubrimiento.
        
        Args:
            locale: Idioma para reportes ('es' o 'en')
        """
        # Configurar sistema de internacionalización
        self.i18n = setup_i18n(locale)
        self.locale = locale
        
        # Inicializar analizadores especializados
        self.database_analyzer = DatabaseAnalyzer()
        self.api_detector = APIPatternDetector()
        self.frontend_analyzer = FrontendAnalyzer()
        self.security_mapper = SecurityMapper()
        self.pattern_recognizer = PatternRecognizer()
        
        # Estado del análisis
        self.current_analysis: Optional[DiscoveryResult] = None
        self.is_analyzing = False
        
        logger.info("🚀 Architecture Discovery Engine inicializado")
    
    def discover_architecture(self, project_path: str, 
                            include_patterns: bool = True,
                            include_security: bool = True,
                            verbose: bool = False) -> DiscoveryResult:
        """
        Ejecuta el análisis completo de arquitectura del proyecto.
        
        Args:
            project_path: Ruta absoluta al directorio raíz del proyecto
            include_patterns: Si incluir análisis de patrones con IA
            include_security: Si incluir análisis de seguridad
            verbose: Si mostrar información detallada durante el análisis
            
        Returns:
            Resultado completo del análisis de descubrimiento
            
        Raises:
            FileNotFoundError: Si el proyecto no existe
            Exception: Si hay errores durante el análisis
        """
        if self.is_analyzing:
            raise RuntimeError("Ya hay un análisis en progreso")
        
        # Validar proyecto
        project_path = Path(project_path).resolve()
        if not project_path.exists():
            raise FileNotFoundError(f"Proyecto no encontrado: {project_path}")
        
        logger.info(f"🔍 Iniciando descubrimiento de arquitectura: {project_path}")
        
        # Inicializar análisis
        self.is_analyzing = True
        metrics = AnalysisMetrics(start_time=time.time())
        
        result = DiscoveryResult(
            project_path=str(project_path),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        try:
            print(f"\n{self.i18n.t('analysis.starting')}")
            
            # 1. Análisis de Base de Datos
            if verbose:
                print(f"📊 {self.i18n.t('database.analyzing')}")
            
            try:
                db_analysis = self.database_analyzer.analyze_project(str(project_path))
                result.database_analysis = self.database_analyzer.get_analysis_summary()
                metrics.database_models_found = result.database_analysis.get("total_models", 0)
                
                if verbose:
                    print(f"   ✓ {metrics.database_models_found} modelos encontrados")
                    
            except Exception as e:
                logger.error(f"Error en análisis de base de datos: {e}")
                metrics.errors_encountered += 1
                result.database_analysis = {"error": str(e)}
            
            # 2. Análisis de API
            if verbose:
                print(f"🔌 {self.i18n.t('api.analyzing')}")
            
            try:
                api_analysis = self.api_detector.analyze_project(str(project_path))
                result.api_analysis = self.api_detector.get_analysis_summary()
                metrics.api_endpoints_found = result.api_analysis.get("total_endpoints", 0)
                
                if verbose:
                    print(f"   ✓ {metrics.api_endpoints_found} endpoints encontrados")
                    
            except Exception as e:
                logger.error(f"Error en análisis de API: {e}")
                metrics.errors_encountered += 1
                result.api_analysis = {"error": str(e)}
            
            # 3. Análisis de Frontend
            if verbose:
                print(f"🎨 {self.i18n.t('frontend.analyzing')}")
            
            try:
                frontend_analysis = self.frontend_analyzer.analyze_project(str(project_path))
                result.frontend_analysis = self.frontend_analyzer.get_analysis_summary()
                metrics.frontend_components_found = result.frontend_analysis.get("total_components", 0)
                
                if verbose:
                    print(f"   ✓ {metrics.frontend_components_found} componentes encontrados")
                    
            except Exception as e:
                logger.error(f"Error en análisis de frontend: {e}")
                metrics.errors_encountered += 1
                result.frontend_analysis = {"error": str(e)}
            
            # 4. Análisis de Seguridad (opcional)
            if include_security:
                if verbose:
                    print(f"🔒 {self.i18n.t('security.analyzing')}")
                
                try:
                    security_analysis = self.security_mapper.analyze_project(str(project_path))
                    result.security_analysis = self.security_mapper.get_analysis_summary()
                    metrics.security_policies_found = result.security_analysis.get("total_rls_policies", 0)
                    
                    if verbose:
                        print(f"   ✓ Score de seguridad: {result.security_analysis.get('security_score', 0)}/100")
                        
                except Exception as e:
                    logger.error(f"Error en análisis de seguridad: {e}")
                    metrics.errors_encountered += 1
                    result.security_analysis = {"error": str(e)}
            
            # 5. Reconocimiento de Patrones con IA (opcional)
            if include_patterns:
                if verbose:
                    print("🧠 Ejecutando reconocimiento inteligente de patrones...")
                
                try:
                    pattern_analysis = self.pattern_recognizer.analyze_patterns(
                        result.database_analysis,
                        result.api_analysis,
                        result.frontend_analysis,
                        result.security_analysis,
                        str(project_path)
                    )
                    result.pattern_analysis = self.pattern_recognizer.get_analysis_summary()
                    metrics.patterns_detected = result.pattern_analysis.get("patterns_detected", 0)
                    
                    if verbose:
                        print(f"   ✓ {metrics.patterns_detected} patrones detectados")
                        
                except Exception as e:
                    logger.error(f"Error en reconocimiento de patrones: {e}")
                    metrics.errors_encountered += 1
                    result.pattern_analysis = {"error": str(e)}
            
            # 6. Análisis de Integración
            if verbose:
                print("🔗 Analizando integración entre componentes...")
            
            integration_insights = self._analyze_integration(result)
            result.integration_insights = integration_insights
            
            # 7. Generar Recomendaciones Cross-Component
            cross_recommendations = self._generate_cross_component_recommendations(result)
            result.cross_component_recommendations = cross_recommendations
            
            # 8. Crear Resumen de Arquitectura
            architecture_summary = self._create_architecture_summary(result)
            result.architecture_summary = architecture_summary
            
            # 9. Calcular Métricas Finales
            self._calculate_overall_metrics(metrics, result)
            metrics.end_time = time.time()
            metrics.duration_seconds = metrics.end_time - metrics.start_time
            result.metrics = metrics
            
            # 10. Generar Reportes
            if verbose:
                print("📝 Generando reportes...")
            
            result.spanish_report = self._generate_spanish_report(result)
            
            if self.locale != "es":
                result.english_report = self._generate_english_report(result)
            
            result.json_summary = self._generate_json_summary(result)
            
            # Finalizar
            self.current_analysis = result
            
            success_msg = self.i18n.t('analysis.completed')
            print(f"\n✅ {success_msg}")
            print(f"⏱️  Duración: {metrics.duration_seconds:.1f} segundos")
            print(f"📈 Score general: {metrics.overall_architecture_score:.1f}/10")
            
            if metrics.errors_encountered > 0:
                print(f"⚠️  {metrics.errors_encountered} errores encontrados (ver logs)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error crítico durante análisis: {e}")
            metrics.errors_encountered += 1
            raise
            
        finally:
            self.is_analyzing = False
    
    def _analyze_integration(self, result: DiscoveryResult) -> List[IntegrationInsight]:
        """Analiza la integración entre componentes de la arquitectura"""
        insights = []
        
        db_analysis = result.database_analysis
        api_analysis = result.api_analysis
        frontend_analysis = result.frontend_analysis
        security_analysis = result.security_analysis
        
        # Verificar consistencia de autenticación
        backend_uses_jwt = security_analysis.get("uses_jwt", False)
        frontend_framework = frontend_analysis.get("framework", "")
        
        if backend_uses_jwt and frontend_framework:
            insights.append(IntegrationInsight(
                type="integration",
                severity="info",
                title="Autenticación JWT Backend-Frontend",
                description="Backend usa JWT, verificar integración con frontend",
                components_involved=["Backend Auth", "Frontend Auth"],
                recommendation="Configurar interceptores de JWT en el cliente",
                impact="Autenticación consistente en toda la aplicación"
            ))
        
        # Verificar multi-tenancy consistente
        db_multi_tenant = db_analysis.get("multi_tenant", False)
        security_multi_tenant = security_analysis.get("multi_tenant_security", False)
        
        if db_multi_tenant and not security_multi_tenant:
            insights.append(IntegrationInsight(
                type="consistency",
                severity="warning",
                title="Multi-tenancy Inconsistente",
                description="Base de datos configurada para multi-tenancy pero seguridad incompleta",
                components_involved=["Database", "Security"],
                recommendation="Implementar políticas RLS completas para aislamiento de tenants",
                impact="Posible filtración de datos entre tenants"
            ))
        
        # Verificar API y Frontend compatibility
        total_endpoints = api_analysis.get("total_endpoints", 0)
        total_components = frontend_analysis.get("total_components", 0)
        
        if total_endpoints > 20 and total_components < 10:
            insights.append(IntegrationInsight(
                type="compatibility",
                severity="warning",
                title="Desbalance API-Frontend",
                description=f"Muchos endpoints ({total_endpoints}) vs pocos componentes ({total_components})",
                components_involved=["API", "Frontend"],
                recommendation="Verificar que todos los endpoints tengan interfaz de usuario",
                impact="Posible funcionalidad backend no utilizada"
            ))
        
        # Verificar TypeScript consistency
        uses_typescript = frontend_analysis.get("typescript_usage", False)
        if not uses_typescript and total_components > 30:
            insights.append(IntegrationInsight(
                type="consistency",
                severity="info",
                title="TypeScript para Proyectos Grandes",
                description="Proyecto frontend grande sin TypeScript",
                components_involved=["Frontend"],
                recommendation="Considerar migración a TypeScript para mejor mantenibilidad",
                impact="Mejor type safety y developer experience"
            ))
        
        return insights
    
    def _generate_cross_component_recommendations(self, result: DiscoveryResult) -> List[str]:
        """Genera recomendaciones que cruzan múltiples componentes"""
        recommendations = []
        
        db_analysis = result.database_analysis
        api_analysis = result.api_analysis
        frontend_analysis = result.frontend_analysis
        security_analysis = result.security_analysis
        
        # Recomendación de testing integral
        total_complexity = (
            db_analysis.get("total_models", 0) +
            api_analysis.get("total_endpoints", 0) +
            frontend_analysis.get("total_components", 0)
        )
        
        if total_complexity > 50:
            recommendations.append(
                "Implementar testing de integración end-to-end para validar flujos completos"
            )
        
        # Recomendación de monitoreo
        if api_analysis.get("total_endpoints", 0) > 15:
            recommendations.append(
                "Configurar monitoreo y logging distribuido entre backend y frontend"
            )
        
        # Recomendación de documentación
        if not api_analysis.get("uses_openapi", False):
            recommendations.append(
                "Generar documentación API automática con OpenAPI/Swagger para el frontend"
            )
        
        # Recomendación de performance
        if frontend_analysis.get("total_components", 0) > 40:
            recommendations.append(
                "Implementar lazy loading y code splitting para optimizar carga inicial"
            )
        
        # Recomendación de seguridad integral
        security_score = security_analysis.get("security_score", 100)
        if security_score < 80:
            recommendations.append(
                "Implementar security headers, CSP y validación consistente frontend-backend"
            )
        
        return recommendations
    
    def _create_architecture_summary(self, result: DiscoveryResult) -> Dict[str, Any]:
        """Crea un resumen ejecutivo de la arquitectura"""
        db_analysis = result.database_analysis
        api_analysis = result.api_analysis
        frontend_analysis = result.frontend_analysis
        security_analysis = result.security_analysis
        pattern_analysis = result.pattern_analysis
        
        summary = {
            # Clasificación de arquitectura
            "architecture_type": self._classify_architecture_type(result),
            "complexity_level": self._assess_complexity_level(result),
            "maturity_level": self._assess_maturity_level(result),
            
            # Stack tecnológico
            "technology_stack": {
                "backend": "FastAPI + SQLAlchemy" if api_analysis.get("total_endpoints", 0) > 0 else "Unknown",
                "frontend": frontend_analysis.get("framework", "Unknown"),
                "database": "PostgreSQL" if db_analysis.get("total_models", 0) > 0 else "Unknown",
                "styling": frontend_analysis.get("styling_approach", "Unknown"),
                "auth": security_analysis.get("auth_type", "Unknown") if security_analysis.get("uses_jwt") else "None"
            },
            
            # Características principales
            "key_features": [],
            
            # Estadísticas clave
            "key_metrics": {
                "total_models": db_analysis.get("total_models", 0),
                "total_endpoints": api_analysis.get("total_endpoints", 0),
                "total_components": frontend_analysis.get("total_components", 0),
                "security_score": security_analysis.get("security_score", 0),
                "patterns_detected": pattern_analysis.get("patterns_detected", 0)
            },
            
            # Assessment general
            "strengths": [],
            "areas_for_improvement": [],
            "recommended_next_steps": []
        }
        
        # Identificar características clave
        if db_analysis.get("multi_tenant", False):
            summary["key_features"].append("Multi-tenant Architecture")
        
        if security_analysis.get("uses_rls", False):
            summary["key_features"].append("Row-Level Security")
        
        if api_analysis.get("uses_openapi", False):
            summary["key_features"].append("OpenAPI Documentation")
        
        if frontend_analysis.get("typescript_usage", False):
            summary["key_features"].append("TypeScript")
        
        # Identificar fortalezas
        if security_analysis.get("security_score", 0) > 80:
            summary["strengths"].append("Modelo de seguridad robusto")
        
        if pattern_analysis.get("patterns_detected", 0) > 3:
            summary["strengths"].append("Uso consistente de patrones arquitectónicos")
        
        if frontend_analysis.get("typescript_usage", False):
            summary["strengths"].append("Type safety con TypeScript")
        
        # Identificar áreas de mejora
        if security_analysis.get("security_score", 0) < 60:
            summary["areas_for_improvement"].append("Fortalecer modelo de seguridad")
        
        if not api_analysis.get("uses_openapi", False):
            summary["areas_for_improvement"].append("Implementar documentación automática de API")
        
        integration_issues = len(result.integration_insights)
        if integration_issues > 2:
            summary["areas_for_improvement"].append("Resolver inconsistencias de integración")
        
        return summary
    
    def _classify_architecture_type(self, result: DiscoveryResult) -> str:
        """Clasifica el tipo de arquitectura"""
        api_endpoints = result.api_analysis.get("total_endpoints", 0)
        frontend_components = result.frontend_analysis.get("total_components", 0)
        
        if api_endpoints > 30 and frontend_components > 40:
            return "Full-Stack Enterprise"
        elif api_endpoints > 15 or frontend_components > 20:
            return "Full-Stack Standard"
        elif api_endpoints > 0 and frontend_components > 0:
            return "Full-Stack Básico"
        elif api_endpoints > 0:
            return "Backend API"
        elif frontend_components > 0:
            return "Frontend Application"
        else:
            return "Unknown"
    
    def _assess_complexity_level(self, result: DiscoveryResult) -> str:
        """Evalúa el nivel de complejidad del proyecto"""
        total_complexity = (
            result.database_analysis.get("total_models", 0) +
            result.api_analysis.get("total_endpoints", 0) +
            result.frontend_analysis.get("total_components", 0)
        )
        
        if total_complexity > 100:
            return "Alta"
        elif total_complexity > 50:
            return "Media"
        elif total_complexity > 20:
            return "Baja"
        else:
            return "Muy Baja"
    
    def _assess_maturity_level(self, result: DiscoveryResult) -> str:
        """Evalúa el nivel de madurez del proyecto"""
        maturity_score = 0
        
        # Factores de madurez
        if result.security_analysis.get("uses_jwt", False):
            maturity_score += 1
        if result.api_analysis.get("uses_openapi", False):
            maturity_score += 1
        if result.frontend_analysis.get("typescript_usage", False):
            maturity_score += 1
        if result.security_analysis.get("uses_rls", False):
            maturity_score += 1
        if result.pattern_analysis.get("patterns_detected", 0) > 3:
            maturity_score += 1
        if result.security_analysis.get("security_score", 0) > 70:
            maturity_score += 1
        
        if maturity_score >= 5:
            return "Madura"
        elif maturity_score >= 3:
            return "Intermedia"
        elif maturity_score >= 1:
            return "Básica"
        else:
            return "Inicial"
    
    def _calculate_overall_metrics(self, metrics: AnalysisMetrics, result: DiscoveryResult):
        """Calcula métricas generales del análisis"""
        # Score de arquitectura general (promedio ponderado)
        scores = []
        weights = []
        
        # Database score (peso 20%)
        if "error" not in result.database_analysis:
            db_score = min(result.database_analysis.get("total_models", 0) * 2, 10)
            scores.append(db_score)
            weights.append(0.2)
        
        # API score (peso 25%)
        if "error" not in result.api_analysis:
            api_score = min(result.api_analysis.get("total_endpoints", 0) * 0.3, 10)
            if result.api_analysis.get("uses_openapi", False):
                api_score += 2
            scores.append(min(api_score, 10))
            weights.append(0.25)
        
        # Frontend score (peso 25%)
        if "error" not in result.frontend_analysis:
            frontend_score = min(result.frontend_analysis.get("total_components", 0) * 0.2, 8)
            if result.frontend_analysis.get("typescript_usage", False):
                frontend_score += 2
            scores.append(min(frontend_score, 10))
            weights.append(0.25)
        
        # Security score (peso 30%)
        security_score = result.security_analysis.get("security_score", 0) / 10
        if "error" not in result.security_analysis:
            scores.append(security_score)
            weights.append(0.3)
        
        # Calcular promedio ponderado
        if scores and weights:
            metrics.overall_architecture_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)
        
        # Otras métricas
        metrics.maintainability_score = result.pattern_analysis.get("maintainability_score", 5.0)
        metrics.security_score = security_score
        metrics.consistency_score = result.pattern_analysis.get("consistency_score", 5.0)
    
    def _generate_spanish_report(self, result: DiscoveryResult) -> str:
        """Genera reporte completo en español"""
        report_lines = []
        
        # Header
        report_lines.append("🏗️ **Análisis de Arquitectura - Proyecto Semilla**")
        report_lines.append("=" * 55)
        report_lines.append("")
        report_lines.append(f"📅 Fecha: {result.timestamp}")
        report_lines.append(f"📁 Proyecto: {result.project_path}")
        report_lines.append(f"⏱️  Duración: {result.metrics.duration_seconds:.1f} segundos")
        report_lines.append("")
        
        # Resumen Ejecutivo
        summary = result.architecture_summary
        report_lines.append("## 📋 Resumen Ejecutivo")
        report_lines.append("")
        report_lines.append(f"**Tipo de Arquitectura:** {summary.get('architecture_type', 'Unknown')}")
        report_lines.append(f"**Nivel de Complejidad:** {summary.get('complexity_level', 'Unknown')}")
        report_lines.append(f"**Nivel de Madurez:** {summary.get('maturity_level', 'Unknown')}")
        report_lines.append(f"**Score General:** {result.metrics.overall_architecture_score:.1f}/10")
        report_lines.append("")
        
        # Stack Tecnológico
        tech_stack = summary.get("technology_stack", {})
        report_lines.append("## 💻 Stack Tecnológico")
        report_lines.append("")
        for component, technology in tech_stack.items():
            report_lines.append(f"- **{component.title()}:** {technology}")
        report_lines.append("")
        
        # Análisis por Capas
        report_lines.append("## 🏛️ Análisis por Capas")
        report_lines.append("")
        
        # Base de Datos
        if "error" not in result.database_analysis:
            report_lines.append("### 📊 **Capa de Base de Datos**")
            
            if result.database_analysis.get("multi_tenant", False):
                report_lines.append("- ✅ Arquitectura multi-tenant con RLS")
            
            if result.database_analysis.get("uses_uuid", False):
                report_lines.append("- ✅ Patrón UUID para claves primarias")
            
            models_count = result.database_analysis.get("total_models", 0)
            report_lines.append(f"- 📈 {models_count} entidades principales detectadas")
            
            if result.database_analysis.get("has_relationships", False):
                report_lines.append("- 🔗 Relaciones: One-to-many, many-to-many consistentes")
            
            report_lines.append("")
        
        # API
        if "error" not in result.api_analysis:
            report_lines.append("### 🔌 **Capa de API**")
            
            if result.api_analysis.get("uses_openapi", False):
                report_lines.append("- ✅ FastAPI con generación automática OpenAPI")
            
            auth_type = result.api_analysis.get("auth_type", "")
            if auth_type:
                report_lines.append(f"- 🔐 Autenticación {auth_type} con permisos basados en roles")
            
            endpoints_count = result.api_analysis.get("total_endpoints", 0)
            if endpoints_count > 0:
                report_lines.append(f"- 📊 {endpoints_count} endpoints RESTful")
            
            api_version = result.api_analysis.get("api_version", "")
            if api_version:
                report_lines.append(f"- 🏷️  Versionado API: {api_version}")
            
            report_lines.append("")
        
        # Frontend
        if "error" not in result.frontend_analysis:
            report_lines.append("### 🎨 **Capa Frontend**")
            
            framework = result.frontend_analysis.get("framework", "")
            if framework:
                typescript_suffix = " con TypeScript" if result.frontend_analysis.get("typescript_usage") else ""
                report_lines.append(f"- ⚛️ {framework}{typescript_suffix}")
            
            report_lines.append("- 🧱 Arquitectura basada en componentes")
            
            styling = result.frontend_analysis.get("styling_approach", "")
            if styling:
                styling_map = {
                    "tailwind": "Tailwind CSS para estilos",
                    "css-modules": "CSS Modules para estilos", 
                    "styled-components": "Styled Components para estilos",
                    "css": "CSS tradicional para estilos"
                }
                report_lines.append(f"- 🎨 {styling_map.get(styling, styling)}")
            
            state_mgmt = result.frontend_analysis.get("state_management", [])
            if state_mgmt:
                mgmt_text = " y ".join(state_mgmt)
                report_lines.append(f"- 🔄 Gestión de estado con {mgmt_text}")
            else:
                report_lines.append("- 🔄 Gestión de estado con Context API")
            
            components_count = result.frontend_analysis.get("total_components", 0)
            pages_count = result.frontend_analysis.get("total_pages", 0)
            report_lines.append(f"- 📊 {pages_count} páginas, {components_count} componentes")
            
            report_lines.append("")
        
        # Seguridad
        if "error" not in result.security_analysis:
            report_lines.append("### 🔒 **Modelo de Seguridad**")
            
            if result.security_analysis.get("uses_rls", False):
                report_lines.append("- 🛡️  Row-Level Security (RLS) para aislamiento de tenants")
            
            if result.security_analysis.get("uses_jwt", False):
                if result.security_analysis.get("uses_refresh_tokens", False):
                    report_lines.append("- 🎫 Tokens JWT con mecanismo de refresh")
                else:
                    report_lines.append("- 🎫 Autenticación con tokens JWT")
            
            if result.security_analysis.get("uses_rbac", False):
                report_lines.append("- 👥 Control de acceso basado en roles (RBAC)")
            
            if result.security_analysis.get("uses_cors", False):
                report_lines.append("- 🌐 Configuración CORS para frontend")
            
            security_score = result.security_analysis.get("security_score", 0)
            roles_count = result.security_analysis.get("total_roles", 0)
            policies_count = result.security_analysis.get("total_rls_policies", 0)
            
            if roles_count > 0:
                report_lines.append(f"- 📊 {roles_count} roles definidos")
            if policies_count > 0:
                report_lines.append(f"- 📋 {policies_count} políticas de seguridad")
            
            report_lines.append(f"- 🏆 Score de seguridad: {security_score}/100")
            report_lines.append("")
        
        # Patrones Detectados
        if "error" not in result.pattern_analysis:
            patterns_count = result.pattern_analysis.get("patterns_detected", 0)
            if patterns_count > 0:
                report_lines.append("### 🧠 **Patrones Arquitectónicos Detectados**")
                
                top_patterns = result.pattern_analysis.get("top_patterns", [])
                for pattern in top_patterns[:5]:
                    confidence = pattern.get("confidence", 0) * 100
                    pattern_name = pattern.get("name", "Unknown")
                    report_lines.append(f"- 🎯 {pattern_name} (confianza: {confidence:.0f}%)")
                
                report_lines.append("")
        
        # Insights de Integración
        if result.integration_insights:
            report_lines.append("### 🔗 **Insights de Integración**")
            
            for insight in result.integration_insights[:5]:
                severity_emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "critical": "🚨"}
                emoji = severity_emoji.get(insight.severity, "ℹ️")
                
                report_lines.append(f"- {emoji} **{insight.title}**")
                report_lines.append(f"  {insight.description}")
                if insight.recommendation:
                    report_lines.append(f"  💡 *{insight.recommendation}*")
            
            report_lines.append("")
        
        # Recomendaciones Principales
        all_recommendations = result.cross_component_recommendations
        
        if result.pattern_analysis and "top_recommendations" in result.pattern_analysis:
            pattern_recs = result.pattern_analysis["top_recommendations"]
            for rec in pattern_recs[:3]:
                all_recommendations.append(rec.get("title", ""))
        
        if all_recommendations:
            report_lines.append("## 💡 **Recomendaciones para nuevos módulos**")
            
            unique_recs = list(dict.fromkeys(all_recommendations))[:8]  # Eliminar duplicados
            
            for rec in unique_recs:
                if rec:  # No mostrar recomendaciones vacías
                    report_lines.append(f"- {rec}")
            
            report_lines.append("")
        
        # Métricas de Calidad
        report_lines.append("## 📊 **Métricas de Calidad**")
        report_lines.append("")
        report_lines.append(f"- **Arquitectura General:** {result.metrics.overall_architecture_score:.1f}/10")
        report_lines.append(f"- **Mantenibilidad:** {result.metrics.maintainability_score:.1f}/10")
        report_lines.append(f"- **Seguridad:** {result.metrics.security_score:.1f}/10")
        report_lines.append(f"- **Consistencia:** {result.metrics.consistency_score:.1f}/10")
        report_lines.append("")
        
        # Estadísticas del Análisis
        report_lines.append("## 🔍 **Estadísticas del Análisis**")
        report_lines.append("")
        report_lines.append(f"- **Modelos analizados:** {result.metrics.database_models_found}")
        report_lines.append(f"- **Endpoints encontrados:** {result.metrics.api_endpoints_found}")
        report_lines.append(f"- **Componentes detectados:** {result.metrics.frontend_components_found}")
        report_lines.append(f"- **Políticas de seguridad:** {result.metrics.security_policies_found}")
        report_lines.append(f"- **Patrones identificados:** {result.metrics.patterns_detected}")
        
        if result.metrics.errors_encountered > 0:
            report_lines.append(f"- **Errores encontrados:** {result.metrics.errors_encountered}")
        
        report_lines.append("")
        
        # Footer
        report_lines.append("---")
        report_lines.append("🤖 *Generado por Architecture Discovery Engine v1.0.0*")
        report_lines.append("🧠 *Vibecoding Expert System - Análisis Inteligente de Arquitectura en Español*")
        
        return "\n".join(report_lines)
    
    def _generate_english_report(self, result: DiscoveryResult) -> str:
        """Genera reporte en inglés (versión simplificada)"""
        # Cambiar temporalmente el idioma
        original_locale = self.i18n.current_locale
        self.i18n.set_locale("en")
        
        try:
            report_lines = []
            
            report_lines.append("🏗️ **Architecture Analysis - Proyecto Semilla**")
            report_lines.append("=" * 50)
            report_lines.append("")
            report_lines.append(f"📅 Date: {result.timestamp}")
            report_lines.append(f"📁 Project: {result.project_path}")
            report_lines.append(f"⏱️  Duration: {result.metrics.duration_seconds:.1f} seconds")
            report_lines.append("")
            
            # Executive Summary
            summary = result.architecture_summary
            report_lines.append("## 📋 Executive Summary")
            report_lines.append("")
            report_lines.append(f"**Architecture Type:** {summary.get('architecture_type', 'Unknown')}")
            report_lines.append(f"**Complexity Level:** {summary.get('complexity_level', 'Unknown')}")
            report_lines.append(f"**Maturity Level:** {summary.get('maturity_level', 'Unknown')}")
            report_lines.append(f"**Overall Score:** {result.metrics.overall_architecture_score:.1f}/10")
            report_lines.append("")
            
            # Technology Stack
            tech_stack = summary.get("technology_stack", {})
            report_lines.append("## 💻 Technology Stack")
            report_lines.append("")
            for component, technology in tech_stack.items():
                report_lines.append(f"- **{component.title()}:** {technology}")
            report_lines.append("")
            
            # Key Metrics
            report_lines.append("## 📊 Key Metrics")
            report_lines.append("")
            metrics = summary.get("key_metrics", {})
            report_lines.append(f"- **Database Models:** {metrics.get('total_models', 0)}")
            report_lines.append(f"- **API Endpoints:** {metrics.get('total_endpoints', 0)}")
            report_lines.append(f"- **Frontend Components:** {metrics.get('total_components', 0)}")
            report_lines.append(f"- **Security Score:** {metrics.get('security_score', 0)}/100")
            report_lines.append(f"- **Patterns Detected:** {metrics.get('patterns_detected', 0)}")
            report_lines.append("")
            
            # Recommendations
            if result.cross_component_recommendations:
                report_lines.append("## 💡 Key Recommendations")
                report_lines.append("")
                for rec in result.cross_component_recommendations[:5]:
                    report_lines.append(f"- {rec}")
                report_lines.append("")
            
            # Footer
            report_lines.append("---")
            report_lines.append("🤖 *Generated by Architecture Discovery Engine v1.0.0*")
            
            return "\n".join(report_lines)
            
        finally:
            # Restaurar idioma original
            self.i18n.set_locale(original_locale)
    
    def _generate_json_summary(self, result: DiscoveryResult) -> Dict[str, Any]:
        """Genera resumen en formato JSON para integración con otros sistemas"""
        return {
            "metadata": {
                "project_path": result.project_path,
                "timestamp": result.timestamp,
                "discovery_version": result.discovery_version,
                "duration_seconds": result.metrics.duration_seconds,
                "locale": self.locale
            },
            "architecture_summary": result.architecture_summary,
            "component_analysis": {
                "database": result.database_analysis,
                "api": result.api_analysis,
                "frontend": result.frontend_analysis,
                "security": result.security_analysis,
                "patterns": result.pattern_analysis
            },
            "integration": {
                "insights": [
                    {
                        "type": insight.type,
                        "severity": insight.severity,
                        "title": insight.title,
                        "description": insight.description
                    }
                    for insight in result.integration_insights
                ],
                "cross_recommendations": result.cross_component_recommendations
            },
            "metrics": {
                "overall_architecture_score": result.metrics.overall_architecture_score,
                "maintainability_score": result.metrics.maintainability_score,
                "security_score": result.metrics.security_score,
                "consistency_score": result.metrics.consistency_score,
                "files_analyzed": result.metrics.files_analyzed,
                "errors_encountered": result.metrics.errors_encountered
            }
        }
    
    def save_results(self, output_path: str, formats: List[str] = None) -> Dict[str, str]:
        """
        Guarda los resultados del análisis en diferentes formatos.
        
        Args:
            output_path: Directorio donde guardar los archivos
            formats: Lista de formatos ('json', 'md', 'txt'). Por defecto todos.
            
        Returns:
            Diccionario con rutas de archivos generados
            
        Raises:
            RuntimeError: Si no hay análisis previo
        """
        if not self.current_analysis:
            raise RuntimeError("No hay análisis para guardar. Ejecute discover_architecture() primero.")
        
        if formats is None:
            formats = ['json', 'md', 'txt']
        
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # JSON Summary
        if 'json' in formats:
            json_path = output_path / "architecture_analysis.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_analysis.json_summary, f, indent=2, ensure_ascii=False)
            generated_files['json'] = str(json_path)
        
        # Markdown Report
        if 'md' in formats:
            md_path = output_path / "architecture_report.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(self.current_analysis.spanish_report)
            generated_files['md'] = str(md_path)
            
            # English report if available
            if self.current_analysis.english_report:
                md_en_path = output_path / "architecture_report_en.md"
                with open(md_en_path, 'w', encoding='utf-8') as f:
                    f.write(self.current_analysis.english_report)
                generated_files['md_en'] = str(md_en_path)
        
        # Text Report
        if 'txt' in formats:
            txt_path = output_path / "architecture_summary.txt"
            # Convertir markdown a texto plano básico
            plain_text = self.current_analysis.spanish_report.replace('**', '').replace('##', '').replace('#', '')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(plain_text)
            generated_files['txt'] = str(txt_path)
        
        logger.info(f"Resultados guardados en: {output_path}")
        return generated_files
    
    def get_current_analysis(self) -> Optional[DiscoveryResult]:
        """Retorna el análisis actual si existe"""
        return self.current_analysis
    
    def clear_analysis(self):
        """Limpia el análisis actual"""
        self.current_analysis = None
        logger.info("Análisis actual limpiado")


# Función de conveniencia para uso rápido
def discover_project_architecture(project_path: str, 
                                locale: str = "es",
                                verbose: bool = True,
                                save_to: Optional[str] = None) -> DiscoveryResult:
    """
    Función de conveniencia para analizar rápidamente la arquitectura de un proyecto.
    
    Args:
        project_path: Ruta al proyecto
        locale: Idioma para reportes ('es' o 'en')
        verbose: Si mostrar progreso detallado
        save_to: Directorio donde guardar resultados (opcional)
        
    Returns:
        Resultado completo del análisis
    """
    engine = DiscoveryEngine(locale=locale)
    
    result = engine.discover_architecture(
        project_path=project_path,
        verbose=verbose
    )
    
    if save_to:
        engine.save_results(save_to)
        print(f"📁 Resultados guardados en: {save_to}")
    
    return result


if __name__ == "__main__":
    # Ejemplo de uso
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/Users/untalcamilomedina/Documents/GitHub/proyecto-semilla"
    
    print("🚀 Iniciando Architecture Discovery Engine...")
    print(f"📁 Analizando: {project_path}")
    
    try:
        result = discover_project_architecture(
            project_path=project_path,
            locale="es",
            verbose=True,
            save_to="./discovery_results"
        )
        
        print("\n" + "="*60)
        print("📋 REPORTE COMPLETO")
        print("="*60)
        print(result.spanish_report)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)