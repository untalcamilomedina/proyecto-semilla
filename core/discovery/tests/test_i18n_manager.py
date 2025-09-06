"""
Test I18n Manager - Pruebas del Gestor de Internacionalización

Pruebas comprehensivas para el sistema de internacionalización
que maneja español e inglés en el Discovery Engine.
"""

import pytest
import os
import tempfile
from pathlib import Path
import json

from ..i18n_manager import I18nManager, get_i18n, setup_i18n, t


class TestI18nManager:
    """Pruebas del gestor de internacionalización"""
    
    def test_initialization_default_spanish(self):
        """Test inicialización por defecto en español"""
        i18n = I18nManager()
        assert i18n.default_locale == "es"
        assert i18n.current_locale == "es"
        assert len(i18n.translations) > 0
    
    def test_initialization_custom_locale(self):
        """Test inicialización con idioma personalizado"""
        i18n = I18nManager(default_locale="en")
        assert i18n.default_locale == "en"
        assert i18n.current_locale == "en"
    
    def test_set_locale_valid(self):
        """Test cambio de idioma válido"""
        i18n = I18nManager()
        result = i18n.set_locale("en")
        assert result is True
        assert i18n.current_locale == "en"
    
    def test_set_locale_invalid(self):
        """Test cambio de idioma inválido"""
        i18n = I18nManager()
        result = i18n.set_locale("fr")
        assert result is False
        assert i18n.current_locale == "es"  # Mantiene el anterior
    
    def test_get_available_locales(self):
        """Test obtener idiomas disponibles"""
        i18n = I18nManager()
        locales = i18n.get_available_locales()
        assert "es" in locales
        assert "en" in locales
        assert isinstance(locales, list)
    
    def test_translation_basic(self):
        """Test traducción básica"""
        i18n = I18nManager()
        
        # Test español
        i18n.set_locale("es")
        result = i18n.t("analysis.starting")
        assert isinstance(result, str)
        assert "Analizando" in result or "análisis" in result.lower()
        
        # Test inglés
        i18n.set_locale("en")
        result = i18n.t("analysis.starting")
        assert isinstance(result, str)
        assert "Analyzing" in result or "analysis" in result.lower()
    
    def test_translation_with_interpolation(self):
        """Test traducción con interpolación de variables"""
        i18n = I18nManager()
        i18n.set_locale("es")
        
        result = i18n.t("database.entities", count=5)
        assert "5" in result
        assert isinstance(result, str)
        
        result = i18n.t("api.routes", count=12)
        assert "12" in result
    
    def test_translation_fallback(self):
        """Test fallback cuando no existe traducción"""
        i18n = I18nManager()
        i18n.set_locale("es")
        
        # Clave inexistente debería hacer fallback
        result = i18n.t("nonexistent.key")
        assert "[nonexistent.key]" in result
    
    def test_translation_nested_keys(self):
        """Test traducción con claves anidadas"""
        i18n = I18nManager()
        i18n.set_locale("es")
        
        result = i18n.t("database.title")
        assert isinstance(result, str)
        assert len(result) > 0
        
        result = i18n.t("recommendations.user_tenant_role")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_locale_info(self):
        """Test información de configuración de idioma"""
        i18n = I18nManager()
        info = i18n.get_locale_info()
        
        assert "current_locale" in info
        assert "default_locale" in info
        assert "available_locales" in info
        assert "translations_loaded" in info
        assert "system_locale" in info
        
        assert info["current_locale"] == "es"
        assert info["default_locale"] == "es"
        assert isinstance(info["available_locales"], list)
        assert info["translations_loaded"] > 0
    
    def test_validate_translations(self):
        """Test validación de traducciones"""
        i18n = I18nManager()
        validation = i18n.validate_translations()
        
        assert "valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
        assert "total_keys" in validation
        assert "locales_checked" in validation
        
        assert isinstance(validation["valid"], bool)
        assert isinstance(validation["errors"], list)
        assert isinstance(validation["warnings"], list)
    
    def test_global_instance(self):
        """Test instancia global"""
        i18n1 = get_i18n()
        i18n2 = get_i18n()
        
        # Debería ser la misma instancia
        assert i18n1 is i18n2
        
        # Test función de conveniencia
        result = t("analysis.starting")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_setup_i18n(self):
        """Test configuración inicial de i18n"""
        i18n = setup_i18n("en")
        assert i18n.default_locale == "en"
        assert i18n.current_locale == "en"
        
        # Verificar que get_i18n() devuelve la nueva instancia
        global_i18n = get_i18n()
        assert global_i18n.current_locale == "en"


class TestI18nManagerWithMockFiles:
    """Pruebas con archivos mock para casos edge"""
    
    def test_load_translations_with_custom_files(self):
        """Test carga de traducciones con archivos personalizados"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivos de traducción mock
            es_file = temp_path / "es.json"
            en_file = temp_path / "en.json"
            
            es_content = {
                "test": {
                    "message": "Mensaje de prueba",
                    "with_var": "Prueba con {count} elementos"
                }
            }
            
            en_content = {
                "test": {
                    "message": "Test message", 
                    "with_var": "Test with {count} items"
                }
            }
            
            with open(es_file, 'w', encoding='utf-8') as f:
                json.dump(es_content, f, ensure_ascii=False)
            
            with open(en_file, 'w', encoding='utf-8') as f:
                json.dump(en_content, f, ensure_ascii=False)
            
            # Crear manager con directorio personalizado
            i18n = I18nManager()
            i18n.locales_dir = temp_path
            i18n._load_translations()
            
            # Verificar carga correcta
            assert "es" in i18n.translations
            assert "en" in i18n.translations
            
            # Test traducciones
            i18n.set_locale("es")
            assert i18n.t("test.message") == "Mensaje de prueba"
            assert i18n.t("test.with_var", count=3) == "Prueba con 3 elementos"
            
            i18n.set_locale("en")
            assert i18n.t("test.message") == "Test message"
            assert i18n.t("test.with_var", count=3) == "Test with 3 items"
    
    def test_error_handling_invalid_json(self):
        """Test manejo de errores con JSON inválido"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Crear archivo JSON inválido
            invalid_file = temp_path / "es.json"
            with open(invalid_file, 'w') as f:
                f.write("{ invalid json content")
            
            i18n = I18nManager()
            i18n.locales_dir = temp_path
            
            # No debería lanzar excepción, sino manejar el error
            i18n._load_translations()
            
            # Debería tener fallback
            assert isinstance(i18n.translations, dict)
    
    def test_missing_translations_fallback(self):
        """Test fallback cuando faltan traducciones"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Solo crear archivo en español
            es_file = temp_path / "es.json"
            es_content = {"test": {"spanish_only": "Solo en español"}}
            
            with open(es_file, 'w', encoding='utf-8') as f:
                json.dump(es_content, f, ensure_ascii=False)
            
            i18n = I18nManager()
            i18n.locales_dir = temp_path
            i18n._load_translations()
            
            # Debería funcionar en español
            i18n.set_locale("es")
            assert i18n.t("test.spanish_only") == "Solo en español"
            
            # En inglés debería hacer fallback a español
            i18n.set_locale("en")
            result = i18n.t("test.spanish_only")
            # Como no existe inglés, debería hacer fallback o mostrar clave
            assert isinstance(result, str)


@pytest.fixture
def sample_i18n():
    """Fixture con instancia de I18n para tests"""
    return I18nManager()


class TestI18nIntegration:
    """Pruebas de integración del sistema i18n"""
    
    def test_all_required_keys_present(self, sample_i18n):
        """Test que todas las claves requeridas están presentes"""
        required_keys = [
            "analysis.starting",
            "analysis.completed", 
            "database.title",
            "api.title",
            "frontend.title",
            "security.title",
            "recommendations.title"
        ]
        
        for locale in ["es", "en"]:
            sample_i18n.set_locale(locale)
            for key in required_keys:
                result = sample_i18n.t(key)
                # No debería devolver la clave entre corchetes
                assert not result.startswith("[")
                assert len(result) > 0
    
    def test_interpolation_edge_cases(self, sample_i18n):
        """Test casos edge de interpolación"""
        sample_i18n.set_locale("es")
        
        # Variables múltiples
        result = sample_i18n.t("database.relationships", types="one-to-many, many-to-many")
        assert "one-to-many" in result
        assert "many-to-many" in result
        
        # Variables con números
        result = sample_i18n.t("api.routes", count=100)
        assert "100" in result
        
        # Variables con strings vacíos
        result = sample_i18n.t("database.entities", count=0)
        assert "0" in result
    
    def test_concurrent_access(self, sample_i18n):
        """Test acceso concurrente (básico)"""
        import threading
        import time
        
        results = []
        
        def translate_worker():
            for i in range(10):
                result = sample_i18n.t("analysis.starting")
                results.append(result)
                time.sleep(0.01)  # Simular trabajo
        
        # Crear varios threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=translate_worker)
            threads.append(thread)
            thread.start()
        
        # Esperar que terminen
        for thread in threads:
            thread.join()
        
        # Verificar resultados
        assert len(results) == 30  # 10 * 3 threads
        assert all(isinstance(r, str) and len(r) > 0 for r in results)


if __name__ == "__main__":
    # Ejecutar tests básicos si se ejecuta directamente
    test_instance = TestI18nManager()
    
    print("🧪 Ejecutando pruebas de I18n Manager...")
    
    try:
        test_instance.test_initialization_default_spanish()
        print("✓ Test inicialización por defecto")
        
        test_instance.test_translation_basic()
        print("✓ Test traducción básica")
        
        test_instance.test_translation_with_interpolation()
        print("✓ Test interpolación de variables")
        
        test_instance.test_global_instance()
        print("✓ Test instancia global")
        
        print("🎉 Todas las pruebas básicas pasaron!")
        
    except Exception as e:
        print(f"❌ Error en pruebas: {e}")
        raise