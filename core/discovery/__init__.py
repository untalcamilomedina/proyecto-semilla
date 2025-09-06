"""
Architecture Discovery Engine - Motor de Descubrimiento de Arquitectura

Este módulo contiene el motor principal para analizar y entender la arquitectura
de proyectos de software, proporcionando insights inteligentes en español.

Componentes principales:
- DiscoveryEngine: Motor principal de análisis
- DatabaseAnalyzer: Análisis de esquemas de base de datos  
- APIPatternDetector: Detección de patrones de API
- FrontendAnalyzer: Análisis de arquitectura frontend
- SecurityMapper: Mapeo de modelos de seguridad
- PatternRecognizer: Reconocimiento de patrones con IA
- I18nManager: Gestión de internacionalización

Autor: Vibecoding Expert System
Versión: 1.0.0
Idioma: Español (con soporte i18n)
"""

from .discovery_engine import DiscoveryEngine, discover_project_architecture
from .i18n_manager import I18nManager
from .analyzers.database_analyzer import DatabaseAnalyzer
from .analyzers.api_pattern_detector import APIPatternDetector
from .analyzers.frontend_analyzer import FrontendAnalyzer
from .analyzers.security_mapper import SecurityMapper
from .analyzers.pattern_recognizer import PatternRecognizer

__all__ = [
    'DiscoveryEngine',
    'discover_project_architecture',
    'I18nManager', 
    'DatabaseAnalyzer',
    'APIPatternDetector',
    'FrontendAnalyzer',
    'SecurityMapper',
    'PatternRecognizer'
]

__version__ = "1.0.0"