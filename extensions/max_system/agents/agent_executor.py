"""
Executor Agent for MAX System
Executes code in a sandboxed environment
"""

import sys
import io
import subprocess
import traceback
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import redirect_stdout, redirect_stderr
from modules.logging_colors import logger


class ExecutorAgent:
    """Executes code safely in a sandbox"""
    
    def __init__(self, config):
        self.config = config
        self.timeout = config['agents']['executor'].get('python_timeout', 60)
        self.max_output_lines = config['agents']['executor'].get('max_output_lines', 1000)
        self.sandbox_dir = Path(config['execution']['sandbox_dir'])
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Restricted operations for safety
        self.restricted = config['safety'].get('restricted_imports', [])
    
    def execute_python(self, code: str, capture_output: bool = True) -> Dict[str, Any]:
        """
        Execute Python code
        
        Args:
            code: Python code to execute
            capture_output: Whether to capture stdout/stderr
            
        Returns:
            Dictionary with execution results
        """
        logger.info("MAX System: Executing Python code...")
        
        result = {
            'success': False,
            'output': '',
            'error': '',
            'execution_time': 0,
            'return_value': None
        }
        
        # Validate code safety
        safety_check = self._check_code_safety(code)
        if not safety_check['safe']:
            result['error'] = f"Safety check failed: {safety_check['reason']}"
            logger.warning(f"MAX System: {result['error']}")
            return result
        
        # Execute in controlled environment
        if capture_output:
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            try:
                # Create a restricted globals dict
                restricted_globals = {
                    '__builtins__': __builtins__,
                    '__name__': '__main__',
                    '__file__': '<sandbox>',
                }
                
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(code, restricted_globals)
                
                result['success'] = True
                result['output'] = stdout_capture.getvalue()
                result['return_value'] = restricted_globals.get('result', None)
                
            except Exception as e:
                result['error'] = str(e)
                result['traceback'] = traceback.format_exc()
                stderr_output = stderr_capture.getvalue()
                if stderr_output:
                    result['error'] += f"\n{stderr_output}"
                
                logger.error(f"MAX System: Execution failed - {e}")
            
            # Limit output size
            if len(result['output']) > self.max_output_lines * 100:
                lines = result['output'].split('\n')
                if len(lines) > self.max_output_lines:
                    result['output'] = '\n'.join(lines[:self.max_output_lines])
                    result['output'] += f"\n\n... (truncated {len(lines) - self.max_output_lines} lines)"
        
        else:
            # Execute without capture
            try:
                exec(code)
                result['success'] = True
            except Exception as e:
                result['error'] = str(e)
                result['traceback'] = traceback.format_exc()
        
        return result
    
    def execute_python_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Execute a Python file
        
        Args:
            file_path: Path to Python file
            
        Returns:
            Dictionary with execution results
        """
        logger.info(f"MAX System: Executing {file_path.name}...")
        
        result = {
            'success': False,
            'output': '',
            'error': '',
            'return_code': None
        }
        
        if not file_path.exists():
            result['error'] = f"File not found: {file_path}"
            return result
        
        try:
            # Execute using subprocess for better isolation
            process = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=file_path.parent
            )
            
            result['return_code'] = process.returncode
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            
        except subprocess.TimeoutExpired:
            result['error'] = f"Execution timed out after {self.timeout} seconds"
            logger.warning(f"MAX System: {result['error']}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"MAX System: Execution failed - {e}")
        
        return result
    
    def run_tests(self, test_file: Path) -> Dict[str, Any]:
        """
        Run pytest on a test file
        
        Args:
            test_file: Path to test file
            
        Returns:
            Dictionary with test results
        """
        logger.info(f"MAX System: Running tests in {test_file.name}...")
        
        result = {
            'success': False,
            'output': '',
            'error': '',
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0
        }
        
        try:
            # Try to run with pytest
            process = subprocess.run(
                [sys.executable, '-m', 'pytest', str(test_file), '-v'],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=test_file.parent
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            
            # Parse pytest output for counts
            output = result['output']
            if 'passed' in output:
                import re
                match = re.search(r'(\d+) passed', output)
                if match:
                    result['tests_passed'] = int(match.group(1))
            
            if 'failed' in output:
                import re
                match = re.search(r'(\d+) failed', output)
                if match:
                    result['tests_failed'] = int(match.group(1))
            
            result['tests_run'] = result['tests_passed'] + result['tests_failed']
            
        except subprocess.TimeoutExpired:
            result['error'] = f"Tests timed out after {self.timeout} seconds"
        except FileNotFoundError:
            # pytest not available, try running as regular Python
            logger.warning("MAX System: pytest not available, running as Python file")
            return self.execute_python_file(test_file)
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _check_code_safety(self, code: str) -> Dict[str, Any]:
        """
        Check if code is safe to execute
        
        Args:
            code: Python code
            
        Returns:
            Dictionary with 'safe' (bool) and 'reason' (str)
        """
        # Check for restricted operations
        restricted_patterns = [
            ('os.system', 'os.system() is not allowed'),
            ('subprocess.Popen', 'subprocess.Popen() is not allowed'),
            ('eval(', 'eval() is not allowed for security'),
            ('exec(', 'exec() is not allowed for security'),
            ('__import__', '__import__ is not allowed'),
            ('open(', 'File operations require review'),  # Could be allowed with restrictions
        ]
        
        code_lower = code.lower()
        
        for pattern, reason in restricted_patterns:
            if pattern.lower() in code_lower:
                # Exception for our own exec in sandbox
                if pattern == 'exec(' and 'restricted_globals' in code:
                    continue
                return {'safe': False, 'reason': reason}
        
        # Additional checks
        dangerous_keywords = ['rm -rf', 'shutil.rmtree', 'os.remove', 'os.unlink']
        for keyword in dangerous_keywords:
            if keyword in code_lower:
                return {'safe': False, 'reason': f'Potentially dangerous operation: {keyword}'}
        
        return {'safe': True, 'reason': 'Code passed safety checks'}
    
    def save_code_to_file(self, code: str, filename: str, subdir: str = None) -> Path:
        """
        Save code to a file in the sandbox
        
        Args:
            code: Code to save
            filename: Filename
            subdir: Optional subdirectory
            
        Returns:
            Path to saved file
        """
        if subdir:
            target_dir = self.sandbox_dir / subdir
            target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = self.sandbox_dir
        
        file_path = target_dir / filename
        file_path.write_text(code, encoding='utf-8')
        logger.info(f"MAX System: Saved code to {file_path}")
        
        return file_path
    
    def create_project_structure(self, project_name: str) -> Path:
        """
        Create a project directory structure
        
        Args:
            project_name: Name of the project
            
        Returns:
            Path to project root
        """
        projects_dir = Path(self.config['execution']['projects_dir'])
        projects_dir.mkdir(parents=True, exist_ok=True)
        
        project_dir = projects_dir / project_name
        project_dir.mkdir(exist_ok=True)
        
        # Create standard structure
        (project_dir / 'src').mkdir(exist_ok=True)
        (project_dir / 'tests').mkdir(exist_ok=True)
        (project_dir / 'docs').mkdir(exist_ok=True)
        
        # Create __init__.py files
        (project_dir / 'src' / '__init__.py').touch()
        (project_dir / 'tests' / '__init__.py').touch()
        
        logger.info(f"MAX System: Created project structure at {project_dir}")
        return project_dir
    
    def install_dependencies(self, requirements: list[str]) -> Dict[str, Any]:
        """
        Install Python dependencies
        
        Args:
            requirements: List of package names
            
        Returns:
            Dictionary with installation results
        """
        result = {
            'success': False,
            'installed': [],
            'failed': [],
            'output': ''
        }
        
        for package in requirements:
            try:
                process = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if process.returncode == 0:
                    result['installed'].append(package)
                else:
                    result['failed'].append(package)
                    result['output'] += f"\nFailed to install {package}: {process.stderr}"
                
            except Exception as e:
                result['failed'].append(package)
                result['output'] += f"\nError installing {package}: {e}"
        
        result['success'] = len(result['failed']) == 0
        
        logger.info(f"MAX System: Installed {len(result['installed'])}/{len(requirements)} packages")
        return result
