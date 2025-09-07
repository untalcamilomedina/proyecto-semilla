"""
Unit tests for CLI Interface System
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from io import StringIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from cli_interface import (
    Colors, Icons, supports_color, colorize, 
    print_header, print_section, print_success, print_error, 
    print_warning, print_info, print_step,
    ProgressBar, InteractivePrompts, WizardInterface
)


class TestColorAndFormatting:
    """Test cases for color and formatting utilities"""
    
    def test_supports_color_true(self):
        """Test color support detection when supported"""
        with patch('sys.stdout.isatty', return_value=True):
            with patch.dict(os.environ, {"TERM": "xterm-256color"}, clear=False):
                with patch('platform.system', return_value='Darwin'):
                    assert supports_color()
    
    def test_supports_color_false_no_tty(self):
        """Test color support detection without TTY"""
        with patch('sys.stdout.isatty', return_value=False):
            assert not supports_color()
    
    def test_supports_color_false_dumb_term(self):
        """Test color support detection with dumb terminal"""
        with patch('sys.stdout.isatty', return_value=True):
            with patch.dict(os.environ, {"TERM": "dumb"}, clear=False):
                assert not supports_color()
    
    def test_colorize_with_support(self):
        """Test colorizing text when color is supported"""
        with patch('cli_interface.supports_color', return_value=True):
            result = colorize("test", Colors.RED, bold=True)
            assert Colors.BOLD in result
            assert Colors.RED in result
            assert Colors.RESET in result
            assert "test" in result
    
    def test_colorize_without_support(self):
        """Test colorizing text when color is not supported"""
        with patch('cli_interface.supports_color', return_value=False):
            result = colorize("test", Colors.RED, bold=True)
            assert result == "test"
    
    @patch('builtins.print')
    def test_print_header(self, mock_print):
        """Test header printing"""
        print_header("Test Header", Icons.ROCKET)
        
        # Should call print multiple times (border, header, border)
        assert mock_print.call_count >= 3
        
        # Check that header text is in one of the calls
        calls = [str(call) for call in mock_print.call_args_list]
        header_found = any("Test Header" in call for call in calls)
        assert header_found
    
    @patch('builtins.print')
    def test_print_section(self, mock_print):
        """Test section printing"""
        print_section("Test Section", Icons.GEAR)
        
        # Should call print at least twice (header and underline)
        assert mock_print.call_count >= 2
    
    @patch('builtins.print')
    def test_print_success(self, mock_print):
        """Test success message printing"""
        print_success("Success message")
        
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert Icons.CHECK in args
        assert "Success message" in args
    
    @patch('builtins.print')
    def test_print_error(self, mock_print):
        """Test error message printing"""
        print_error("Error message")
        
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert Icons.CROSS in args
        assert "Error message" in args
    
    @patch('builtins.print')
    def test_print_warning(self, mock_print):
        """Test warning message printing"""
        print_warning("Warning message")
        
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert Icons.WARNING in args
        assert "Warning message" in args
    
    @patch('builtins.print')
    def test_print_info(self, mock_print):
        """Test info message printing"""
        print_info("Info message")
        
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert Icons.INFO in args
        assert "Info message" in args
    
    @patch('builtins.print')
    def test_print_step(self, mock_print):
        """Test step printing"""
        print_step(2, 5, "Step description")
        
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "[2/5]" in args
        assert "Step description" in args


class TestProgressBar:
    """Test cases for ProgressBar class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.progress_bar = ProgressBar(total=10, width=20)
    
    @patch('builtins.print')
    @patch('cli_interface.supports_color', return_value=True)
    def test_progress_bar_update(self, mock_supports_color, mock_print):
        """Test progress bar update"""
        self.progress_bar.update(5)
        
        mock_print.assert_called_once()
        output = mock_print.call_args[1]
        assert output['end'] == ''
        assert output['flush'] is True
    
    @patch('builtins.print')
    @patch('cli_interface.supports_color', return_value=False)
    def test_progress_bar_no_color(self, mock_supports_color, mock_print):
        """Test progress bar without color support"""
        self.progress_bar.update(5)
        
        mock_print.assert_not_called()
    
    @patch('builtins.print')
    @patch('cli_interface.supports_color', return_value=True)
    def test_progress_bar_completion(self, mock_supports_color, mock_print):
        """Test progress bar completion"""
        self.progress_bar.update(10)
        
        # Should call print twice - once for bar, once for newline
        assert mock_print.call_count == 2


class TestInteractivePrompts:
    """Test cases for InteractivePrompts class"""
    
    @patch('builtins.input', return_value='y')
    def test_yes_no_yes(self, mock_input):
        """Test yes/no prompt with yes response"""
        result = InteractivePrompts.yes_no("Test question?")
        assert result is True
    
    @patch('builtins.input', return_value='n')
    def test_yes_no_no(self, mock_input):
        """Test yes/no prompt with no response"""
        result = InteractivePrompts.yes_no("Test question?")
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_yes_no_default_true(self, mock_input):
        """Test yes/no prompt with empty input and default True"""
        result = InteractivePrompts.yes_no("Test question?", default=True)
        assert result is True
    
    @patch('builtins.input', return_value='')
    def test_yes_no_default_false(self, mock_input):
        """Test yes/no prompt with empty input and default False"""
        result = InteractivePrompts.yes_no("Test question?", default=False)
        assert result is False
    
    @patch('builtins.input', side_effect=['invalid', 'y'])
    @patch('cli_interface.print_warning')
    def test_yes_no_invalid_then_valid(self, mock_warning, mock_input):
        """Test yes/no prompt with invalid input followed by valid"""
        result = InteractivePrompts.yes_no("Test question?")
        
        assert result is True
        mock_warning.assert_called_once()
    
    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_select_option(self, mock_print, mock_input):
        """Test option selection"""
        options = ["Option 1", "Option 2", "Option 3"]
        result = InteractivePrompts.select_option("Choose:", options)
        
        assert result == 1  # Zero-indexed
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_select_option_default(self, mock_print, mock_input):
        """Test option selection with default"""
        options = ["Option 1", "Option 2", "Option 3"]
        result = InteractivePrompts.select_option("Choose:", options, default=2)
        
        assert result == 2
    
    @patch('builtins.input', side_effect=['5', '2'])
    @patch('builtins.print')
    @patch('cli_interface.print_warning')
    def test_select_option_invalid_then_valid(self, mock_warning, mock_print, mock_input):
        """Test option selection with invalid input followed by valid"""
        options = ["Option 1", "Option 2", "Option 3"]
        result = InteractivePrompts.select_option("Choose:", options)
        
        assert result == 1
        mock_warning.assert_called_once()
    
    @patch('builtins.input', return_value='Test input')
    def test_text_input(self, mock_input):
        """Test text input"""
        result = InteractivePrompts.text_input("Enter text:")
        assert result == "Test input"
    
    @patch('builtins.input', return_value='')
    def test_text_input_default(self, mock_input):
        """Test text input with default"""
        result = InteractivePrompts.text_input("Enter text:", default="default value")
        assert result == "default value"
    
    @patch('builtins.input', side_effect=['', 'Required input'])
    @patch('cli_interface.print_warning')
    def test_text_input_required(self, mock_warning, mock_input):
        """Test text input with required field"""
        result = InteractivePrompts.text_input("Enter text:", required=True)
        
        assert result == "Required input"
        mock_warning.assert_called_once()
    
    @patch('builtins.input', return_value='/path/to/file')
    @patch('os.path.exists', return_value=True)
    def test_path_input_exists(self, mock_exists, mock_input):
        """Test path input when path exists"""
        result = InteractivePrompts.path_input("Enter path:", must_exist=True)
        assert result == "/path/to/file"
    
    @patch('builtins.input', side_effect=['/nonexistent', '/valid/path'])
    @patch('os.path.exists', side_effect=[False, True])
    @patch('cli_interface.print_error')
    def test_path_input_must_exist(self, mock_error, mock_exists, mock_input):
        """Test path input when path must exist"""
        result = InteractivePrompts.path_input("Enter path:", must_exist=True)
        
        assert result == "/valid/path"
        mock_error.assert_called_once()


class TestWizardInterface:
    """Test cases for WizardInterface class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.wizard = WizardInterface()
    
    @pytest.mark.asyncio
    @patch.object(WizardInterface, '_step_environment_detection')
    @patch.object(WizardInterface, '_step_environment_analysis')
    @patch.object(WizardInterface, '_step_configuration_validation')
    @patch.object(WizardInterface, '_step_configuration_setup')
    @patch.object(WizardInterface, '_step_final_testing')
    @patch.object(WizardInterface, '_print_summary')
    @patch('cli_interface.print_header')
    @patch('builtins.print')
    async def test_run_complete_wizard(self, mock_print, mock_header, 
                                     mock_summary, mock_final, mock_setup, 
                                     mock_validation, mock_analysis, mock_detection):
        """Test complete wizard run"""
        await self.wizard.run()
        
        # Verify all steps were called
        mock_detection.assert_called_once()
        mock_analysis.assert_called_once()
        mock_validation.assert_called_once()
        mock_setup.assert_called_once()
        mock_final.assert_called_once()
        mock_summary.assert_called_once()
        mock_header.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('cli_interface.print_warning')
    async def test_run_keyboard_interrupt(self, mock_warning):
        """Test wizard run with keyboard interrupt"""
        with patch.object(self.wizard, '_step_environment_detection', 
                         side_effect=KeyboardInterrupt):
            await self.wizard.run()
            
            mock_warning.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('cli_interface.print_error')
    async def test_run_unexpected_error(self, mock_error):
        """Test wizard run with unexpected error"""
        with patch.object(self.wizard, '_step_environment_detection', 
                         side_effect=Exception("Test error")):
            await self.wizard.run()
            
            mock_error.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('environment_detector.EnvironmentDetector')
    @patch('cli_interface.print_step')
    @patch('cli_interface.print_success')
    async def test_step_environment_detection(self, mock_success, mock_step, mock_detector):
        """Test environment detection step"""
        # Mock environment detector
        mock_env = Mock()
        mock_env.os_type.value = 'macos'
        mock_env.os_version = 'macOS-12.0'
        mock_env.python_env.version = '3.9.0'
        mock_env.python_env.is_virtual_env = True
        mock_env.llm_clients = []
        mock_env.mcp_installation.is_installed = False
        
        mock_detector_instance = Mock()
        mock_detector_instance.detect_full_environment.return_value = mock_env
        mock_detector.return_value = mock_detector_instance
        
        await self.wizard._step_environment_detection()
        
        assert self.wizard.environment == mock_env
        mock_step.assert_called_once()
        mock_success.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('environment_detector.EnvironmentAnalyzer')
    @patch('cli_interface.print_step')
    async def test_step_environment_analysis(self, mock_step, mock_analyzer):
        """Test environment analysis step"""
        # Setup mock environment
        self.wizard.environment = Mock()
        
        # Setup mock analyzer
        mock_analyzer_instance = Mock()
        mock_analysis = {
            'compatibility_score': 85,
            'requirements_met': ['Python 3.8+'],
            'missing_requirements': ['MCP library'],
            'issues': [],
            'recommendations': ['Install MCP library']
        }
        mock_analyzer_instance.analyze_compatibility.return_value = mock_analysis
        mock_analyzer.return_value = mock_analyzer_instance
        
        with patch('builtins.print'):
            with patch('cli_interface.print_success'):
                with patch('cli_interface.print_warning'):
                    with patch('cli_interface.print_info'):
                        await self.wizard._step_environment_analysis()
        
        mock_step.assert_called_once()
        mock_analyzer.assert_called_once_with(self.wizard.environment)
    
    @pytest.mark.asyncio
    @patch('config_validator.ConfigurationValidator')
    @patch('cli_interface.print_step')
    @patch('cli_interface.InteractivePrompts')
    async def test_step_configuration_validation_no_clients(self, mock_prompts, mock_step, mock_validator):
        """Test configuration validation step with no LLM clients"""
        self.wizard.environment = Mock()
        self.wizard.environment.llm_clients = []
        
        mock_prompts.yes_no.return_value = False
        
        with patch('cli_interface.print_warning'):
            with patch('cli_interface.print_info'):
                await self.wizard._step_configuration_validation()
        
        mock_step.assert_called_once()
        mock_prompts.yes_no.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('cli_interface.print_step')
    async def test_step_configuration_setup_no_configs(self, mock_step):
        """Test configuration setup step with no configurations"""
        self.wizard.configurations = []
        
        with patch('cli_interface.print_info') as mock_info:
            await self.wizard._step_configuration_setup()
            
            mock_step.assert_called_once()
            mock_info.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('cli_interface.print_step')
    async def test_step_final_testing_no_validator(self, mock_step):
        """Test final testing step with no validator"""
        self.wizard.validator = None
        
        with patch('cli_interface.print_info') as mock_info:
            await self.wizard._step_final_testing()
            
            mock_step.assert_called_once()
            mock_info.assert_called_once()
    
    @patch('cli_interface.print_header')
    @patch('builtins.print')
    def test_print_summary(self, mock_print, mock_header):
        """Test summary printing"""
        self.wizard.environment = Mock()
        self.wizard.environment.os_type.value = 'macos'
        self.wizard.environment.python_env.version = '3.9.0'
        self.wizard.environment.mcp_installation.is_installed = True
        
        self.wizard.configurations = []
        
        self.wizard._print_summary()
        
        mock_header.assert_called_once()
        assert mock_print.call_count > 0
    
    def test_get_default_claude_config_path_macos(self):
        """Test getting default Claude config path on macOS"""
        self.wizard.environment = Mock()
        self.wizard.environment.os_type.value = 'macos'
        
        path = self.wizard._get_default_claude_config_path()
        
        assert "Library/Application Support/Claude" in path
    
    def test_show_validation_details(self):
        """Test showing validation details"""
        from config_validator import ValidationResult, ValidationStatus
        
        mock_config = Mock()
        mock_config.validation_results = [
            ValidationResult("test1", ValidationStatus.VALID, "Valid test"),
            ValidationResult("test2", ValidationStatus.ERROR, "Error test", fix_suggestion="Fix it"),
            ValidationResult("test3", ValidationStatus.WARNING, "Warning test")
        ]
        
        with patch('builtins.print') as mock_print:
            self.wizard._show_validation_details(mock_config)
            
            # Should print details for all validation results
            assert mock_print.call_count >= 3


if __name__ == '__main__':
    pytest.main([__file__])