"""
MAX System Extension for Text Generation Web UI
Self-developing AI Agent System based on .gguf models
"""

import gradio as gr
import json
from pathlib import Path
from datetime import datetime

from modules import shared
from modules.logging_colors import logger

from .agents.agent_core import CoreAgent

# Global state
params = {
    "display_name": "MAX System - Self-Developing AI",
    "is_tab": True,
}

core_agent = None
current_task_result = None
execution_log = []


def setup():
    """Initialize MAX System on extension load"""
    global core_agent
    
    try:
        logger.info("MAX System: Initializing...")
        core_agent = CoreAgent()
        logger.info("MAX System: Ready")
    except Exception as e:
        logger.error(f"MAX System: Failed to initialize - {e}")
        core_agent = None


def execute_task_handler(task_description, progress=gr.Progress()):
    """Handle task execution from UI"""
    global current_task_result, execution_log
    
    if not core_agent:
        return "❌ MAX System not initialized. Check logs for errors.", "", ""
    
    if not task_description.strip():
        return "⚠️ Please enter a task description", "", ""
    
    execution_log = []
    execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting task: {task_description}")
    
    progress(0, desc="Initializing...")
    
    # Check if model is loaded
    if not shared.model or shared.model_name in [None, 'None']:
        msg = "⚠️ No model loaded. Please load a .gguf model first."
        execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {msg}")
        return msg, "\n".join(execution_log), ""
    
    execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Using model: {shared.model_name}")
    
    try:
        # Execute task
        progress(0.1, desc="Creating plan...")
        execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] Creating execution plan...")
        
        result = core_agent.execute_task(task_description)
        current_task_result = result
        
        # Format result
        if result['success']:
            status_msg = f"""✅ Task Completed Successfully!

**Task ID:** {result['task_id']}
**Project Directory:** {result['project_dir']}
**Steps Completed:** {result['steps_completed']}/{result['total_steps']}
**Execution Time:** {result['execution_time']:.1f}s

Check the project directory for generated code."""
            
            execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Task completed successfully")
        else:
            status_msg = f"""⚠️ Task Partially Completed

**Task ID:** {result['task_id']}
**Steps Completed:** {result['steps_completed']}/{result['total_steps']}
**Steps Failed:** {result['steps_failed']}

Check execution log for details."""
            
            execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Task failed or incomplete")
        
        # Format detailed results
        details = json.dumps(result, indent=2)
        
        return status_msg, "\n".join(execution_log), details
        
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        execution_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] ERROR: {e}")
        logger.error(f"MAX System: Task execution error - {e}")
        return error_msg, "\n".join(execution_log), ""


def get_task_status_handler(task_id_str):
    """Get status of a specific task"""
    if not core_agent:
        return "MAX System not initialized"
    
    try:
        task_id = int(task_id_str)
        status = core_agent.get_task_status(task_id)
        
        if status:
            return json.dumps(status, indent=2)
        else:
            return f"Task {task_id} not found"
    except ValueError:
        return "Invalid task ID"
    except Exception as e:
        return f"Error: {e}"


def list_tasks_handler():
    """List recent tasks"""
    if not core_agent:
        return "MAX System not initialized"
    
    try:
        tasks = core_agent.list_recent_tasks(limit=20)
        
        if not tasks:
            return "No tasks found"
        
        output = "# Recent Tasks\n\n"
        for task in tasks:
            status_emoji = "✅" if task['status'] == 'completed' else "⚠️" if task['status'] == 'failed' else "⏳"
            output += f"{status_emoji} **Task {task['id']}**: {task['description'][:80]}\n"
            output += f"   Status: {task['status']} | Created: {task['created_at']}\n\n"
        
        return output
    except Exception as e:
        return f"Error: {e}"


def ui():
    """Create Gradio UI for MAX System"""
    
    with gr.Tab("MAX System", elem_id="max-system-tab"):
        gr.Markdown("""
# 🚀 MAX System - Self-Developing AI Agent

Create a fully autonomous AI system that can:
- Plan and break down complex tasks
- Generate code automatically
- Execute and test code in sandbox
- Debug and fix errors autonomously
- Learn from experience
- Manage projects with Git

**Requirements:** Load a .gguf model first (e.g., Qwen2.5-14B-Instruct)
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("## Task Execution")
                
                task_input = gr.Textbox(
                    label="Task Description",
                    placeholder="Example: Create a Python script that scrapes weather data from a website and saves it to a SQLite database",
                    lines=4,
                    elem_id="max-task-input"
                )
                
                with gr.Row():
                    execute_btn = gr.Button("🚀 Execute Task", variant="primary")
                    clear_btn = gr.Button("Clear")
                
                status_output = gr.Markdown("Ready to execute tasks...")
                
                with gr.Accordion("Execution Log", open=False):
                    log_output = gr.Textbox(
                        label="Log",
                        lines=15,
                        max_lines=30,
                        elem_id="max-log-output"
                    )
                
                with gr.Accordion("Detailed Results", open=False):
                    details_output = gr.Textbox(
                        label="JSON Results",
                        lines=15,
                        max_lines=30,
                        elem_id="max-details-output"
                    )
            
            with gr.Column(scale=1):
                gr.Markdown("## Task Management")
                
                with gr.Accordion("Recent Tasks", open=True):
                    refresh_btn = gr.Button("🔄 Refresh Tasks")
                    tasks_list = gr.Markdown("No tasks yet")
                
                with gr.Accordion("Task Status", open=False):
                    task_id_input = gr.Textbox(
                        label="Task ID",
                        placeholder="Enter task ID",
                        elem_id="max-task-id"
                    )
                    status_btn = gr.Button("Get Status")
                    task_status_output = gr.Textbox(
                        label="Status",
                        lines=10,
                        elem_id="max-task-status"
                    )
                
                gr.Markdown("""
### Quick Start Examples

1. **Data Processing:**
   - "Create a CSV parser that extracts and analyzes sales data"

2. **Web Scraping:**
   - "Build a web scraper for news articles with sentiment analysis"

3. **API Development:**
   - "Create a REST API for managing a todo list"

4. **Automation:**
   - "Write a script to organize files by type and date"
                """)
        
        # Event handlers
        execute_btn.click(
            fn=execute_task_handler,
            inputs=[task_input],
            outputs=[status_output, log_output, details_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "Ready to execute tasks...", "", ""),
            inputs=[],
            outputs=[task_input, status_output, log_output, details_output]
        )
        
        refresh_btn.click(
            fn=list_tasks_handler,
            inputs=[],
            outputs=[tasks_list]
        )
        
        status_btn.click(
            fn=get_task_status_handler,
            inputs=[task_id_input],
            outputs=[task_status_output]
        )
        
        # Auto-refresh tasks on tab load
        # This will be triggered when the tab is selected
        gr.Markdown("", elem_id="max-system-init", visible=False)


def custom_css():
    """Custom CSS for MAX System"""
    return """
    #max-system-tab {
        padding: 20px;
    }
    
    #max-task-input textarea {
        font-size: 14px;
    }
    
    #max-log-output, #max-details-output, #max-task-status {
        font-family: monospace;
        font-size: 12px;
    }
    """


def custom_js():
    """Custom JavaScript for MAX System"""
    return """
    // Auto-scroll log output
    function autoScrollLog() {
        const logOutput = document.querySelector('#max-log-output textarea');
        if (logOutput) {
            logOutput.scrollTop = logOutput.scrollHeight;
        }
    }
    
    // Call on updates
    setInterval(autoScrollLog, 1000);
    """
