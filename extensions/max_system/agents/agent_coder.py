"""
Coder Agent for MAX System
Generates code based on task descriptions
"""

import re
from typing import Dict, Any, Optional
from modules.logging_colors import logger


class CoderAgent:
    """Generates and manages code"""
    
    def __init__(self, llm_wrapper, memory_agent, config):
        self.llm = llm_wrapper
        self.memory = memory_agent
        self.config = config
        self.max_code_length = config['agents']['coder'].get('max_code_length', 8000)
        self.add_tests = config['agents']['coder'].get('add_tests', True)
        self.add_documentation = config['agents']['coder'].get('add_documentation', True)
    
    def generate_code(self, step_description: str, context: str = "", language: str = "python") -> Dict[str, Any]:
        """
        Generate code for a step
        
        Args:
            step_description: Description of what the code should do
            context: Additional context (previous steps, etc.)
            language: Programming language
            
        Returns:
            Dictionary with 'code', 'language', 'description'
        """
        logger.info(f"MAX System: Generating code for - {step_description[:50]}...")
        
        # Build context from similar past experiences
        similar = self.memory.get_similar_experiences(step_description, limit=2)
        experience_context = ""
        if similar:
            experience_context = "\n\nRelevant past patterns:\n"
            for exp in similar:
                experience_context += f"- {exp['pattern']}\n"
        
        full_context = context + experience_context
        
        # Generate code
        code = self.llm.generate_code(step_description, language, full_context)
        
        # Clean code
        code = self._extract_code(code)
        
        if len(code) > self.max_code_length:
            logger.warning(f"MAX System: Generated code exceeds max length ({len(code)} > {self.max_code_length})")
            code = code[:self.max_code_length]
        
        result = {
            'code': code,
            'language': language,
            'description': step_description,
            'has_tests': False,
            'has_docs': bool(re.search(r'""".*?"""', code, re.DOTALL))
        }
        
        logger.info(f"MAX System: Generated {len(code)} characters of {language} code")
        return result
    
    def _extract_code(self, text: str) -> str:
        """
        Extract code from LLM response
        
        Args:
            text: LLM response text
            
        Returns:
            Extracted code
        """
        # Look for code blocks
        code_block_pattern = r'```(?:python|py)?\n(.*?)```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            # Return the last code block (most complete)
            return matches[-1].strip()
        
        # If no code blocks, check if the entire response looks like code
        lines = text.split('\n')
        code_indicators = ['def ', 'class ', 'import ', 'from ', '    ', '\t']
        
        code_lines = sum(1 for line in lines if any(line.strip().startswith(ind) for ind in code_indicators))
        
        if code_lines > len(lines) * 0.3:  # 30% of lines look like code
            return text.strip()
        
        # Default: return as is
        return text.strip()
    
    def generate_tests(self, code: str, description: str) -> str:
        """
        Generate unit tests for code
        
        Args:
            code: Code to test
            description: Description of what the code does
            
        Returns:
            Test code
        """
        if not self.add_tests:
            return ""
        
        system_prompt = """You are an expert at writing Python unit tests using pytest.
Generate comprehensive test cases that cover normal cases, edge cases, and error handling."""
        
        user_prompt = f"""Generate pytest unit tests for the following code:

```python
{code}
```

Description: {description}

Generate comprehensive tests. Include fixtures if needed.
Respond with ONLY the test code, no explanations."""
        
        tests = self.llm.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=2048)
        return self._extract_code(tests)
    
    def add_documentation(self, code: str, description: str) -> str:
        """
        Add or improve documentation in code
        
        Args:
            code: Code to document
            description: Description of what the code does
            
        Returns:
            Documented code
        """
        if not self.add_documentation:
            return code
        
        system_prompt = """You are an expert at writing clear, comprehensive Python documentation.
Add docstrings following Google style guide."""
        
        user_prompt = f"""Add comprehensive docstrings to this code:

```python
{code}
```

Description: {description}

Add module docstring, function/class docstrings with Args, Returns, Raises sections.
Respond with ONLY the documented code, no explanations."""
        
        documented = self.llm.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=3072)
        return self._extract_code(documented)
    
    def refactor_code(self, code: str, reason: str) -> str:
        """
        Refactor code for improvement
        
        Args:
            code: Code to refactor
            reason: Reason for refactoring
            
        Returns:
            Refactored code
        """
        system_prompt = """You are an expert at refactoring Python code.
Improve code quality while maintaining functionality."""
        
        user_prompt = f"""Refactor this code: {reason}

```python
{code}
```

Maintain all functionality while improving the code.
Respond with ONLY the refactored code, no explanations."""
        
        refactored = self.llm.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=3072)
        return self._extract_code(refactored)
    
    def combine_code_blocks(self, code_blocks: list[str]) -> str:
        """
        Combine multiple code blocks into a cohesive module
        
        Args:
            code_blocks: List of code strings
            
        Returns:
            Combined code
        """
        # Simple combination with separators
        combined = "\n\n# " + "=" * 70 + "\n\n"
        combined = combined.join(code_blocks)
        
        # Could be enhanced to:
        # - Deduplicate imports
        # - Organize functions/classes
        # - Add module-level docstring
        
        return combined
    
    def validate_syntax(self, code: str, language: str = "python") -> tuple[bool, Optional[str]]:
        """
        Validate code syntax
        
        Args:
            code: Code to validate
            language: Programming language
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if language != "python":
            return True, None  # Only validate Python for now
        
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    def extract_imports(self, code: str) -> list[str]:
        """
        Extract import statements from code
        
        Args:
            code: Python code
            
        Returns:
            List of imported modules
        """
        imports = []
        
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        
        return imports
    
    def analyze_code_structure(self, code: str) -> Dict[str, Any]:
        """
        Analyze code structure
        
        Args:
            code: Python code
            
        Returns:
            Dictionary with structure info
        """
        structure = {
            'functions': [],
            'classes': [],
            'imports': [],
            'lines': len(code.split('\n')),
            'has_main': '__name__' in code and '__main__' in code
        }
        
        # Extract functions
        func_pattern = r'def\s+(\w+)\s*\('
        structure['functions'] = re.findall(func_pattern, code)
        
        # Extract classes
        class_pattern = r'class\s+(\w+)\s*[:\(]'
        structure['classes'] = re.findall(class_pattern, code)
        
        # Extract imports
        structure['imports'] = self.extract_imports(code)
        
        return structure
