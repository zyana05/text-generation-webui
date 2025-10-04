"""
Tools Agent for MAX System
Manages Git, linters, and other development tools
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from modules.logging_colors import logger


class ToolsAgent:
    """Manages development tools and utilities"""
    
    def __init__(self, config):
        self.config = config
        self.auto_commit = config['git'].get('auto_commit', True)
        self.commit_prefix = config['git'].get('commit_prefix', '[MAX]')
    
    # Git operations
    def git_init(self, project_dir: Path) -> Dict[str, Any]:
        """Initialize git repository"""
        result = {'success': False, 'output': '', 'error': ''}
        
        try:
            process = subprocess.run(
                ['git', 'init'],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            
            result['success'] = process.returncode == 0
            result['output'] = process.stdout
            result['error'] = process.stderr
            
            if result['success']:
                logger.info(f"MAX System: Initialized git in {project_dir}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"MAX System: Git init failed - {e}")
        
        return result
    
    def git_add(self, project_dir: Path, files: List[str] = None) -> Dict[str, Any]:
        """Add files to git"""
        result = {'success': False, 'output': '', 'error': ''}
        
        try:
            cmd = ['git', 'add']
            if files:
                cmd.extend(files)
            else:
                cmd.append('.')
            
            process = subprocess.run(
                cmd,
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            
            result['success'] = process.returncode == 0
            result['output'] = process.stdout
            result['error'] = process.stderr
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def git_commit(self, project_dir: Path, message: str) -> Dict[str, Any]:
        """Commit changes"""
        result = {'success': False, 'output': '', 'error': ''}
        
        if not self.auto_commit:
            result['error'] = "Auto-commit is disabled"
            return result
        
        try:
            full_message = f"{self.commit_prefix} {message}"
            
            process = subprocess.run(
                ['git', 'commit', '-m', full_message],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            
            result['success'] = process.returncode == 0
            result['output'] = process.stdout
            result['error'] = process.stderr
            
            if result['success']:
                logger.info(f"MAX System: Committed - {message}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"MAX System: Git commit failed - {e}")
        
        return result
    
    def git_status(self, project_dir: Path) -> Dict[str, Any]:
        """Get git status"""
        result = {'success': False, 'output': '', 'error': '', 'has_changes': False}
        
        try:
            process = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=project_dir,
                capture_output=True,
                text=True
            )
            
            result['success'] = process.returncode == 0
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['has_changes'] = bool(process.stdout.strip())
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def git_commit_step(self, project_dir: Path, step_number: int, description: str):
        """Auto-commit a completed step"""
        if not self.auto_commit:
            return
        
        # Add all changes
        self.git_add(project_dir)
        
        # Check if there are changes
        status = self.git_status(project_dir)
        if not status.get('has_changes', False):
            logger.info("MAX System: No changes to commit")
            return
        
        # Commit
        message = f"Step {step_number}: {description}"
        self.git_commit(project_dir, message)
    
    # Linting tools
    def run_pylint(self, file_path: Path) -> Dict[str, Any]:
        """Run pylint on a file"""
        result = {'success': False, 'output': '', 'error': '', 'score': None}
        
        try:
            process = subprocess.run(
                ['python', '-m', 'pylint', str(file_path), '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            
            # Parse JSON output
            if process.stdout:
                try:
                    lint_results = json.loads(process.stdout)
                    result['issues'] = lint_results
                    result['success'] = True
                except json.JSONDecodeError:
                    result['output'] = process.stdout
            
        except subprocess.TimeoutExpired:
            result['error'] = "Pylint timed out"
        except FileNotFoundError:
            result['error'] = "Pylint not installed"
            logger.warning("MAX System: pylint not available")
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def run_flake8(self, file_path: Path) -> Dict[str, Any]:
        """Run flake8 on a file"""
        result = {'success': False, 'output': '', 'error': '', 'issues': []}
        
        try:
            process = subprocess.run(
                ['python', '-m', 'flake8', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            
            # Parse output
            if process.stdout:
                for line in process.stdout.split('\n'):
                    if line.strip():
                        result['issues'].append(line)
            
        except FileNotFoundError:
            result['error'] = "Flake8 not installed"
            logger.warning("MAX System: flake8 not available")
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def run_black(self, file_path: Path, check_only: bool = False) -> Dict[str, Any]:
        """Run black formatter"""
        result = {'success': False, 'output': '', 'error': '', 'would_reformat': False}
        
        try:
            cmd = ['python', '-m', 'black', str(file_path)]
            if check_only:
                cmd.append('--check')
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            result['output'] = process.stdout
            result['error'] = process.stderr
            result['success'] = process.returncode == 0
            result['would_reformat'] = process.returncode != 0 and check_only
            
            if result['success'] and not check_only:
                logger.info(f"MAX System: Formatted {file_path.name} with black")
        
        except FileNotFoundError:
            result['error'] = "Black not installed"
            logger.warning("MAX System: black not available")
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def check_code_quality(self, file_path: Path) -> Dict[str, Any]:
        """Run multiple code quality checks"""
        result = {
            'success': True,
            'checks': {},
            'summary': {
                'total_issues': 0,
                'critical_issues': 0
            }
        }
        
        # Try flake8
        flake8_result = self.run_flake8(file_path)
        result['checks']['flake8'] = flake8_result
        if flake8_result.get('issues'):
            result['summary']['total_issues'] += len(flake8_result['issues'])
        
        # Try black check
        black_result = self.run_black(file_path, check_only=True)
        result['checks']['black'] = black_result
        if black_result.get('would_reformat'):
            result['summary']['total_issues'] += 1
        
        result['success'] = result['summary']['total_issues'] == 0
        
        return result
    
    def format_code(self, file_path: Path) -> Dict[str, Any]:
        """Format code with available formatters"""
        result = {'success': False, 'formatted': False}
        
        # Try black
        black_result = self.run_black(file_path, check_only=False)
        if black_result['success']:
            result['success'] = True
            result['formatted'] = True
            result['formatter'] = 'black'
        
        return result
    
    # File operations
    def create_readme(self, project_dir: Path, content: str) -> Path:
        """Create README file"""
        readme_path = project_dir / 'README.md'
        readme_path.write_text(content, encoding='utf-8')
        logger.info(f"MAX System: Created README.md")
        return readme_path
    
    def create_requirements_txt(self, project_dir: Path, packages: List[str]) -> Path:
        """Create requirements.txt"""
        req_path = project_dir / 'requirements.txt'
        req_path.write_text('\n'.join(packages), encoding='utf-8')
        logger.info(f"MAX System: Created requirements.txt with {len(packages)} packages")
        return req_path
    
    def create_gitignore(self, project_dir: Path) -> Path:
        """Create .gitignore file"""
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Tests
.pytest_cache/
.coverage
htmlcov/

# Logs
*.log
"""
        gitignore_path = project_dir / '.gitignore'
        gitignore_path.write_text(gitignore_content, encoding='utf-8')
        logger.info(f"MAX System: Created .gitignore")
        return gitignore_path
    
    def analyze_dependencies(self, code: str) -> List[str]:
        """Analyze code to extract dependencies"""
        dependencies = set()
        
        import_lines = [line for line in code.split('\n') if line.strip().startswith(('import ', 'from '))]
        
        for line in import_lines:
            # Extract module name
            if line.strip().startswith('import '):
                module = line.strip()[7:].split()[0].split('.')[0]
                dependencies.add(module)
            elif line.strip().startswith('from '):
                module = line.strip()[5:].split()[0].split('.')[0]
                dependencies.add(module)
        
        # Filter out standard library modules
        stdlib_modules = {'os', 'sys', 'json', 'time', 'datetime', 're', 'math', 'random', 
                          'collections', 'itertools', 'functools', 'pathlib', 'io', 'typing'}
        
        external_deps = [dep for dep in dependencies if dep not in stdlib_modules]
        
        return external_deps
