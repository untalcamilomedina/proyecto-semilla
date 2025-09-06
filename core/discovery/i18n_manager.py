"""
I18n Manager - Gestor de Internacionalización

Maneja la internacionalización del Architecture Discovery Engine con soporte
para español (primario) e inglés (secundario).

Características:
- Carga automática de archivos de localización JSON
- Interpolación de variables en mensajes
- Fallback automático de español a inglés
- Detección automática de idioma del sistema
- Cache de traducciones para rendimiento
"""

import json
import os
import locale
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class I18nManager:
    """Gestor de internacionalización para el Discovery Engine"""
    
    def __init__(self, default_locale: str = "es"):
        """
        Inicializa el gestor de i18n.
        
        Args:
            default_locale: Idioma por defecto ('es' o 'en')
        """
        self.default_locale = default_locale
        self.current_locale = default_locale
        self.translations: Dict[str, Dict] = {}
        self.locales_dir = Path(__file__).parent / "locales"
        
        # Cargar traducciones disponibles
        self._load_translations()
        
        # Detectar idioma del sistema si es posible
        self._detect_system_locale()
    
    def _load_translations(self) -> None:
        """Carga todas las traducciones desde archivos JSON"""
        try:
            for locale_file in self.locales_dir.glob("*.json"):
                locale_code = locale_file.stem
                
                with open(locale_file, 'r', encoding='utf-8') as f:
                    self.translations[locale_code] = json.load(f)
                    
                logger.debug(f"Cargadas traducciones para idioma: {locale_code}")
                    
        except Exception as e:
            logger.error(f"Error cargando traducciones: {e}")
            # Fallback básico en caso de error
            self.translations = {"es": {}, "en": {}}
    
    def _detect_system_locale(self) -> None:
        """Detecta automáticamente el idioma del sistema"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                if system_locale.startswith('es'):
                    self.current_locale = "es"
                elif system_locale.startswith('en'):
                    self.current_locale = "en"
                else:
                    self.current_locale = self.default_locale
            
            logger.debug(f"Idioma detectado del sistema: {self.current_locale}")
                    
        except Exception as e:
            logger.warning(f"No se pudo detectar idioma del sistema: {e}")
            self.current_locale = self.default_locale
    
    def set_locale(self, locale_code: str) -> bool:
        """
        Establece el idioma actual.
        
        Args:
            locale_code: Código de idioma ('es' o 'en')
            
        Returns:
            True si el idioma fue establecido correctamente
        """
        if locale_code in self.translations:
            self.current_locale = locale_code
            logger.info(f"Idioma cambiado a: {locale_code}")
            return True
        else:
            logger.warning(f"Idioma no disponible: {locale_code}")
            return False
    
    def get_available_locales(self) -> list:
        """Retorna lista de idiomas disponibles"""
        return list(self.translations.keys())
    
    def t(self, key: str, **kwargs) -> str:
        """
        Traduce una clave con interpolación de variables.
        
        Args:
            key: Clave de traducción en formato 'categoria.subclave'
            **kwargs: Variables para interpolar en el mensaje
            
        Returns:
            Mensaje traducido con variables interpoladas
            
        Examples:
            >>> i18n = I18nManager()
            >>> i18n.t('database.entities', count=5)
            '5 entidades principales detectadas'
        """
        return self._get_translation(key, self.current_locale, **kwargs)
    
    def _get_translation(self, key: str, locale_code: str, **kwargs) -> str:
        """
        Obtiene la traducción para una clave específica.
        
        Args:
            key: Clave de traducción
            locale_code: Código de idioma
            **kwargs: Variables para interpolación
            
        Returns:
            Mensaje traducido
        """
        try:
            # Navegar por la estructura anidada de traducciones
            keys = key.split('.')
            current = self.translations[locale_code]
            
            for k in keys:
                current = current[k]
            
            # Interpolar variables si están presentes
            if kwargs and isinstance(current, str):
                return current.format(**kwargs)
            
            return str(current)
            
        except (KeyError, TypeError):
            # Fallback al idioma por defecto
            if locale_code != self.default_locale:
                logger.warning(f"Traducción no encontrada para '{key}' en {locale_code}, usando fallback")
                return self._get_translation(key, self.default_locale, **kwargs)
            
            # Fallback final: retornar la clave
            logger.error(f"Traducción no encontrada para '{key}' en ningún idioma")
            return f"[{key}]"
    
    def get_locale_info(self) -> Dict[str, Any]:
        """
        Retorna información sobre la configuración de idioma actual.
        
        Returns:
            Diccionario con información de configuración
        """
        return {
            "current_locale": self.current_locale,
            "default_locale": self.default_locale,
            "available_locales": self.get_available_locales(),
            "translations_loaded": len(self.translations),
            "system_locale": locale.getdefaultlocale()[0] if locale.getdefaultlocale()[0] else "unknown"
        }
    
    def validate_translations(self) -> Dict[str, Any]:
        """
        Valida que todas las claves de traducción estén presentes en todos los idiomas.
        
        Returns:
            Reporte de validación
        """
        if not self.translations:
            return {"valid": False, "errors": ["No hay traducciones cargadas"]}
        
        errors = []
        warnings = []
        
        # Obtener todas las claves del idioma por defecto
        default_keys = self._get_all_keys(self.translations[self.default_locale])
        
        # Validar cada idioma
        for locale_code, translations in self.translations.items():
            if locale_code == self.default_locale:
                continue
                
            locale_keys = self._get_all_keys(translations)
            
            # Claves faltantes
            missing_keys = default_keys - locale_keys
            if missing_keys:
                errors.append(f"Claves faltantes en {locale_code}: {missing_keys}")
            
            # Claves extra
            extra_keys = locale_keys - default_keys
            if extra_keys:
                warnings.append(f"Claves extra en {locale_code}: {extra_keys}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_keys": len(default_keys),
            "locales_checked": len(self.translations)
        }
    
    def _get_all_keys(self, obj: Dict, prefix: str = "") -> set:
        """Obtiene todas las claves anidadas de un diccionario"""
        keys = set()
        
        for key, value in obj.items():
            full_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                keys.update(self._get_all_keys(value, full_key))
            else:
                keys.add(full_key)
        
        return keys


# Instancia global para uso en todo el módulo
_i18n_instance: Optional[I18nManager] = None


def get_i18n() -> I18nManager:
    """
    Retorna la instancia global del gestor i18n.
    
    Returns:
        Instancia del I18nManager
    """
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nManager()
    return _i18n_instance


def t(key: str, **kwargs) -> str:
    """
    Función de conveniencia para traducir mensajes.
    
    Args:
        key: Clave de traducción
        **kwargs: Variables para interpolación
        
    Returns:
        Mensaje traducido
    """
    return get_i18n().t(key, **kwargs)


# Función para configurar i18n al inicio de la aplicación
def setup_i18n(locale: str = "es") -> I18nManager:
    """
    Configura e inicializa el sistema i18n.
    
    Args:
        locale: Idioma por defecto
        
    Returns:
        Instancia configurada del I18nManager
    """
    global _i18n_instance
    _i18n_instance = I18nManager(locale)
    return _i18n_instance


if __name__ == "__main__":
    # Ejemplo de uso y pruebas
    i18n = I18nManager()
    
    print("=== Prueba del Sistema I18n ===")
    print(f"Idiomas disponibles: {i18n.get_available_locales()}")
    print(f"Idioma actual: {i18n.current_locale}")
    
    print("\n=== Pruebas de Traducción ===")
    print(i18n.t('analysis.starting'))
    print(i18n.t('database.entities', count=5))
    print(i18n.t('api.routes', count=12))
    
    print("\n=== Cambio de Idioma ===")
    i18n.set_locale('en')
    print(i18n.t('analysis.starting'))
    print(i18n.t('database.entities', count=5))
    
    print("\n=== Validación de Traducciones ===")
    validation = i18n.validate_translations()
    print(f"Válido: {validation['valid']}")
    if validation['errors']:
        print(f"Errores: {validation['errors']}")
    if validation['warnings']:
        print(f"Advertencias: {validation['warnings']}")