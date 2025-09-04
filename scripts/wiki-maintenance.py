#!/usr/bin/env python3
"""
🤖 Claude Code Wiki Maintenance Agent
Automatiza la sincronización de documentación entre repositorio privado y wiki público
"""

import os
import sys
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import yaml
import argparse

class WikiMaintenanceAgent:
    """Agente para mantenimiento automático del GitHub Wiki"""
    
    def __init__(self, config_path: str = "claude-agents.config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        self.project_root = Path(".")
        self.private_repo = Path("../proyecto-semilla-privados")
        self.wiki_temp = Path("wiki-temp")
        
    def load_config(self) -> Dict:
        """Carga la configuración de agentes"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            sys.exit(1)
            
    def setup_wiki_directory(self):
        """Prepara el directorio temporal para wiki"""
        if self.wiki_temp.exists():
            shutil.rmtree(self.wiki_temp)
        self.wiki_temp.mkdir(parents=True)
        print(f"📁 Directorio wiki creado: {self.wiki_temp}")
        
    def remove_private_sections(self, content: str) -> str:
        """Remueve secciones marcadas como privadas del contenido"""
        # Patrones para detectar contenido privado
        private_patterns = [
            r'PRIVATE:.*?END_PRIVATE',
            r'INTERNAL:.*?END_INTERNAL', 
            r'TODO:.*?\n',
            r'KILO CODE:.*?\n',
            r'CONFIDENTIAL:.*?END_CONFIDENTIAL'
        ]
        
        cleaned_content = content
        for pattern in private_patterns:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL)
            
        # Limpiar líneas vacías múltiples
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content)
        
        return cleaned_content.strip()
        
    def transform_for_wiki(self, content: str, transform_type: str) -> str:
        """Transforma contenido según el tipo especificado"""
        if transform_type == "remove_private_sections":
            return self.remove_private_sections(content)
            
        elif transform_type == "format_release_notes":
            # Formatear changelog para wiki
            content = re.sub(r'^#', '##', content, flags=re.MULTILINE)
            return f"# 📋 Release Notes\n\n{content}"
            
        elif transform_type == "wiki_format":
            # Adaptar enlaces relativos para wiki
            content = re.sub(r'\[(.*?)\]\((?!http)(.*?)\)', r'[\1](\2)', content)
            return content
            
        return content
        
    def sync_file(self, source_path: Path, target_name: str, transform: str):
        """Sincroniza un archivo desde source a wiki"""
        if not source_path.exists():
            print(f"⚠️ Archivo fuente no encontrado: {source_path}")
            return False
            
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Aplicar transformación
            transformed_content = self.transform_for_wiki(content, transform)
            
            # Escribir archivo transformado
            target_path = self.wiki_temp / target_name
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(transformed_content)
                
            print(f"✅ Sincronizado: {source_path} -> {target_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error sincronizando {source_path}: {e}")
            return False
            
    def generate_project_metrics(self) -> str:
        """Genera métricas automáticas del proyecto"""
        try:
            # Obtener información de git
            commit_count = subprocess.check_output(
                ['git', 'rev-list', '--all', '--count'],
                cwd=self.project_root,
                text=True
            ).strip()
            
            contributors = subprocess.check_output(
                ['git', 'log', '--format=%ae'],
                cwd=self.project_root,
                text=True
            )
            unique_contributors = len(set(contributors.strip().split('\n')))
            
            last_activity = subprocess.check_output(
                ['git', 'log', '-1', '--format=%ad', '--date=relative'],
                cwd=self.project_root,
                text=True
            ).strip()
            
            # Obtener información de releases
            try:
                latest_tag = subprocess.check_output(
                    ['git', 'describe', '--tags', '--abbrev=0'],
                    cwd=self.project_root,
                    text=True,
                    stderr=subprocess.DEVNULL
                ).strip()
            except:
                latest_tag = "v0.1.0-dev"
                
        except Exception as e:
            print(f"⚠️ Error obteniendo métricas: {e}")
            commit_count = "N/A"
            unique_contributors = "N/A"
            last_activity = "N/A"
            latest_tag = "N/A"
            
        metrics_content = f"""# 📊 Métricas del Proyecto

**Última Actualización**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

## 🚀 Información General
- **Versión Actual**: {latest_tag}
- **Estado**: En desarrollo activo
- **Licencia**: MIT License
- **Arquitectura**: Multi-tenant SaaS

## 📈 Estadísticas del Repositorio
- **Commits Totales**: {commit_count}
- **Colaboradores Únicos**: {unique_contributors}
- **Última Actividad**: {last_activity}

## 🎯 Progreso de Desarrollo
- **Core Backend**: ✅ Completado (v0.1.0)
- **Autenticación JWT**: ✅ Implementado
- **Row-Level Security**: ✅ Configurado
- **API Documentación**: ✅ OpenAPI/Swagger
- **Docker Setup**: ✅ Funcionando
- **Testing Suite**: 🔄 En progreso
- **Frontend**: 📅 Próximamente

## 🔧 Stack Tecnológico
- **Backend**: FastAPI + SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL 15 + Redis
- **Autenticación**: JWT con refresh tokens
- **Contenedores**: Docker + Docker Compose
- **Documentación**: OpenAPI 3.0

## 📋 Roadmap Público
Consultar [Roadmap completo](Roadmap.md) para detalles de versiones futuras.

---
*Métricas generadas automáticamente por Claude Code Wiki Agent*
"""
        return metrics_content
        
    def update_contributor_list(self) -> str:
        """Genera lista actualizada de contribuidores"""
        try:
            # Obtener contribuidores con estadísticas
            contributors_raw = subprocess.check_output(
                ['git', 'shortlog', '-sn', '--all'],
                cwd=self.project_root,
                text=True
            )
            
            contributors_content = f"""# 👥 Contribuidores

**Última Actualización**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

## 🏆 Hall of Fame

{contributors_raw}

## 🙏 Reconocimientos Especiales
- **KILO CODE**: Desarrollo backend principal
- **Claude Code**: Automatización y auditoría de calidad

## 🤝 Cómo Contribuir
Consulta nuestra [Guía de Contribución](../CONTRIBUTING.md) para empezar.

---
*Lista generada automáticamente*
"""
            return contributors_content
            
        except Exception as e:
            print(f"⚠️ Error generando lista de contribuidores: {e}")
            return "# 👥 Contribuidores\n\nError generando lista automática."
            
    def sync_documentation(self):
        """Ejecuta sincronización completa de documentación"""
        print("🚀 Iniciando sincronización de documentación...")
        
        # Obtener configuración de sync targets
        sync_targets = self.config.get('agents', {}).get('wiki_maintenance', {}).get('sync_targets', [])
        
        success_count = 0
        for target in sync_targets:
            source_path = Path(target['source'])
            if not source_path.is_absolute():
                # Resolver ruta relativa desde project_root
                if target['source'].startswith('../'):
                    source_path = self.project_root / target['source']
                else:
                    source_path = self.project_root / target['source']
                    
            if self.sync_file(source_path, target['target'], target['transform']):
                success_count += 1
                
        # Generar archivos automáticos
        print("📊 Generando métricas de proyecto...")
        metrics_content = self.generate_project_metrics()
        with open(self.wiki_temp / "Project-Metrics.md", 'w', encoding='utf-8') as f:
            f.write(metrics_content)
            
        print("👥 Generando lista de contribuidores...")
        contributors_content = self.update_contributor_list()
        with open(self.wiki_temp / "Contributors.md", 'w', encoding='utf-8') as f:
            f.write(contributors_content)
            
        print(f"✅ Sincronización completada: {success_count} archivos procesados")
        return success_count > 0
        
    def deploy_to_wiki(self):
        """Despliega contenido a GitHub Wiki (simulado)"""
        print("📤 Preparando despliegue a GitHub Wiki...")
        
        if not self.wiki_temp.exists() or not any(self.wiki_temp.iterdir()):
            print("❌ No hay contenido para desplegar")
            return False
            
        print("📁 Archivos preparados para Wiki:")
        for file_path in self.wiki_temp.iterdir():
            if file_path.is_file():
                size_kb = file_path.stat().st_size / 1024
                print(f"  - {file_path.name} ({size_kb:.1f} KB)")
                
        # En una implementación real, aquí se haría:
        # 1. Clone del wiki repository
        # 2. Copiar archivos desde wiki_temp
        # 3. Commit y push de cambios
        # 4. Cleanup de archivos temporales
        
        print("✅ Contenido listo para despliegue manual a Wiki")
        print(f"💡 Para desplegar, copiar archivos de {self.wiki_temp}/ al repositorio wiki")
        
        return True
        
    def run(self, action: str = "full_sync"):
        """Ejecuta el agente de mantenimiento de wiki"""
        print("🤖 Claude Code Wiki Maintenance Agent")
        print("=" * 50)
        
        self.setup_wiki_directory()
        
        if action in ["full_sync", "sync"]:
            if self.sync_documentation():
                self.deploy_to_wiki()
            else:
                print("❌ Error en sincronización de documentación")
                return False
                
        elif action == "metrics":
            print("📊 Generando solo métricas...")
            metrics = self.generate_project_metrics()
            with open(self.wiki_temp / "Project-Metrics.md", 'w') as f:
                f.write(metrics)
            print("✅ Métricas generadas")
            
        elif action == "contributors":
            print("👥 Generando solo lista de contribuidores...")
            contributors = self.update_contributor_list()
            with open(self.wiki_temp / "Contributors.md", 'w') as f:
                f.write(contributors)
            print("✅ Lista de contribuidores generada")
            
        else:
            print(f"❌ Acción desconocida: {action}")
            return False
            
        return True

def main():
    parser = argparse.ArgumentParser(
        description="🤖 Claude Code Wiki Maintenance Agent"
    )
    parser.add_argument(
        'action',
        choices=['full_sync', 'sync', 'metrics', 'contributors'],
        default='full_sync',
        help='Acción a ejecutar'
    )
    parser.add_argument(
        '--config',
        default='claude-agents.config.yaml',
        help='Archivo de configuración'
    )
    
    args = parser.parse_args()
    
    agent = WikiMaintenanceAgent(args.config)
    success = agent.run(args.action)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()