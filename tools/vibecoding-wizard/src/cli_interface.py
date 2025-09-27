# -*- coding: utf-8 -*-
"""
CLI Interface for Vibecoding Configuration Wizard

Provides an intuitive command-line interface with interactive prompts,
progress indicators, and helpful error messages for configuring MCP connections.
"""

import os
import sys
import asyncio
import platform
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

# Color and formatting utilities
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    
    # Background colors
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'


class Icons:
    """ASCII icons for better visual feedback (fallback safe)"""
    CHECK = "✓"
    CROSS = "✗"
    WARNING = "!"
    INFO = "i"
    ARROW_RIGHT = ">"
    ARROW_DOWN = "v"
    BULLET = "*"
    GEAR = "+"
    ROCKET = "^"
    MAGNIFYING_GLASS = "?"
    COMPUTER = "#"
    WRENCH = "&"
    LIGHTBULB = "!"
    PACKAGE = "[]"
    FILE = "-"
    FOLDER = "/"


def supports_color() -> bool:
    """Check if terminal supports color output"""
    return (
        hasattr(sys.stdout, "isatty") and sys.stdout.isatty() and
        os.environ.get("TERM") != "dumb" and
        platform.system() != "Windows" or "ANSICON" in os.environ
    )


def colorize(text: str, color: str = '', bold: bool = False) -> str:
    """Apply color and formatting to text"""
    if not supports_color():
        return text
    
    formatting = Colors.BOLD if bold else ''
    return f"{formatting}{color}{text}{Colors.RESET}"


def print_header(text: str, icon: str = ''):
    """Print a styled header"""
    border = "=" * (len(text) + 4)
    print(f"\n{colorize(border, Colors.BRIGHT_CYAN)}")
    print(f"{colorize(f'{icon} {text}', Colors.BRIGHT_CYAN, bold=True)}")
    print(f"{colorize(border, Colors.BRIGHT_CYAN)}\n")


def print_section(text: str, icon: str = ''):
    """Print a section header"""
    print(f"\n{colorize(f'{icon} {text}', Colors.BRIGHT_BLUE, bold=True)}")
    print(f"{colorize('-' * (len(text) + 2), Colors.BLUE)}")


def print_success(text: str):
    """Print success message"""
    print(f"{colorize(Icons.CHECK, Colors.BRIGHT_GREEN)} {colorize(text, Colors.GREEN)}")


def print_error(text: str):
    """Print error message"""
    print(f"{colorize(Icons.CROSS, Colors.BRIGHT_RED)} {colorize(text, Colors.RED)}")


def print_warning(text: str):
    """Print warning message"""
    print(f"{colorize(Icons.WARNING, Colors.BRIGHT_YELLOW)} {colorize(text, Colors.YELLOW)}")


def print_info(text: str):
    """Print info message"""
    print(f"{colorize(Icons.INFO, Colors.BRIGHT_BLUE)} {colorize(text, Colors.BLUE)}")


def print_step(step: int, total: int, text: str):
    """Print step in a process"""
    step_text = f"[{step}/{total}]"
    print(f"\n{colorize(step_text, Colors.BRIGHT_MAGENTA, bold=True)} {text}")


class ProgressBar:
    """Simple progress bar for terminal"""
    
    def __init__(self, total: int, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, value: Optional[int] = None):
        """Update progress bar"""
        if value is not None:
            self.current = value
        else:
            self.current += 1
        
        if not supports_color():
            return
        
        progress = self.current / self.total
        filled = int(self.width * progress)
        bar = "#" * filled + "-" * (self.width - filled)
        percent = int(progress * 100)
        
        print(f"\r{colorize(f'Progress: [{bar}] {percent}%', Colors.BRIGHT_CYAN)}", end='', flush=True)
        
        if self.current >= self.total:
            print()  # New line when complete


class InteractivePrompts:
    """Interactive prompts for user input"""
    
    @staticmethod
    def yes_no(question: str, default: bool = True) -> bool:
        """Ask a yes/no question"""
        default_text = "Y/n" if default else "y/N"
        while True:
            response = input(f"{colorize('?', Colors.BRIGHT_BLUE)} {question} ({default_text}): ").strip().lower()
            
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            
            print_warning("Please enter 'y' or 'n'")
    
    @staticmethod
    def select_option(question: str, options: List[str], default: int = 0) -> int:
        """Select from multiple options"""
        print(f"\n{colorize('?', Colors.BRIGHT_BLUE)} {question}")
        
        for i, option in enumerate(options):
            marker = f"{colorize('>', Colors.BRIGHT_GREEN)}" if i == default else " "
            print(f"{marker} {i + 1}. {option}")
        
        while True:
            try:
                response = input(f"\nSelect option (1-{len(options)}, default {default + 1}): ").strip()
                
                if not response:
                    return default
                
                choice = int(response) - 1
                if 0 <= choice < len(options):
                    return choice
                else:
                    print_warning(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print_warning("Please enter a valid number")
    
    @staticmethod
    def text_input(question: str, default: str = "", required: bool = True) -> str:
        """Get text input from user"""
        default_text = f" (default: {default})" if default else ""
        required_text = " *" if required else ""
        
        while True:
            response = input(f"{colorize('?', Colors.BRIGHT_BLUE)} {question}{default_text}{colorize(required_text, Colors.RED)}: ").strip()
            
            if response:
                return response
            elif default:
                return default
            elif not required:
                return ""
            else:
                print_warning("This field is required")
    
    @staticmethod
    def path_input(question: str, default: str = "", must_exist: bool = False) -> str:
        """Get file/directory path input"""
        while True:
            path = InteractivePrompts.text_input(question, default, required=True)
            expanded_path = os.path.expanduser(path)
            
            if not must_exist or os.path.exists(expanded_path):
                return expanded_path
            else:
                print_error(f"Path does not exist: {expanded_path}")


class WizardInterface:
    """Main wizard interface for MCP configuration"""
    
    def __init__(self):
        self.environment = None
        self.validator = None
        self.configurations = []
    
    async def run(self):
        """Run the complete configuration wizard"""
        try:
            print_header("Vibecoding Configuration Wizard", Icons.ROCKET)
            print("Welcome! This wizard will help you configure MCP connections for your LLM clients.")
            print("We'll detect your environment, validate configurations, and fix any issues automatically.\n")
            
            # Step 1: Environment Detection
            await self._step_environment_detection()
            
            # Step 2: Environment Analysis
            await self._step_environment_analysis()
            
            # Step 3: Configuration Detection and Validation
            await self._step_configuration_validation()
            
            # Step 4: Configuration Setup/Repair
            await self._step_configuration_setup()
            
            # Step 5: Final Testing
            await self._step_final_testing()
            
            # Summary
            self._print_summary()
            
        except KeyboardInterrupt:
            print_warning("\nWizard interrupted by user. Goodbye!")
        except Exception as e:
            print_error(f"Unexpected error: {str(e)}")
            if InteractivePrompts.yes_no("Show detailed error information?", False):
                import traceback
                print(traceback.format_exc())
    
    async def _step_environment_detection(self):
        """Step 1: Detect system environment"""
        print_step(1, 5, "Detecting System Environment")
        
        # Import here to avoid circular imports
        from environment_detector import EnvironmentDetector
        
        progress = ProgressBar(4)
        
        print("Scanning system configuration...")
        progress.update(1)
        
        detector = EnvironmentDetector()
        self.environment = detector.detect_full_environment()
        progress.update(2)
        
        print("Analyzing Python environment...")
        progress.update(3)
        
        print("Checking for existing MCP installations...")
        progress.update(4)
        
        print_success("Environment detection completed!")
        
        # Show key findings
        print(f"\n{Icons.COMPUTER} System Information:")
        print(f"  OS: {self.environment.os_type.value.title()} {self.environment.os_version}")
        print(f"  Python: {self.environment.python_env.version} ({'Virtual env' if self.environment.python_env.is_virtual_env else 'System'})")
        print(f"  LLM Clients: {len(self.environment.llm_clients)} detected")
        print(f"  MCP Installed: {'Yes' if self.environment.mcp_installation.is_installed else 'No'}")
    
    async def _step_environment_analysis(self):
        """Step 2: Analyze environment compatibility"""
        print_step(2, 5, "Analyzing Environment Compatibility")
        
        from environment_detector import EnvironmentAnalyzer
        
        analyzer = EnvironmentAnalyzer(self.environment)
        analysis = analyzer.analyze_compatibility()
        
        # Show compatibility score
        score = analysis['compatibility_score']
        if score >= 80:
            color = Colors.BRIGHT_GREEN
            status = "Excellent"
        elif score >= 60:
            color = Colors.YELLOW
            status = "Good"
        elif score >= 40:
            color = Colors.BRIGHT_YELLOW
            status = "Fair"
        else:
            color = Colors.BRIGHT_RED
            status = "Poor"
        
        print(f"\nCompatibility Score: {colorize(f'{score}/100 ({status})', color, bold=True)}")
        
        # Show requirements status
        if analysis['requirements_met']:
            print_success("Requirements met:")
            for req in analysis['requirements_met']:
                print(f"  {Icons.CHECK} {req}")
        
        if analysis['missing_requirements']:
            print_warning("Missing requirements:")
            for req in analysis['missing_requirements']:
                print(f"  {Icons.CROSS} {req}")
        
        if analysis['issues']:
            print_error("Issues found:")
            for issue in analysis['issues']:
                print(f"  {Icons.WARNING} {issue}")
        
        # Show recommendations
        if analysis['recommendations']:
            print_info("Recommendations:")
            for rec in analysis['recommendations']:
                print(f"  {Icons.LIGHTBULB} {rec}")
        
        # Ask if user wants to proceed with fixes
        if analysis['issues'] or analysis['missing_requirements']:
            if not InteractivePrompts.yes_no("Would you like the wizard to help fix these issues?"):
                print_info("You can run the wizard again after addressing the issues manually.")
                return
    
    async def _step_configuration_validation(self):
        """Step 3: Detect and validate existing configurations"""
        print_step(3, 5, "Validating Existing Configurations")
        
        from config_validator import ConfigurationValidator
        
        self.validator = ConfigurationValidator(self.environment)
        
        if not self.environment.llm_clients:
            print_warning("No supported LLM clients detected.")
            if InteractivePrompts.yes_no("Would you like to configure for Claude Desktop anyway?"):
                # Create a mock client info for Claude Desktop
                from environment_detector import LLMClientInfo, LLMClient
                mock_client = LLMClientInfo(
                    client_type=LLMClient.CLAUDE_DESKTOP,
                    is_installed=False,
                    installation_path=None,
                    config_path=self._get_default_claude_config_path(),
                    version=None
                )
                self.environment.llm_clients = [mock_client]
            else:
                print_info("Skipping configuration validation.")
                return
        
        # Validate configurations
        print("Validating configurations...")
        self.configurations = await self.validator.validate_all_configurations()
        
        # Report results
        for config in self.configurations:
            client_name = config.config_type.value.replace('_', ' ').title()
            print(f"\n{Icons.FILE} {client_name} Configuration:")
            
            if config.is_valid:
                print_success(f"Configuration is valid ({len(config.servers)} servers)")
            else:
                error_count = sum(1 for r in config.validation_results if r.status.value == 'error')
                warning_count = sum(1 for r in config.validation_results if r.status.value == 'warning')
                print_error(f"Configuration has issues ({error_count} errors, {warning_count} warnings)")
            
            # Show detailed results if requested
            if config.validation_results and not config.is_valid:
                if InteractivePrompts.yes_no("Show detailed validation results?", False):
                    self._show_validation_details(config)
    
    async def _step_configuration_setup(self):
        """Step 4: Setup or repair configurations"""
        print_step(4, 5, "Setting up MCP Configurations")
        
        if not self.configurations:
            print_info("No configurations to set up.")
            return
        
        from config_validator import ConfigurationGenerator
        generator = ConfigurationGenerator(self.validator)
        
        for config in self.configurations:
            if config.is_valid:
                print_success(f"{config.config_type.value.replace('_', ' ').title()} configuration is already valid")
                continue
            
            client_name = config.config_type.value.replace('_', ' ').title()
            print_section(f"Configuring {client_name}", Icons.WRENCH)
            
            if InteractivePrompts.yes_no(f"Fix {client_name} configuration?"):
                await self._fix_configuration(config, generator)
    
    async def _step_final_testing(self):
        """Step 5: Test final configurations"""
        print_step(5, 5, "Testing Final Configurations")
        
        if not self.validator:
            print_info("No configurations to test.")
            return
        
        print("Running final validation tests...")
        
        # Re-validate configurations
        updated_configs = await self.validator.validate_all_configurations()
        
        all_valid = True
        for config in updated_configs:
            client_name = config.config_type.value.replace('_', ' ').title()
            
            if config.is_valid:
                print_success(f"{client_name}: All tests passed")
            else:
                print_error(f"{client_name}: Issues remain")
                all_valid = False
        
        if all_valid:
            print_success("All configurations are working correctly!")
        else:
            print_warning("Some configurations still have issues. Check the logs above.")
    
    def _show_validation_details(self, config):
        """Show detailed validation results"""
        for result in config.validation_results:
            if result.status.value == 'error':
                icon = Icons.CROSS
                color = Colors.RED
            elif result.status.value == 'warning':
                icon = Icons.WARNING
                color = Colors.YELLOW
            else:
                icon = Icons.CHECK
                color = Colors.GREEN
            
            print(f"  {colorize(icon, color)} {result.check_name}: {result.message}")
            
            if result.fix_suggestion:
                print(f"    {Icons.LIGHTBULB} Fix: {result.fix_suggestion}")
    
    async def _fix_configuration(self, config, generator):
        """Fix a specific configuration"""
        from config_validator import ConfigType
        
        if config.config_type == ConfigType.CLAUDE_DESKTOP:
            success, message = await generator.create_claude_desktop_config()
            
            if success:
                print_success(message)
            else:
                print_error(message)
        else:
            print_warning(f"Automatic fixing not yet supported for {config.config_type.value}")
    
    def _get_default_claude_config_path(self) -> str:
        """Get default Claude Desktop configuration path"""
        if self.environment.os_type.value == "macos":
            return os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
        elif self.environment.os_type.value == "windows":
            return os.path.expanduser("~/AppData/Roaming/Claude/claude_desktop_config.json")
        else:
            return os.path.expanduser("~/.config/Claude/claude_desktop_config.json")
    
    def _print_summary(self):
        """Print final summary"""
        print_header("Configuration Summary", Icons.CHECK)
        
        if self.environment:
            # Environment summary
            print(f"{Icons.COMPUTER} Environment:")
            print(f"  OS: {self.environment.os_type.value.title()}")
            print(f"  Python: {self.environment.python_env.version}")
            print(f"  MCP Library: {'Installed' if self.environment.mcp_installation.is_installed else 'Not installed'}")
        
        # Configuration summary
        if self.configurations:
            print(f"\n{Icons.GEAR} Configurations:")
            for config in self.configurations:
                client_name = config.config_type.value.replace('_', ' ').title()
                status = "Valid" if config.is_valid else "Issues found"
                icon = Icons.CHECK if config.is_valid else Icons.WARNING
                print(f"  {icon} {client_name}: {status}")
        
        # Next steps
        print(f"\n{Icons.ROCKET} Next Steps:")
        if self.environment and self.environment.mcp_installation.is_installed:
            print(f"  1. Start your MCP server if it's not running")
            print(f"  2. Open your LLM client and test the connection")
            print(f"  3. Try using MCP tools in your conversations")
        else:
            print(f"  1. Install the MCP library: pip install mcp")
            print(f"  2. Start your MCP server")
            print(f"  3. Run this wizard again to complete the setup")
        
        print(f"\n{colorize('Happy coding with Vibecoding!', Colors.BRIGHT_GREEN, bold=True)}")


def main():
    """Main entry point for the CLI wizard"""
    wizard = WizardInterface()
    asyncio.run(wizard.run())


if __name__ == "__main__":
    main()