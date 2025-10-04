"""
LLM Wrapper for MAX System
Interfaces with text-generation-webui's loaded models
"""

import copy
from modules import shared
from modules.text_generation import generate_reply
from modules.logging_colors import logger


class LLMWrapper:
    """Wrapper for interacting with loaded LLM models"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.default_state = self._get_default_state()
    
    def _get_default_state(self):
        """Get default generation state"""
        state = {
            'max_new_tokens': self.config.get('max_tokens', 4096),
            'temperature': self.config.get('temperature', 0.7),
            'top_p': self.config.get('top_p', 0.9),
            'top_k': self.config.get('top_k', 40),
            'repetition_penalty': 1.15,
            'encoder_repetition_penalty': 1.0,
            'no_repeat_ngram_size': 0,
            'min_length': 0,
            'do_sample': True,
            'penalty_alpha': 0.0,
            'num_beams': 1,
            'length_penalty': 1.0,
            'early_stopping': False,
            'add_bos_token': True,
            'ban_eos_token': False,
            'skip_special_tokens': True,
            'stream': False,
            'seed': -1,
            'custom_stopping_strings': [],
        }
        return state
    
    def is_model_loaded(self):
        """Check if a model is loaded"""
        return shared.model is not None and shared.model_name not in [None, 'None']
    
    def generate(self, prompt, max_tokens=None, temperature=None, stop_strings=None):
        """
        Generate text from the loaded model
        
        Args:
            prompt: Input prompt string
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stop_strings: List of strings to stop generation
            
        Returns:
            Generated text string
        """
        if not self.is_model_loaded():
            logger.error("MAX System: No model loaded")
            return ""
        
        # Prepare state
        state = copy.deepcopy(self.default_state)
        if max_tokens is not None:
            state['max_new_tokens'] = max_tokens
        if temperature is not None:
            state['temperature'] = temperature
        
        # Generate
        try:
            result = ""
            for response in generate_reply(
                prompt, 
                state, 
                stopping_strings=stop_strings or [],
                is_chat=False
            ):
                result = response
            
            return result
        except Exception as e:
            logger.error(f"MAX System: Generation error - {e}")
            return ""
    
    def generate_with_system_prompt(self, system_prompt, user_prompt, max_tokens=None):
        """
        Generate with system and user prompts
        
        Args:
            system_prompt: System instructions
            user_prompt: User query
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response
        """
        full_prompt = f"""<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_prompt}<|im_end|>
<|im_start|>assistant
"""
        
        response = self.generate(
            full_prompt, 
            max_tokens=max_tokens,
            stop_strings=['<|im_end|>', '<|im_start|>']
        )
        
        return response.strip()
    
    def generate_code(self, task_description, language="python", context=""):
        """
        Generate code for a given task
        
        Args:
            task_description: Description of the code to generate
            language: Programming language
            context: Additional context
            
        Returns:
            Generated code
        """
        system_prompt = f"""You are an expert {language} programmer. Generate clean, efficient, well-documented code.
Follow best practices and include error handling where appropriate."""

        user_prompt = f"""Task: {task_description}

{f'Context: {context}' if context else ''}

Generate {language} code to accomplish this task. Include docstrings and comments.
Respond with ONLY the code, no explanations."""

        return self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=4096)
    
    def analyze_error(self, code, error_message, traceback_str=""):
        """
        Analyze an error and suggest fixes
        
        Args:
            code: Code that caused the error
            error_message: Error message
            traceback_str: Full traceback if available
            
        Returns:
            Analysis and suggested fix
        """
        system_prompt = """You are an expert debugger. Analyze errors and provide clear, actionable fixes."""
        
        user_prompt = f"""The following code produced an error:

```python
{code}
```

Error: {error_message}

{f'Traceback: {traceback_str}' if traceback_str else ''}

Analyze the error and provide:
1. Root cause
2. Fixed code
3. Explanation of the fix

Respond in this format:
CAUSE: <explanation>
FIX:
```python
<fixed code>
```
EXPLANATION: <how it fixes the issue>"""

        return self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=2048)
    
    def create_plan(self, task_description, max_steps=20):
        """
        Create a step-by-step plan for a task
        
        Args:
            task_description: Task to plan for
            max_steps: Maximum number of steps
            
        Returns:
            List of plan steps
        """
        system_prompt = """You are an expert project planner. Break down tasks into clear, actionable steps."""
        
        user_prompt = f"""Task: {task_description}

Create a detailed step-by-step plan with no more than {max_steps} steps.
Each step should be specific and actionable.

Format your response as a numbered list:
1. [Step description]
2. [Step description]
etc."""

        response = self.generate_with_system_prompt(system_prompt, user_prompt, max_tokens=1024)
        
        # Parse steps
        steps = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering
                step = line.split('.', 1)[-1].strip()
                step = step.lstrip('- ')
                if step:
                    steps.append(step)
        
        return steps
