"""
Module Sandbox for Proyecto Semilla
Provides isolated execution environment for modules
"""

import asyncio
import sys
import os
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
import resource
import signal
import threading
from contextlib import contextmanager


class ModuleSandbox:
    """
    Sandbox environment for safe module execution
    """

    def __init__(self):
        self.active_sandboxes: Dict[str, 'SandboxEnvironment'] = {}
        self.resource_limits = {
            'cpu_time': 300,  # 5 minutes
            'memory': 100 * 1024 * 1024,  # 100MB
            'file_descriptors': 50
        }

    @contextmanager
    def create_sandbox(self, module_name: str, module_path: Path):
        """
        Create a sandboxed environment for module execution
        """
        sandbox = SandboxEnvironment(module_name, module_path, self.resource_limits)
        self.active_sandboxes[module_name] = sandbox

        try:
            with sandbox:
                yield sandbox
        finally:
            if module_name in self.active_sandboxes:
                del self.active_sandboxes[module_name]

    def get_sandbox(self, module_name: str) -> Optional['SandboxEnvironment']:
        """
        Get active sandbox for a module
        """
        return self.active_sandboxes.get(module_name)

    def terminate_sandbox(self, module_name: str) -> bool:
        """
        Forcefully terminate a sandbox
        """
        sandbox = self.active_sandboxes.get(module_name)
        if sandbox:
            sandbox.terminate()
            del self.active_sandboxes[module_name]
            return True
        return False

    def list_active_sandboxes(self) -> List[str]:
        """
        List all active sandboxes
        """
        return list(self.active_sandboxes.keys())

    def get_sandbox_stats(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a sandbox
        """
        sandbox = self.active_sandboxes.get(module_name)
        if sandbox:
            return sandbox.get_stats()
        return None


class SandboxEnvironment:
    """
    Isolated execution environment for a single module
    """

    def __init__(self, module_name: str, module_path: Path, resource_limits: Dict[str, Any]):
        self.module_name = module_name
        self.module_path = module_path
        self.resource_limits = resource_limits

        # Execution state
        self.process = None
        self.thread = None
        self.is_active = False

        # Resource tracking
        self.start_time = None
        self.memory_usage = 0
        self.cpu_usage = 0

        # Allowed modules and functions
        self.allowed_modules = self._get_allowed_modules()
        self.allowed_builtins = self._get_allowed_builtins()

        # Security restrictions
        self.forbidden_operations = {
            'eval', 'exec', 'compile', '__import__',
            'open', 'file', 'input', 'raw_input'
        }

    def __enter__(self):
        """Enter sandbox context"""
        self.is_active = True
        self.start_time = asyncio.get_event_loop().time()
        self._setup_resource_limits()
        self._setup_signal_handlers()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit sandbox context"""
        self.is_active = False
        self._cleanup()

    def _setup_resource_limits(self):
        """Set up resource limits for the sandbox"""
        try:
            # Set CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU,
                             (self.resource_limits['cpu_time'], self.resource_limits['cpu_time']))

            # Set memory limit
            resource.setrlimit(resource.RLIMIT_AS,
                             (self.resource_limits['memory'], self.resource_limits['memory']))

            # Set file descriptor limit
            resource.setrlimit(resource.RLIMIT_NOFILE,
                             (self.resource_limits['file_descriptors'], self.resource_limits['file_descriptors']))

        except Exception as e:
            print(f"Failed to set resource limits for {self.module_name}: {e}")

    def _setup_signal_handlers(self):
        """Set up signal handlers for timeout and termination"""
        def timeout_handler(signum, frame):
            print(f"Module {self.module_name} timed out")
            self.terminate()

        def termination_handler(signum, frame):
            print(f"Module {self.module_name} terminated")
            self.terminate()

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.signal(signal.SIGTERM, termination_handler)

        # Set alarm for CPU timeout
        signal.alarm(self.resource_limits['cpu_time'])

    def _cleanup(self):
        """Clean up sandbox resources"""
        try:
            # Cancel alarm
            signal.alarm(0)

            # Terminate any running processes
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except:
                    self.process.kill()

            # Clean up thread
            if self.thread and self.thread.is_alive():
                # Note: In a real implementation, you'd need a way to terminate threads safely
                pass

        except Exception as e:
            print(f"Error during sandbox cleanup for {self.module_name}: {e}")

    def terminate(self):
        """Forcefully terminate the sandbox"""
        self.is_active = False
        self._cleanup()

    def execute_code(self, code: str, globals_dict: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute code within the sandbox
        """
        if not self.is_active:
            raise RuntimeError("Sandbox is not active")

        # Create restricted globals
        restricted_globals = self._create_restricted_globals(globals_dict or {})

        try:
            # Execute code with restrictions
            result = self._execute_with_restrictions(code, restricted_globals)
            return result

        except Exception as e:
            print(f"Error executing code in sandbox {self.module_name}: {e}")
            raise

    def _create_restricted_globals(self, user_globals: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create restricted global namespace
        """
        # Start with allowed builtins
        restricted_globals = {
            '__builtins__': self.allowed_builtins,
            '__name__': f'sandbox_{self.module_name}',
            '__doc__': None,
            '__package__': None,
            '__loader__': None,
            '__spec__': None,
            '__annotations__': {},
            '__file__': f'<sandbox:{self.module_name}>',
        }

        # Add allowed modules
        for module_name in self.allowed_modules:
            try:
                __import__(module_name)
                restricted_globals[module_name] = sys.modules[module_name]
            except ImportError:
                pass  # Module not available, skip

        # Add user globals (with restrictions)
        for key, value in user_globals.items():
            if not self._is_forbidden_name(key):
                restricted_globals[key] = value

        return restricted_globals

    def _execute_with_restrictions(self, code: str, globals_dict: Dict[str, Any]) -> Any:
        """
        Execute code with security restrictions
        """
        # Check for forbidden operations
        if any(op in code for op in self.forbidden_operations):
            raise SecurityError(f"Forbidden operation detected in code for {self.module_name}")

        # Execute in restricted environment
        try:
            # Compile code to check for syntax errors
            compiled_code = compile(code, f'<sandbox:{self.module_name}>', 'exec')

            # Execute with timeout and resource monitoring
            result = None
            exec(compiled_code, globals_dict)

            # Get result if it's an expression
            if 'result' in globals_dict:
                result = globals_dict['result']

            return result

        except SyntaxError as e:
            raise ValueError(f"Syntax error in {self.module_name}: {e}")
        except Exception as e:
            raise RuntimeError(f"Execution error in {self.module_name}: {e}")

    def _is_forbidden_name(self, name: str) -> bool:
        """
        Check if a name is forbidden
        """
        forbidden_names = {
            '__builtins__', '__import__', 'eval', 'exec', 'compile',
            'open', 'file', 'input', 'raw_input', 'reload',
            'sys', 'os', 'subprocess', 'multiprocessing'
        }
        return name in forbidden_names

    def _get_allowed_modules(self) -> Set[str]:
        """
        Get list of allowed modules for sandbox
        """
        return {
            'asyncio', 'json', 'datetime', 'time', 'math', 'random',
            'collections', 'itertools', 'functools', 'operator',
            'typing', 'enum', 'dataclasses', 'uuid',
            'urllib.parse', 'base64', 'hashlib', 'hmac',
            're', 'string', 'unicodedata'
        }

    def _get_allowed_builtins(self) -> Dict[str, Any]:
        """
        Get allowed builtin functions
        """
        import builtins

        # Start with safe builtins
        safe_builtins = {}

        # Whitelist of safe builtin functions
        safe_builtin_names = {
            'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes',
            'callable', 'chr', 'classmethod', 'complex', 'delattr', 'dict',
            'dir', 'divmod', 'enumerate', 'filter', 'float', 'format', 'frozenset',
            'getattr', 'hasattr', 'hash', 'help', 'hex', 'id', 'int', 'isinstance',
            'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max', 'memoryview',
            'min', 'next', 'object', 'oct', 'ord', 'pow', 'print', 'property',
            'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
            'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
            'vars', 'zip'
        }

        for name in safe_builtin_names:
            if hasattr(builtins, name):
                safe_builtins[name] = getattr(builtins, name)

        # Add safe exceptions
        safe_exceptions = {
            'ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException',
            'BufferError', 'BytesWarning', 'DeprecationWarning', 'EOFError',
            'EnvironmentError', 'Exception', 'FloatingPointError', 'FutureWarning',
            'GeneratorExit', 'ImportError', 'ImportWarning', 'IndentationError',
            'IndexError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
            'MemoryError', 'NameError', 'NotImplementedError', 'OSError',
            'OverflowError', 'PendingDeprecationWarning', 'ReferenceError',
            'ResourceWarning', 'RuntimeError', 'RuntimeWarning', 'StopAsyncIteration',
            'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
            'SystemExit', 'TabError', 'TimeoutError', 'TypeError', 'UnboundLocalError',
            'UnicodeDecodeError', 'UnicodeEncodeError', 'UnicodeError', 'UnicodeTranslateError',
            'UnicodeWarning', 'UserWarning', 'ValueError', 'Warning', 'ZeroDivisionError'
        }

        for exc_name in safe_exceptions:
            if hasattr(builtins, exc_name):
                safe_builtins[exc_name] = getattr(builtins, exc_name)

        return safe_builtins

    def get_stats(self) -> Dict[str, Any]:
        """
        Get sandbox statistics
        """
        current_time = asyncio.get_event_loop().time()
        runtime = current_time - (self.start_time or current_time)

        return {
            'module_name': self.module_name,
            'is_active': self.is_active,
            'runtime_seconds': runtime,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage,
            'resource_limits': self.resource_limits
        }


class SecurityError(Exception):
    """Security violation in sandbox"""
    pass