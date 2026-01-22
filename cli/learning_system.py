"""
Learning System for ARIA
Enables ARIA to learn from user corrections and improve over time
"""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class Feedback:
    """User feedback on ARIA's response"""
    id: Optional[int] = None
    timestamp: str = ""
    user_query: str = ""
    aria_response: str = ""
    user_correction: str = ""
    feedback_type: str = "correction"  # correction, preference, rating
    rating: Optional[int] = None  # 1-5 scale
    context: str = ""  # JSON string of context
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

@dataclass
class Pattern:
    """Learned pattern from user interactions"""
    pattern_type: str  # preference, common_mistake, useful_approach
    description: str
    frequency: int
    confidence: float
    examples: List[str]
    metadata: Dict

class LearningSystem:
    """
    Manages ARIA's learning from user feedback and corrections
    """
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # In-memory caches for quick access
        self.recent_feedback: List[Feedback] = []
        self.learned_patterns: Dict[str, Pattern] = {}
        self._load_patterns()
    
    def _init_database(self):
        """Initialize SQLite database for storing feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_query TEXT NOT NULL,
                aria_response TEXT NOT NULL,
                user_correction TEXT,
                feedback_type TEXT,
                rating INTEGER,
                context TEXT
            )
        ''')
        
        # Patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                description TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                confidence REAL DEFAULT 0.5,
                examples TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Initialized learning database at {self.db_path}")
    
    def record_feedback(self, feedback: Feedback) -> int:
        """
        Record user feedback
        
        Returns:
            Feedback ID
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (timestamp, user_query, aria_response, 
                                user_correction, feedback_type, rating, context)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            feedback.timestamp,
            feedback.user_query,
            feedback.aria_response,
            feedback.user_correction,
            feedback.feedback_type,
            feedback.rating,
            feedback.context
        ))
        
        feedback_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Add to recent feedback cache
        feedback.id = feedback_id
        self.recent_feedback.append(feedback)
        
        # Trigger pattern learning
        self._analyze_feedback(feedback)
        
        logger.info(f"Recorded feedback #{feedback_id}: {feedback.feedback_type}")
        return feedback_id
    
    def _analyze_feedback(self, feedback: Feedback):
        """Analyze feedback to extract patterns"""
        # Simple pattern detection - can be enhanced with ML
        
        if feedback.feedback_type == "correction":
            # Look for similar corrections
            similar = self._find_similar_corrections(feedback)
            
            if len(similar) >= 2:  # At least 2 similar corrections
                # Create or update pattern
                pattern_key = f"correction_{hash(feedback.user_query[:50])}"
                
                if pattern_key in self.learned_patterns:
                    pattern = self.learned_patterns[pattern_key]
                    pattern.frequency += 1
                    pattern.confidence = min(pattern.confidence + 0.1, 1.0)
                    pattern.examples.append(feedback.user_correction)
                else:
                    pattern = Pattern(
                        pattern_type="common_mistake",
                        description=f"User tends to correct responses about: {feedback.user_query[:100]}",
                        frequency=1,
                        confidence=0.6,
                        examples=[feedback.user_correction],
                        metadata={"query_pattern": feedback.user_query[:100]}
                    )
                    self.learned_patterns[pattern_key] = pattern
                
                self._save_pattern(pattern_key, pattern)
    
    def _find_similar_corrections(self, feedback: Feedback) -> List[Feedback]:
        """Find similar corrections in history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple keyword-based similarity (can be enhanced with embeddings)
        keywords = set(feedback.user_query.lower().split()[:5])
        
        cursor.execute('''
            SELECT * FROM feedback
            WHERE feedback_type = 'correction'
            AND id != ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (feedback.id or -1,))
        
        similar = []
        for row in cursor.fetchall():
            query_keywords = set(row[2].lower().split()[:5])
            if len(keywords & query_keywords) >= 2:
                similar.append(Feedback(*row))
        
        conn.close()
        return similar
    
    def _save_pattern(self, key: str, pattern: Pattern):
        """Save pattern to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        examples_json = json.dumps(pattern.examples)
        metadata_json = json.dumps(pattern.metadata)
        
        cursor.execute('''
            INSERT OR REPLACE INTO patterns 
            (id, pattern_type, description, frequency, confidence, examples, metadata, created_at, updated_at)
            VALUES (
                (SELECT id FROM patterns WHERE description = ?),
                ?, ?, ?, ?, ?, ?, 
                COALESCE((SELECT created_at FROM patterns WHERE description = ?), ?),
                ?
            )
        ''', (
            pattern.description,
            pattern.pattern_type,
            pattern.description,
            pattern.frequency,
            pattern.confidence,
            examples_json,
            metadata_json,
            pattern.description,
            now,
            now
        ))
        
        conn.commit()
        conn.close()
    
    def _load_patterns(self):
        """Load learned patterns from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patterns WHERE confidence > 0.5 ORDER BY frequency DESC')
        
        for row in cursor.fetchall():
            pattern_id, ptype, desc, freq, conf, examples_json, metadata_json, created, updated = row
            
            pattern = Pattern(
                pattern_type=ptype,
                description=desc,
                frequency=freq,
                confidence=conf,
                examples=json.loads(examples_json) if examples_json else [],
                metadata=json.loads(metadata_json) if metadata_json else {}
            )
            
            self.learned_patterns[f"pattern_{pattern_id}"] = pattern
        
        conn.close()
        logger.info(f"Loaded {len(self.learned_patterns)} learned patterns")
    
    def get_relevant_patterns(self, query: str, limit: int = 5) -> List[Pattern]:
        """Get patterns relevant to the current query"""
        # Simple keyword matching - can be enhanced with embeddings
        query_keywords = set(query.lower().split())
        
        scored_patterns = []
        for pattern in self.learned_patterns.values():
            # Score based on keyword overlap and confidence
            metadata_text = str(pattern.metadata).lower()
            overlap = len(query_keywords & set(metadata_text.split()))
            score = (overlap * pattern.confidence * pattern.frequency)
            
            if score > 0:
                scored_patterns.append((score, pattern))
        
        # Sort by score and return top patterns
        scored_patterns.sort(reverse=True, key=lambda x: x[0])
        return [p for _, p in scored_patterns[:limit]]
    
    def get_preference(self, key: str) -> Optional[str]:
        """Get a user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else None
    
    def set_preference(self, key: str, value: str):
        """Set a user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (key, value, updated_at)
            VALUES (?, ?, ?)
        ''', (key, value, now))
        
        conn.commit()
        conn.close()
        logger.info(f"Set preference: {key} = {value}")
    
    def get_statistics(self) -> Dict:
        """Get learning statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM feedback')
        total_feedback = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM feedback WHERE feedback_type = "correction"')
        corrections = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM patterns')
        total_patterns = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(rating) FROM feedback WHERE rating IS NOT NULL')
        avg_rating = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            "total_feedback": total_feedback,
            "corrections": corrections,
            "learned_patterns": total_patterns,
            "average_rating": round(avg_rating, 2)
        }
    
    def enhance_prompt(self, base_prompt: str, query: str) -> str:
        """
        Enhance a prompt with learned patterns and preferences
        """
        patterns = self.get_relevant_patterns(query)
        
        if not patterns:
            return base_prompt
        
        enhancement = "\n\nLearned preferences and patterns:\n"
        for pattern in patterns:
            enhancement += f"- {pattern.description}\n"
            if pattern.examples:
                enhancement += f"  Example: {pattern.examples[0][:100]}\n"
        
        return base_prompt + enhancement
