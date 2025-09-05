#!/usr/bin/env python3
"""
Vibecoding Configuration Wizard - Main Entry Point

This is the main executable for the Vibecoding Configuration Wizard.
It provides a comprehensive solution for configuring MCP connections
with any LLM client through intelligent environment detection and
automated configuration validation.

Usage:
    python main.py [OPTIONS]
    
Options:
    --debug         Enable debug mode with detailed logging
    --no-color      Disable colored output
    --config-only   Only validate existing configurations (no setup)
    --client TYPE   Target specific client type (claude_desktop, vscode, etc.)
    --help          Show this help message
    
Examples:
    python main.py                          # Run full wizard
    python main.py --debug                  # Run with debug output
    python main.py --config-only            # Just validate configurations
    python main.py --client claude_desktop  # Configure only Claude Desktop
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from cli_interface import WizardInterface, print_header, print_error, colorize, Colors, Icons
from error_handler import get_error_handler
from environment_detector import EnvironmentDetector
from config_validator import ConfigurationValidator, ConfigType


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Vibecoding Configuration Wizard - Intelligent MCP Setup",
        epilog="""
Examples:
  %(prog)s                          Run the complete wizard
  %(prog)s --debug                  Enable debug output
  %(prog)s --config-only            Only validate existing configurations
  %(prog)s --client claude_desktop  Target Claude Desktop only
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logging"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored terminal output"
    )
    
    parser.add_argument(
        "--config-only",
        action="store_true",
        help="Only validate existing configurations (no setup)"
    )
    
    parser.add_argument(
        "--client",
        choices=["claude_desktop", "vscode", "cursor", "custom"],
        help="Target specific client type"
    )
    
    parser.add_argument(
        "--project-path",
        type=str,
        help="Path to project root (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"Vibecoding Configuration Wizard 1.0.0"
    )
    
    return parser.parse_args()


class WizardApp:
    """Main application class for the wizard"""
    
    def __init__(self, args):
        self.args = args
        self.error_handler = get_error_handler(debug_mode=args.debug)
        
        # Configure color support
        if args.no_color:
            import cli_interface
            cli_interface.supports_color = lambda: False
    
    async def run(self):
        """Run the wizard application"""
        try:
            with self.error_handler.handle_errors("wizard_startup", "main_app"):
                await self._run_wizard()
        except KeyboardInterrupt:
            print_error(f"\n{Icons.WARNING} Wizard interrupted by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Fatal error: {str(e)}")
            if self.args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    
    async def _run_wizard(self):
        """Internal wizard execution"""
        # Show welcome banner
        self._show_welcome()
        
        if self.args.config_only:
            await self._run_validation_only()
        else:
            await self._run_full_wizard()
    
    def _show_welcome(self):
        """Show welcome message"""
        print_header("Vibecoding Configuration Wizard v1.0.0", Icons.ROCKET)
        
        print(f"{Icons.COMPUTER} {colorize('System:', Colors.BRIGHT_BLUE, bold=True)} Auto-detecting environment and MCP configurations")
        print(f"{Icons.GEAR} {colorize('Validation:', Colors.BRIGHT_BLUE, bold=True)} Testing connections and fixing issues")
        print(f"{Icons.WRENCH} {colorize('Setup:', Colors.BRIGHT_BLUE, bold=True)} Intelligent configuration generation")
        print(f"{Icons.CHECK} {colorize('Recovery:', Colors.BRIGHT_BLUE, bold=True)} Automated error handling and fixes")
        
        if self.args.debug:
            print(f"\n{colorize('Debug mode enabled - detailed logging active', Colors.YELLOW)}")
        
        print()
    
    async def _run_validation_only(self):
        """Run only configuration validation"""
        print_header("Configuration Validation Mode", Icons.MAGNIFYING_GLASS)
        
        # Detect environment
        detector = EnvironmentDetector(self.args.project_path)
        environment = detector.detect_full_environment()
        
        # Validate configurations
        validator = ConfigurationValidator(environment)
        configurations = await validator.validate_all_configurations()
        
        # Show results
        self._show_validation_results(configurations)
    
    async def _run_full_wizard(self):
        """Run the complete wizard"""
        wizard = WizardInterface()
        
        # Override specific client if specified
        if self.args.client:
            wizard.target_client = ConfigType(self.args.client)
        
        await wizard.run()
    
    def _show_validation_results(self, configurations):
        """Show validation results in config-only mode"""
        from cli_interface import print_success, print_warning, print_info
        
        if not configurations:
            print_warning("No MCP configurations found")
            return
        
        print_info(f"Found {len(configurations)} MCP configuration(s)")
        
        for config in configurations:
            client_name = config.config_type.value.replace('_', ' ').title()
            
            if config.is_valid:
                print_success(f"{client_name}: Configuration is valid")
            else:
                error_count = sum(1 for r in config.validation_results 
                                if r.status.value == 'error')
                warning_count = sum(1 for r in config.validation_results 
                                  if r.status.value == 'warning')
                
                if error_count > 0:
                    print_error(f"{client_name}: {error_count} error(s), {warning_count} warning(s)")
                else:
                    print_warning(f"{client_name}: {warning_count} warning(s)")
                
                # Show details
                for result in config.validation_results:
                    if result.status.value in ['error', 'warning']:
                        status_icon = Icons.CROSS if result.status.value == 'error' else Icons.WARNING
                        print(f"  {status_icon} {result.check_name}: {result.message}")


def check_requirements():
    """Check basic requirements before running"""
    # Check Python version
    if sys.version_info < (3, 8):
        print_error("Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    
    # Check if we can import required modules
    try:
        import json
        import asyncio
        import pathlib
    except ImportError as e:
        print_error(f"Missing required Python module: {e}")
        return False
    
    return True


async def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()
    
    # Check basic requirements
    if not check_requirements():
        sys.exit(1)
    
    # Create and run wizard app
    app = WizardApp(args)
    await app.run()


if __name__ == "__main__":
    try:
        # Ensure event loop compatibility across platforms
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        print(f"\n{colorize('Goodbye! =K', Colors.BRIGHT_BLUE)}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)