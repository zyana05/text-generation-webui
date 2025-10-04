"""
Memory Agent for MAX System
Manages long-term memory using SQLite and vector embeddings with ChromaDB
"""

import sqlite3
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import chromadb
    from chromadb.config import Settings
    from chromadb.utils import embedding_functions
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: ChromaDB not available. Vector search disabled.")

from modules.logging_colors import logger


class MemoryAgent:
    """Manages task history, experiences, and learned patterns"""
    
    def __init__(self, config):
        self.config = config
        self.db_path = Path(config['memory']['sqlite_path'])
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
        # Initialize ChromaDB for vector search
        self.chroma_client = None
        self.collection = None
        if CHROMADB_AVAILABLE:
            self._init_chromadb()
    
    def _init_db(self):
        """Initialize SQLite database schema"""
        cursor = self.conn.cursor()
        
        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                result TEXT,
                error TEXT
            )
        """)
        
        # Steps table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS steps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                code TEXT,
                output TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)
        
        # Experiences table - stores successful patterns
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_type TEXT NOT NULL,
                pattern TEXT NOT NULL,
                success_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)
        
        # Errors table - stores error patterns and fixes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                code_snippet TEXT,
                fix_applied TEXT,
                success BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
        logger.info("MAX System: Memory database initialized")
    
    def _init_chromadb(self):
        """Initialize ChromaDB for vector embeddings"""
        try:
            chroma_path = Path(self.config['memory']['chromadb_path'])
            chroma_path.mkdir(parents=True, exist_ok=True)
            
            embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=self.config['memory'].get('embedding_model', 'sentence-transformers/all-mpnet-base-v2')
            )
            
            self.chroma_client = chromadb.PersistentClient(
                path=str(chroma_path),
                settings=Settings(anonymized_telemetry=False)
            )
            
            self.collection = self.chroma_client.get_or_create_collection(
                name="max_experiences",
                embedding_function=embedder
            )
            
            logger.info("MAX System: ChromaDB initialized")
        except Exception as e:
            logger.warning(f"MAX System: ChromaDB initialization failed - {e}")
            self.chroma_client = None
            self.collection = None
    
    def create_task(self, description: str) -> int:
        """Create a new task entry"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (description, status) VALUES (?, ?)",
            (description, "pending")
        )
        self.conn.commit()
        task_id = cursor.lastrowid
        logger.info(f"MAX System: Created task {task_id}: {description[:50]}...")
        return task_id
    
    def update_task_status(self, task_id: int, status: str, result: str = None, error: str = None):
        """Update task status"""
        cursor = self.conn.cursor()
        
        if status == "completed":
            cursor.execute(
                "UPDATE tasks SET status=?, result=?, completed_at=CURRENT_TIMESTAMP WHERE id=?",
                (status, result, task_id)
            )
        else:
            cursor.execute(
                "UPDATE tasks SET status=?, error=? WHERE id=?",
                (status, error, task_id)
            )
        
        self.conn.commit()
        logger.info(f"MAX System: Task {task_id} status: {status}")
    
    def add_step(self, task_id: int, step_number: int, description: str) -> int:
        """Add a step to a task"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO steps (task_id, step_number, description, status) VALUES (?, ?, ?, ?)",
            (task_id, step_number, description, "pending")
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def update_step(self, step_id: int, status: str, code: str = None, output: str = None, error: str = None):
        """Update step status and results"""
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE steps SET status=?, code=?, output=?, error=? WHERE id=?",
            (status, code, output, error, step_id)
        )
        self.conn.commit()
    
    def save_experience(self, task_type: str, pattern: str, metadata: Dict = None):
        """Save a successful pattern for future reference"""
        cursor = self.conn.cursor()
        
        # Check if pattern exists
        cursor.execute(
            "SELECT id, success_count FROM experiences WHERE task_type=? AND pattern=?",
            (task_type, pattern)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Increment success count
            cursor.execute(
                "UPDATE experiences SET success_count=?, last_used=CURRENT_TIMESTAMP WHERE id=?",
                (existing['success_count'] + 1, existing['id'])
            )
        else:
            # Create new experience
            cursor.execute(
                "INSERT INTO experiences (task_type, pattern, metadata) VALUES (?, ?, ?)",
                (task_type, pattern, json.dumps(metadata or {}))
            )
        
        self.conn.commit()
        
        # Add to vector database
        if self.collection:
            try:
                doc_id = f"{task_type}_{pattern[:20]}_{int(time.time())}"
                self.collection.add(
                    documents=[f"{task_type}: {pattern}"],
                    metadatas=[metadata or {}],
                    ids=[doc_id]
                )
            except Exception as e:
                logger.warning(f"MAX System: Failed to add to ChromaDB - {e}")
    
    def save_error(self, error_type: str, error_message: str, code: str = None, fix: str = None, success: bool = False):
        """Save an error pattern and its fix"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO errors (error_type, error_message, code_snippet, fix_applied, success) VALUES (?, ?, ?, ?, ?)",
            (error_type, error_message, code, fix, success)
        )
        self.conn.commit()
    
    def get_similar_experiences(self, query: str, limit: int = 5) -> List[Dict]:
        """Find similar past experiences using vector search"""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            experiences = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    experiences.append({
                        'pattern': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            return experiences
        except Exception as e:
            logger.warning(f"MAX System: Vector search failed - {e}")
            return []
    
    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """Get recent task history"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append(dict(row))
        
        return tasks
    
    def get_task_steps(self, task_id: int) -> List[Dict]:
        """Get all steps for a task"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM steps WHERE task_id=? ORDER BY step_number",
            (task_id,)
        )
        
        steps = []
        for row in cursor.fetchall():
            steps.append(dict(row))
        
        return steps
    
    def get_common_errors(self, limit: int = 10) -> List[Dict]:
        """Get most common error patterns"""
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT error_type, error_message, COUNT(*) as count, 
               SUM(CASE WHEN success THEN 1 ELSE 0 END) as fixed_count
               FROM errors 
               GROUP BY error_type, error_message 
               ORDER BY count DESC 
               LIMIT ?""",
            (limit,)
        )
        
        errors = []
        for row in cursor.fetchall():
            errors.append(dict(row))
        
        return errors
    
    def close(self):
        """Close database connections"""
        if self.conn:
            self.conn.close()
        if self.chroma_client:
            # ChromaDB doesn't need explicit closing
            pass
