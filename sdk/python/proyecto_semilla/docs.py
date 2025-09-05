"""
Proyecto Semilla SDK Auto-Documentation System
Generates and updates documentation automatically for modules
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from jinja2 import Template

from .models import ModuleSpec, ModuleStatus
from .client import ProyectoSemillaClient
from .exceptions import ProyectoSemillaError


class AutoDocumentation:
    """
    Auto-Documentation System for Proyecto Semilla

    Automatically generates and updates documentation for modules
    using templates and real-time data from the system.
    """

    def __init__(self, client: ProyectoSemillaClient, templates_path: Optional[str] = None):
        """
        Initialize Auto-Documentation system

        Args:
            client: Proyecto Semilla client instance
            templates_path: Path to documentation templates
        """
        self.client = client
        self.templates_path = Path(templates_path or "docs/templates")
        self.generated_path = Path("docs/generated")
        self.modules_path = Path("modules")

        # Ensure directories exist
        self.generated_path.mkdir(parents=True, exist_ok=True)

    async def update_module_docs(self, module_name: str) -> Dict[str, Any]:
        """
        Update documentation for a specific module

        Args:
            module_name: Name of the module to update docs for

        Returns:
            Dict with update results
        """
        try:
            # Get module information
            module_info = await self._get_module_info(module_name)
            if not module_info:
                raise ProyectoSemillaError(f"Module '{module_name}' not found")

            # Generate README
            readme_content = await self._generate_readme(module_info)
            readme_path = self.modules_path / module_name / "README.md"
            await self._write_file(readme_path, readme_content)

            # Generate API documentation
            api_docs = await self._generate_api_docs(module_info)
            api_docs_path = self.generated_path / f"{module_name}_api.md"
            await self._write_file(api_docs_path, api_docs)

            # Update main index
            await self._update_main_index(module_name)

            return {
                "success": True,
                "files_updated": 3,
                "readme_generated": True,
                "api_docs_generated": True,
                "index_updated": True,
                "module_name": module_name,
                "updated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "module_name": module_name,
                "updated_at": datetime.now().isoformat()
            }

    async def _get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive module information"""
        try:
            # Get module status
            status = await self.client.get_module_status(module_name)

            # Get module spec (if available)
            # This would come from module metadata or configuration
            spec = await self._get_module_spec(module_name)

            return {
                "name": module_name,
                "display_name": status.description or module_name.replace('_', ' ').title(),
                "description": f"Auto-generated {module_name} module",
                "version": "1.0.0",
                "category": getattr(spec, 'category', 'custom') if spec else 'custom',
                "status": status.status,
                "files_count": status.files_count or 0,
                "api_endpoints_count": status.api_endpoints_count or 0,
                "ui_components_count": status.ui_components_count or 0,
                "generated_date": status.created_at.isoformat(),
                "updated_date": status.updated_at.isoformat(),
                "features": getattr(spec, 'features', []) if spec else [],
                "entities": getattr(spec, 'entities', []) if spec else [],
                "apis": getattr(spec, 'apis', []) if spec else [],
                "ui_components": getattr(spec, 'ui_components', []) if spec else []
            }

        except Exception:
            return None

    async def _get_module_spec(self, module_name: str) -> Optional[ModuleSpec]:
        """Get module specification from metadata"""
        # This would read from module configuration files
        # For now, return None (placeholder for future implementation)
        return None

    async def _generate_readme(self, module_info: Dict[str, Any]) -> str:
        """Generate README content using template"""
        template_path = self.templates_path / "module_readme.md"

        if not template_path.exists():
            raise ProyectoSemillaError(f"Template not found: {template_path}")

        template_content = template_path.read_text()
        template = Template(template_content)

        # Format features list
        features_list = "\n".join(f"- ✅ **{feature}**" for feature in module_info.get('features', []))
        if not features_list:
            features_list = "- ✅ Auto-generated module functionality"

        # Format entities list
        entities_list = "\n".join(f"- 📋 **{entity.get('name', 'Unknown')}**: {entity.get('description', 'No description')}"
                                 for entity in module_info.get('entities', []))
        if not entities_list:
            entities_list = "- 📋 Auto-generated data models"

        # Format APIs list
        apis_list = "\n".join(f"- 🔌 **{api.get('method', 'GET')}** `{api.get('path', '/')}`: {api.get('description', 'API endpoint')}"
                             for api in module_info.get('apis', []))
        if not apis_list:
            apis_list = "- 🔌 RESTful API endpoints"

        # Format UI components list
        ui_components_list = "\n".join(f"- 🖥️ **{component}**" for component in module_info.get('ui_components', []))
        if not ui_components_list:
            ui_components_list = "- 🖥️ Responsive web interface"

        # Format API endpoints for reference
        api_endpoints = "\n".join(f"#### {api.get('method', 'GET')} {api.get('path', '/')}\n"
                                 f"{api.get('description', 'API endpoint')}\n"
                                 for api in module_info.get('apis', []))

        # Format data models
        data_models = "\n".join(f"#### {entity.get('name', 'Unknown')}\n"
                               f"{entity.get('description', 'Data model')}\n"
                               f"**Fields:** {', '.join(field.get('name', '') for field in entity.get('fields', []))}\n"
                               for entity in module_info.get('entities', []))

        return template.render(
            name=module_info['name'],
            display_name=module_info['display_name'],
            description=module_info['description'],
            version=module_info['version'],
            category=module_info['category'],
            generated_date=module_info['generated_date'],
            updated_date=module_info['updated_date'],
            features_list=features_list,
            entities_list=entities_list,
            apis_list=apis_list,
            ui_components_list=ui_components_list,
            api_endpoints=api_endpoints,
            data_models=data_models
        )

    async def _generate_api_docs(self, module_info: Dict[str, Any]) -> str:
        """Generate API documentation"""
        api_docs = f"# {module_info['display_name']} - API Documentation\n\n"
        api_docs += f"**Version:** {module_info['version']}\n"
        api_docs += f"**Generated:** {datetime.now().isoformat()}\n\n"

        if module_info.get('apis'):
            api_docs += "## Endpoints\n\n"
            for api in module_info['apis']:
                api_docs += f"### {api.get('method', 'GET')} {api.get('path', '/')}\n\n"
                api_docs += f"{api.get('description', 'API endpoint')}\n\n"

                if api.get('parameters'):
                    api_docs += "**Parameters:**\n"
                    for param in api['parameters']:
                        api_docs += f"- `{param['name']}` ({param.get('type', 'string')}): {param.get('description', '')}\n"
                    api_docs += "\n"

                if api.get('responses'):
                    api_docs += "**Responses:**\n"
                    for status_code, response in api['responses'].items():
                        api_docs += f"- `{status_code}`: {response.get('description', '')}\n"
                    api_docs += "\n"
        else:
            api_docs += "No API endpoints documented yet.\n"

        return api_docs

    async def _update_main_index(self, module_name: str):
        """Update main documentation index"""
        index_path = self.generated_path / "modules_index.md"

        # Read existing index or create new one
        if index_path.exists():
            existing_content = index_path.read_text()
        else:
            existing_content = "# Proyecto Semilla - Modules Index\n\n"
            existing_content += "Auto-generated index of all available modules.\n\n"
            existing_content += f"**Last Updated:** {datetime.now().isoformat()}\n\n"
            existing_content += "## Available Modules\n\n"

        # Check if module is already in index
        if f"## {module_name}" in existing_content:
            # Update existing entry
            lines = existing_content.split('\n')
            in_module_section = False
            for i, line in enumerate(lines):
                if line.startswith(f"## {module_name}"):
                    in_module_section = True
                    lines[i+1] = f"Updated: {datetime.now().isoformat()}"
                    break
                elif line.startswith("## ") and in_module_section:
                    break

            existing_content = '\n'.join(lines)
        else:
            # Add new module entry
            existing_content += f"## {module_name}\n\n"
            existing_content += f"Updated: {datetime.now().isoformat()}\n\n"
            existing_content += f"📖 [README](modules/{module_name}/README.md)\n"
            existing_content += f"🔌 [API Docs](generated/{module_name}_api.md)\n\n"

        await self._write_file(index_path, existing_content)

    async def _write_file(self, path: Path, content: str):
        """Write content to file asynchronously"""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    async def generate_full_docs(self) -> Dict[str, Any]:
        """
        Generate documentation for all modules

        Returns:
            Dict with generation results
        """
        try:
            # Get all modules
            modules = await self.client.list_modules()

            results = []
            for module in modules:
                result = await self.update_module_docs(module.description or module.name)
                results.append(result)

            return {
                "success": True,
                "modules_processed": len(results),
                "total_files_updated": sum(r.get('files_updated', 0) for r in results if r['success']),
                "results": results,
                "generated_at": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "generated_at": datetime.now().isoformat()
            }

    async def validate_docs(self, module_name: str) -> Dict[str, Any]:
        """
        Validate that documentation exists and is up to date

        Args:
            module_name: Name of module to validate

        Returns:
            Validation results
        """
        results = {
            "module_name": module_name,
            "readme_exists": False,
            "api_docs_exist": False,
            "index_updated": False,
            "all_valid": False
        }

        # Check README
        readme_path = self.modules_path / module_name / "README.md"
        results["readme_exists"] = readme_path.exists()

        # Check API docs
        api_docs_path = self.generated_path / f"{module_name}_api.md"
        results["api_docs_exist"] = api_docs_path.exists()

        # Check index
        index_path = self.generated_path / "modules_index.md"
        if index_path.exists():
            index_content = index_path.read_text()
            results["index_updated"] = f"## {module_name}" in index_content

        results["all_valid"] = all([
            results["readme_exists"],
            results["api_docs_exist"],
            results["index_updated"]
        ])

        return results