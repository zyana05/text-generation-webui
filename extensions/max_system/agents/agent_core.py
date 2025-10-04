"""
Core Agent for MAX System
Main orchestrator that coordinates all other agents
"""

import time
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from modules.logging_colors import logger

from ..llm_wrapper import LLMWrapper
from .agent_memory import MemoryAgent
from .agent_planner import PlannerAgent
from .agent_coder import CoderAgent
from .agent_executor import ExecutorAgent
from .agent_reflex import ReflexAgent
from .agent_tools import ToolsAgent


class CoreAgent:
    """Main orchestrator for the MAX System"""
    
    def __init__(self, config_path: str = None):
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / 'config.yaml'
        
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize all sub-agents
        logger.info("MAX System: Initializing agents...")
        
        self.llm = LLMWrapper(self.config.get('llm', {}))
        self.memory = MemoryAgent(self.config)
        self.planner = PlannerAgent(self.llm, self.memory, self.config)
        self.coder = CoderAgent(self.llm, self.memory, self.config)
        self.executor = ExecutorAgent(self.config)
        self.reflex = ReflexAgent(self.llm, self.memory, self.config)
        self.tools = ToolsAgent(self.config)
        
        # State
        self.current_task_id = None
        self.current_plan = None
        
        logger.info("MAX System: All agents initialized successfully")
    
    def execute_task(self, task_description: str) -> Dict[str, Any]:
        """
        Main entry point - execute a complete task
        
        Args:
            task_description: Natural language description of the task
            
        Returns:
            Dictionary with task results
        """
        logger.info(f"MAX System: Starting task - {task_description}")
        
        # Check if model is loaded
        if not self.llm.is_model_loaded():
            logger.error("MAX System: No model loaded. Please load a model first.")
            return {
                'success': False,
                'error': 'No model loaded',
                'task_id': None
            }
        
        start_time = time.time()
        
        # Create task in memory
        task_id = self.memory.create_task(task_description)
        self.current_task_id = task_id
        
        # Create plan
        logger.info("MAX System: Creating execution plan...")
        plan = self.planner.create_plan(task_description)
        self.current_plan = plan
        
        # Validate plan
        is_valid, validation_msg = self.planner.validate_plan(plan)
        if not is_valid:
            logger.error(f"MAX System: Invalid plan - {validation_msg}")
            self.memory.update_task_status(task_id, "failed", error=validation_msg)
            return {
                'success': False,
                'error': validation_msg,
                'task_id': task_id
            }
        
        # Execute plan step by step
        logger.info(f"MAX System: Executing {plan['total_steps']} steps...")
        
        project_name = f"task_{task_id}_{int(time.time())}"
        project_dir = self.executor.create_project_structure(project_name)
        
        # Initialize git
        self.tools.git_init(project_dir)
        self.tools.create_gitignore(project_dir)
        
        task_result = {
            'success': False,
            'task_id': task_id,
            'project_dir': str(project_dir),
            'steps_completed': 0,
            'steps_failed': 0,
            'total_steps': plan['total_steps'],
            'outputs': [],
            'errors': []
        }
        
        # Execute each step
        context = ""
        for step_idx in range(plan['total_steps']):
            step_number, step_description = self.planner.get_next_step(plan)
            
            if step_number is None:
                break
            
            logger.info(f"MAX System: Step {step_number}/{plan['total_steps']} - {step_description}")
            
            # Save step to memory
            step_id = self.memory.add_step(task_id, step_number, step_description)
            
            # Execute step with retry logic
            step_result = self._execute_step_with_retry(
                step_description, 
                context, 
                project_dir,
                step_id
            )
            
            if step_result['success']:
                task_result['steps_completed'] += 1
                task_result['outputs'].append({
                    'step': step_number,
                    'description': step_description,
                    'output': step_result.get('output', '')
                })
                
                # Update context for next step
                if step_result.get('code'):
                    context += f"\n\nStep {step_number} ({step_description}):\n```python\n{step_result['code']}\n```\n"
                
                # Mark step complete
                self.planner.mark_step_complete(plan)
                self.memory.update_step(step_id, "completed", code=step_result.get('code'))
                
                # Commit step
                self.tools.git_commit_step(project_dir, step_number, step_description)
                
            else:
                task_result['steps_failed'] += 1
                task_result['errors'].append({
                    'step': step_number,
                    'description': step_description,
                    'error': step_result.get('error', 'Unknown error')
                })
                
                self.memory.update_step(step_id, "failed", error=step_result.get('error'))
                
                # Decide whether to continue or abort
                if self._should_abort_task(task_result):
                    logger.error("MAX System: Too many failures, aborting task")
                    break
        
        # Finalize task
        elapsed_time = time.time() - start_time
        task_result['execution_time'] = elapsed_time
        
        if task_result['steps_completed'] == task_result['total_steps']:
            task_result['success'] = True
            self.memory.update_task_status(task_id, "completed", result=str(task_result))
            
            # Save successful pattern
            task_type = self.planner.analyze_task_type(task_description)
            self.memory.save_experience(
                task_type=task_type,
                pattern=task_description,
                metadata={'steps': plan['total_steps'], 'time': elapsed_time}
            )
            
            logger.info(f"MAX System: Task completed successfully in {elapsed_time:.1f}s")
        else:
            self.memory.update_task_status(task_id, "failed", error=f"Completed {task_result['steps_completed']}/{task_result['total_steps']} steps")
            logger.warning(f"MAX System: Task partially completed - {task_result['steps_completed']}/{task_result['total_steps']} steps")
        
        return task_result
    
    def _execute_step_with_retry(self, step_description: str, context: str, 
                                  project_dir: Path, step_id: int) -> Dict[str, Any]:
        """Execute a single step with retry logic"""
        
        max_attempts = self.reflex.max_fix_attempts
        previous_errors = []
        
        for attempt in range(max_attempts):
            if attempt > 0:
                logger.info(f"MAX System: Retry attempt {attempt + 1}/{max_attempts}")
            
            # Generate code
            code_result = self.coder.generate_code(step_description, context)
            code = code_result['code']
            
            # Validate syntax
            is_valid, syntax_error = self.coder.validate_syntax(code)
            if not is_valid:
                logger.warning(f"MAX System: Syntax error - {syntax_error}")
                previous_errors.append(syntax_error)
                
                # Try to fix syntax
                analysis = self.reflex.analyze_error(code, syntax_error)
                code = self.reflex.generate_fix(analysis)
                
                # Revalidate
                is_valid, _ = self.coder.validate_syntax(code)
                if not is_valid:
                    continue
            
            # Save code to file
            filename = f"step_{step_id}.py"
            code_file = self.executor.save_code_to_file(code, filename, "src")
            
            # Execute code
            exec_result = self.executor.execute_python(code)
            
            if exec_result['success']:
                logger.info(f"MAX System: Step executed successfully")
                return {
                    'success': True,
                    'code': code,
                    'output': exec_result['output'],
                    'file': str(code_file)
                }
            
            # Execution failed - analyze and fix
            error = exec_result.get('error', 'Unknown error')
            traceback = exec_result.get('traceback', '')
            
            logger.warning(f"MAX System: Execution failed - {error}")
            previous_errors.append(error)
            
            # Analyze error
            analysis = self.reflex.analyze_error(code, error, traceback)
            
            # Check retry strategy
            strategy = self.reflex.create_retry_strategy(attempt + 1, previous_errors)
            if not strategy['should_retry']:
                logger.error("MAX System: Max retry attempts reached")
                return {
                    'success': False,
                    'error': error,
                    'attempts': attempt + 1
                }
            
            # Generate fix
            fixed_code = self.reflex.generate_fix(analysis)
            
            # Validate fix
            fix_validation = self.reflex.validate_fix(code, fixed_code, error)
            if not fix_validation['valid']:
                logger.warning(f"MAX System: Fix validation failed - {fix_validation['reason']}")
                continue
            
            # Update context with fix
            context += f"\n\nPrevious attempt failed: {error}\nFix applied: {analysis.get('explanation', '')}\n"
        
        # All attempts failed
        return {
            'success': False,
            'error': f"Failed after {max_attempts} attempts. Last error: {previous_errors[-1] if previous_errors else 'Unknown'}",
            'attempts': max_attempts
        }
    
    def _should_abort_task(self, task_result: Dict[str, Any]) -> bool:
        """Determine if task should be aborted"""
        # Abort if more than 50% of steps failed
        if task_result['steps_failed'] > task_result['total_steps'] * 0.5:
            return True
        
        # Abort if 3 consecutive failures
        if len(task_result['errors']) >= 3:
            return True
        
        return False
    
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """Get status of a task"""
        tasks = self.memory.get_task_history(limit=100)
        for task in tasks:
            if task['id'] == task_id:
                steps = self.memory.get_task_steps(task_id)
                return {
                    'task': task,
                    'steps': steps
                }
        return None
    
    def list_recent_tasks(self, limit: int = 10) -> list:
        """List recent tasks"""
        return self.memory.get_task_history(limit)
    
    def cleanup(self):
        """Cleanup resources"""
        if self.memory:
            self.memory.close()
        logger.info("MAX System: Cleanup complete")
