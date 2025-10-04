"""
Planner Agent for MAX System
Breaks down tasks into actionable steps and manages dependencies
"""

from typing import List, Dict, Any
from modules.logging_colors import logger


class PlannerAgent:
    """Plans and orchestrates task execution"""
    
    def __init__(self, llm_wrapper, memory_agent, config):
        self.llm = llm_wrapper
        self.memory = memory_agent
        self.config = config
        self.max_steps = config['agents']['planner'].get('max_steps', 20)
    
    def create_plan(self, task_description: str) -> Dict[str, Any]:
        """
        Create a detailed execution plan for a task
        
        Args:
            task_description: Description of the task
            
        Returns:
            Dictionary containing plan details
        """
        logger.info(f"MAX System: Planning task - {task_description[:50]}...")
        
        # Check for similar past tasks
        similar = self.memory.get_similar_experiences(task_description, limit=3)
        context = ""
        if similar:
            context = "\n\nSimilar past experiences:\n"
            for exp in similar:
                context += f"- {exp['pattern']}\n"
        
        # Generate plan
        steps = self.llm.create_plan(task_description + context, max_steps=self.max_steps)
        
        if not steps:
            logger.warning("MAX System: Failed to generate plan")
            steps = [task_description]  # Fallback to single step
        
        plan = {
            'task': task_description,
            'steps': steps,
            'total_steps': len(steps),
            'current_step': 0,
            'status': 'created'
        }
        
        logger.info(f"MAX System: Created plan with {len(steps)} steps")
        return plan
    
    def analyze_task_type(self, task_description: str) -> str:
        """
        Analyze and categorize the task type
        
        Args:
            task_description: Task description
            
        Returns:
            Task type (e.g., 'data_processing', 'web_scraping', 'api', etc.)
        """
        task_lower = task_description.lower()
        
        # Simple keyword-based classification
        if any(word in task_lower for word in ['api', 'endpoint', 'rest', 'http']):
            return 'api_development'
        elif any(word in task_lower for word in ['scrape', 'crawl', 'web', 'html']):
            return 'web_scraping'
        elif any(word in task_lower for word in ['data', 'csv', 'json', 'parse', 'process']):
            return 'data_processing'
        elif any(word in task_lower for word in ['database', 'sql', 'query', 'table']):
            return 'database'
        elif any(word in task_lower for word in ['file', 'read', 'write', 'io']):
            return 'file_operations'
        elif any(word in task_lower for word in ['test', 'unittest', 'pytest']):
            return 'testing'
        else:
            return 'general'
    
    def estimate_complexity(self, plan: Dict[str, Any]) -> str:
        """
        Estimate task complexity based on plan
        
        Args:
            plan: Task plan
            
        Returns:
            Complexity level: 'simple', 'moderate', 'complex'
        """
        num_steps = plan['total_steps']
        
        if num_steps <= 3:
            return 'simple'
        elif num_steps <= 8:
            return 'moderate'
        else:
            return 'complex'
    
    def refine_step(self, step_description: str, context: str = "") -> str:
        """
        Refine a step description to make it more actionable
        
        Args:
            step_description: Original step description
            context: Additional context
            
        Returns:
            Refined step description
        """
        # For now, return as-is
        # Could be enhanced to use LLM for refinement
        return step_description
    
    def validate_plan(self, plan: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate that a plan is feasible
        
        Args:
            plan: Task plan
            
        Returns:
            Tuple of (is_valid, reason)
        """
        if not plan['steps']:
            return False, "Plan has no steps"
        
        if plan['total_steps'] > self.max_steps:
            return False, f"Too many steps ({plan['total_steps']} > {self.max_steps})"
        
        return True, "Plan is valid"
    
    def get_next_step(self, plan: Dict[str, Any]) -> tuple[int, str]:
        """
        Get the next step to execute
        
        Args:
            plan: Current plan
            
        Returns:
            Tuple of (step_number, step_description)
        """
        current = plan['current_step']
        
        if current >= plan['total_steps']:
            return None, None
        
        step_number = current + 1
        step_description = plan['steps'][current]
        
        return step_number, step_description
    
    def mark_step_complete(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mark current step as complete and move to next
        
        Args:
            plan: Current plan
            
        Returns:
            Updated plan
        """
        plan['current_step'] += 1
        
        if plan['current_step'] >= plan['total_steps']:
            plan['status'] = 'completed'
        
        return plan
    
    def handle_step_failure(self, plan: Dict[str, Any], error: str) -> Dict[str, Any]:
        """
        Handle a step failure and potentially adjust the plan
        
        Args:
            plan: Current plan
            error: Error description
            
        Returns:
            Updated plan (may include retry strategy)
        """
        logger.warning(f"MAX System: Step {plan['current_step'] + 1} failed - {error}")
        
        # For now, just mark as failed
        # Could be enhanced to insert recovery steps
        plan['status'] = 'failed'
        plan['error'] = error
        
        return plan
