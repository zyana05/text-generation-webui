"""
Reflex Agent for MAX System
Analyzes errors and implements fixes autonomously
"""

import re
from typing import Dict, Any, Optional
from modules.logging_colors import logger


class ReflexAgent:
    """Analyzes failures and generates fixes"""
    
    def __init__(self, llm_wrapper, memory_agent, config):
        self.llm = llm_wrapper
        self.memory = memory_agent
        self.config = config
        self.max_fix_attempts = config['agents']['reflex'].get('max_fix_attempts', 3)
    
    def analyze_error(self, code: str, error: str, traceback: str = "") -> Dict[str, Any]:
        """
        Analyze an execution error
        
        Args:
            code: Code that failed
            error: Error message
            traceback: Full traceback
            
        Returns:
            Dictionary with analysis results
        """
        logger.info("MAX System: Analyzing error...")
        
        # Check for similar past errors
        error_type = self._classify_error(error)
        
        # Get LLM analysis
        analysis_text = self.llm.analyze_error(code, error, traceback)
        
        # Parse analysis
        analysis = self._parse_analysis(analysis_text)
        analysis['error_type'] = error_type
        analysis['original_code'] = code
        analysis['original_error'] = error
        
        logger.info(f"MAX System: Error classified as {error_type}")
        return analysis
    
    def _classify_error(self, error: str) -> str:
        """
        Classify error type
        
        Args:
            error: Error message
            
        Returns:
            Error classification
        """
        error_lower = error.lower()
        
        if 'nameerror' in error_lower or 'not defined' in error_lower:
            return 'undefined_variable'
        elif 'syntaxerror' in error_lower:
            return 'syntax_error'
        elif 'indentationerror' in error_lower:
            return 'indentation_error'
        elif 'typeerror' in error_lower:
            return 'type_error'
        elif 'attributeerror' in error_lower:
            return 'attribute_error'
        elif 'importerror' in error_lower or 'modulenotfounderror' in error_lower:
            return 'import_error'
        elif 'indexerror' in error_lower:
            return 'index_error'
        elif 'keyerror' in error_lower:
            return 'key_error'
        elif 'valueerror' in error_lower:
            return 'value_error'
        elif 'zerodivisionerror' in error_lower:
            return 'division_error'
        elif 'filenotfounderror' in error_lower:
            return 'file_not_found'
        elif 'permissionerror' in error_lower:
            return 'permission_error'
        else:
            return 'unknown_error'
    
    def _parse_analysis(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse LLM analysis response
        
        Args:
            analysis_text: Raw LLM output
            
        Returns:
            Parsed analysis dictionary
        """
        result = {
            'cause': '',
            'fixed_code': '',
            'explanation': ''
        }
        
        # Extract cause
        cause_match = re.search(r'CAUSE:\s*(.*?)(?=FIX:|EXPLANATION:|$)', analysis_text, re.DOTALL | re.IGNORECASE)
        if cause_match:
            result['cause'] = cause_match.group(1).strip()
        
        # Extract fixed code
        code_pattern = r'```(?:python|py)?\n(.*?)```'
        code_matches = re.findall(code_pattern, analysis_text, re.DOTALL)
        if code_matches:
            result['fixed_code'] = code_matches[0].strip()
        
        # Extract explanation
        exp_match = re.search(r'EXPLANATION:\s*(.*?)$', analysis_text, re.DOTALL | re.IGNORECASE)
        if exp_match:
            result['explanation'] = exp_match.group(1).strip()
        
        return result
    
    def generate_fix(self, analysis: Dict[str, Any]) -> str:
        """
        Generate fixed code based on analysis
        
        Args:
            analysis: Error analysis dictionary
            
        Returns:
            Fixed code
        """
        if analysis.get('fixed_code'):
            return analysis['fixed_code']
        
        # If no fixed code in analysis, try to generate it
        logger.warning("MAX System: No fixed code in analysis, regenerating...")
        
        code = analysis.get('original_code', '')
        error = analysis.get('original_error', '')
        
        # Simple fix attempts based on error type
        error_type = analysis.get('error_type', 'unknown_error')
        
        if error_type == 'import_error':
            return self._fix_import_error(code, error)
        elif error_type == 'indentation_error':
            return self._fix_indentation(code)
        elif error_type == 'syntax_error':
            return self._fix_syntax(code, error)
        else:
            # Use LLM for general fixes
            return self.llm.analyze_error(code, error).split('```python')[-1].split('```')[0].strip()
    
    def _fix_import_error(self, code: str, error: str) -> str:
        """Try to fix import errors"""
        # Extract missing module name
        match = re.search(r"No module named '(\w+)'", error)
        if match:
            module = match.group(1)
            # Add note about missing dependency
            return f"# NOTE: Install missing module: pip install {module}\n\n{code}"
        return code
    
    def _fix_indentation(self, code: str) -> str:
        """Try to fix indentation errors"""
        # Simple fix: normalize to 4 spaces
        lines = code.split('\n')
        fixed_lines = []
        
        for line in lines:
            if line.strip():
                # Count leading spaces
                spaces = len(line) - len(line.lstrip())
                # Normalize to multiples of 4
                normalized_spaces = (spaces // 4) * 4
                fixed_lines.append(' ' * normalized_spaces + line.lstrip())
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _fix_syntax(self, code: str, error: str) -> str:
        """Try to fix syntax errors"""
        # This is complex, best handled by LLM
        return code
    
    def validate_fix(self, original_code: str, fixed_code: str, original_error: str) -> Dict[str, Any]:
        """
        Validate that a fix is reasonable
        
        Args:
            original_code: Original failing code
            fixed_code: Proposed fix
            original_error: Original error message
            
        Returns:
            Validation result
        """
        result = {
            'valid': True,
            'reason': '',
            'concerns': []
        }
        
        # Check if fix is substantially different
        if original_code == fixed_code:
            result['valid'] = False
            result['reason'] = "Fixed code is identical to original"
            return result
        
        # Check if fix is not empty
        if not fixed_code.strip():
            result['valid'] = False
            result['reason'] = "Fixed code is empty"
            return result
        
        # Check for suspicious patterns
        if '# TODO' in fixed_code or '# FIXME' in fixed_code:
            result['concerns'].append("Fixed code contains TODO/FIXME comments")
        
        if 'pass' in fixed_code and 'pass' not in original_code:
            result['concerns'].append("Fixed code adds 'pass' statements")
        
        return result
    
    def learn_from_fix(self, analysis: Dict[str, Any], fix_worked: bool):
        """
        Save fix pattern to memory for future learning
        
        Args:
            analysis: Error analysis
            fix_worked: Whether the fix was successful
        """
        error_type = analysis.get('error_type', 'unknown')
        cause = analysis.get('cause', '')
        
        # Save to memory
        self.memory.save_error(
            error_type=error_type,
            error_message=analysis.get('original_error', ''),
            code=analysis.get('original_code', ''),
            fix=analysis.get('fixed_code', ''),
            success=fix_worked
        )
        
        if fix_worked:
            # Save as successful pattern
            self.memory.save_experience(
                task_type=f"error_fix_{error_type}",
                pattern=f"{cause}: {analysis.get('explanation', '')}",
                metadata={
                    'error_type': error_type,
                    'fix_explanation': analysis.get('explanation', '')
                }
            )
            logger.info(f"MAX System: Learned from successful fix of {error_type}")
    
    def suggest_improvements(self, code: str, execution_result: Dict[str, Any]) -> list[str]:
        """
        Suggest improvements even when code works
        
        Args:
            code: Working code
            execution_result: Execution results
            
        Returns:
            List of improvement suggestions
        """
        suggestions = []
        
        # Check for common improvement opportunities
        if 'import' not in code:
            suggestions.append("Consider adding necessary imports at the top")
        
        if '"""' not in code and "'''" not in code:
            suggestions.append("Add docstrings to document the code")
        
        if 'def ' in code and 'return' not in code:
            suggestions.append("Consider adding return values to functions")
        
        # Check execution output
        output = execution_result.get('output', '')
        if 'warning' in output.lower():
            suggestions.append("Address warnings in the output")
        
        return suggestions
    
    def create_retry_strategy(self, attempt_number: int, previous_errors: list[str]) -> Dict[str, Any]:
        """
        Create a retry strategy based on attempt history
        
        Args:
            attempt_number: Current attempt number
            previous_errors: List of previous error messages
            
        Returns:
            Retry strategy
        """
        strategy = {
            'should_retry': attempt_number < self.max_fix_attempts,
            'approach': 'standard',
            'modifications': []
        }
        
        if not strategy['should_retry']:
            return strategy
        
        # Analyze error patterns
        if all('import' in err.lower() for err in previous_errors):
            strategy['approach'] = 'install_dependencies'
            strategy['modifications'].append("Install missing dependencies")
        
        elif all('syntax' in err.lower() for err in previous_errors):
            strategy['approach'] = 'simplify_code'
            strategy['modifications'].append("Simplify code structure")
        
        elif len(previous_errors) >= 2 and previous_errors[-1] == previous_errors[-2]:
            strategy['approach'] = 'alternative_solution'
            strategy['modifications'].append("Try completely different approach")
        
        return strategy
