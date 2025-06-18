from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import re
from collections import Counter, defaultdict

from ..models.conversation import ConversationSession, ConversationMessage, ConversationPattern
from ..database import SessionLocal

class ConversationLearningService:
    """
    Service that learns from user conversations to improve AI responses
    """
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    async def log_conversation_start(
        self, 
        session_id: str, 
        partner_id: str, 
        agent_used: str
    ) -> ConversationSession:
        """Start logging a new conversation session"""
        
        # Check if session already exists
        existing = self.db.query(ConversationSession).filter(
            ConversationSession.session_id == session_id
        ).first()
        
        if existing:
            return existing
        
        # Create new session
        session = ConversationSession(
            session_id=session_id,
            partner_id=partner_id,
            agent_used=agent_used
        )
        
        self.db.add(session)
        self.db.commit()
        return session
    
    async def log_message_exchange(
        self,
        session_id: str,
        user_message: str,
        agent_response: str,
        ai_powered: bool = False,
        ai_reasoning: str = None,
        project_type_detected: str = None,
        missing_info: List[str] = None,
        led_to_pricing: bool = False,
        led_to_registration: bool = False
    ) -> ConversationMessage:
        """Log a complete message exchange (user question + agent response)"""
        
        # Get or create session
        session = self.db.query(ConversationSession).filter(
            ConversationSession.session_id == session_id
        ).first()
        
        if not session:
            session = await self.log_conversation_start(session_id, "unknown", "unknown")
        
        # Get message order
        message_count = self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).count()
        
        # Create message record
        message = ConversationMessage(
            session_id=session_id,
            message_order=message_count + 1,
            user_message=user_message,
            agent_response=agent_response,
            ai_powered=ai_powered,
            ai_reasoning=ai_reasoning,
            project_type_detected=project_type_detected,
            led_to_pricing=led_to_pricing,
            led_to_registration=led_to_registration
        )
        
        if missing_info:
            message.set_missing_info_list(missing_info)
        
        self.db.add(message)
        
        # Update session stats
        session.total_messages = message_count + 1
        if led_to_registration:
            session.led_to_registration = True
        
        self.db.commit()
        
        # Async pattern learning (don't block the response)
        try:
            await self._analyze_and_learn_patterns(message)
        except Exception as e:
            print(f"Pattern learning failed: {e}")
        
        return message
    
    async def mark_user_responded(
        self, 
        session_id: str, 
        response_time_seconds: float = None
    ):
        """Mark that user responded to the last agent message"""
        
        last_message = self.db.query(ConversationMessage).filter(
            ConversationMessage.session_id == session_id
        ).order_by(ConversationMessage.message_order.desc()).first()
        
        if last_message:
            last_message.user_responded = True
            if response_time_seconds:
                last_message.user_response_time_seconds = response_time_seconds
            self.db.commit()
    
    async def _analyze_and_learn_patterns(self, message: ConversationMessage):
        """Analyze message and update learned patterns"""
        
        user_query = message.user_message.lower()
        project_type = message.project_type_detected or "unknown"
        
        # Extract patterns from user query
        patterns_to_check = [
            self._extract_maling_pattern(user_query),
            self._extract_bad_pattern(user_query),
            self._extract_kjokken_pattern(user_query),
            self._extract_general_pattern(user_query, project_type)
        ]
        
        for pattern_info in patterns_to_check:
            if pattern_info:
                await self._update_or_create_pattern(
                    pattern_info, 
                    message.user_message, 
                    message.agent_response,
                    message.ai_powered
                )
    
    def _extract_maling_pattern(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract maling-specific patterns"""
        
        if "mal" not in query:
            return None
        
        # Categorize maling queries
        if any(word in query for word in ["innvendig", "inni", "stue", "soverom", "gang"]):
            return {
                "pattern_name": "maling_innvendig_initial",
                "user_query_pattern": r"(mal|paint).*(innvendig|inni|stue|soverom|gang)",
                "project_type": "maling",
                "category": "innvendig"
            }
        elif any(word in query for word in ["utvendig", "ute", "fasade", "vegg", "hus"]):
            return {
                "pattern_name": "maling_utvendig_initial", 
                "user_query_pattern": r"(mal|paint).*(utvendig|ute|fasade|hus)",
                "project_type": "maling",
                "category": "utvendig"
            }
        else:
            return {
                "pattern_name": "maling_general_initial",
                "user_query_pattern": r"(mal|paint)",
                "project_type": "maling",
                "category": "general"
            }
    
    def _extract_bad_pattern(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract bathroom-specific patterns"""
        
        if "bad" not in query:
            return None
        
        if any(word in query for word in ["total", "komplett", "renovering", "pusse opp"]):
            return {
                "pattern_name": "bad_total_renovering",
                "user_query_pattern": r"bad.*(total|komplett|renovering|pusse opp)",
                "project_type": "bad_komplett",
                "category": "total_renovation"
            }
        else:
            return {
                "pattern_name": "bad_general",
                "user_query_pattern": r"bad",
                "project_type": "bad_komplett", 
                "category": "general"
            }
    
    def _extract_kjokken_pattern(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract kitchen-specific patterns"""
        
        if "kjøkken" not in query and "kitchen" not in query:
            return None
        
        return {
            "pattern_name": "kjokken_general",
            "user_query_pattern": r"(kjøkken|kitchen)",
            "project_type": "kjøkken_komplett",
            "category": "general"
        }
    
    def _extract_general_pattern(self, query: str, project_type: str) -> Optional[Dict[str, Any]]:
        """Extract general patterns for any project type"""
        
        return {
            "pattern_name": f"{project_type}_general",
            "user_query_pattern": query[:50],  # First 50 chars as pattern
            "project_type": project_type,
            "category": "general"
        }
    
    async def _update_or_create_pattern(
        self, 
        pattern_info: Dict[str, Any], 
        user_query: str,
        agent_response: str,
        ai_powered: bool
    ):
        """Update existing pattern or create new one"""
        
        pattern_name = pattern_info["pattern_name"]
        
        # Find existing pattern
        existing = self.db.query(ConversationPattern).filter(
            ConversationPattern.pattern_name == pattern_name
        ).first()
        
        if existing:
            # Update existing pattern
            existing.times_seen += 1
            existing.add_sample_query(user_query)
            if ai_powered:  # Only add AI-generated responses as good samples
                existing.add_sample_response(agent_response)
            existing.last_updated = datetime.utcnow()
            
            # Update success rate (simplified - could be more sophisticated)
            if ai_powered:
                existing.success_rate = (existing.success_rate * 0.8) + (0.8 * 0.2)  # Weighted average
            
        else:
            # Create new pattern
            pattern = ConversationPattern(
                pattern_name=pattern_name,
                user_query_pattern=pattern_info["user_query_pattern"],
                project_type=pattern_info["project_type"],
                most_successful_followup=agent_response if ai_powered else "",
                success_rate=0.7 if ai_powered else 0.3,
                times_seen=1,
                confidence_score=0.6
            )
            pattern.add_sample_query(user_query)
            if ai_powered:
                pattern.add_sample_response(agent_response)
            
            self.db.add(pattern)
        
        self.db.commit()
    
    async def get_improved_ai_prompt(self, project_type: str) -> str:
        """Generate improved AI prompt based on learned patterns"""
        
        # Get patterns for this project type
        patterns = self.db.query(ConversationPattern).filter(
            ConversationPattern.project_type == project_type,
            ConversationPattern.confidence_score > 0.5,
            ConversationPattern.times_seen >= 3  # Only use patterns seen multiple times
        ).order_by(ConversationPattern.success_rate.desc()).limit(5).all()
        
        if not patterns:
            return ""
        
        # Build improved prompt section
        prompt_additions = [f"\nLEARNED PATTERNS FOR {project_type.upper()}:"]
        
        for pattern in patterns:
            sample_queries = pattern.get_sample_queries()
            sample_responses = pattern.get_sample_responses()
            
            if sample_queries and sample_responses:
                prompt_additions.append(f"\nWhen user says something like: {', '.join(sample_queries[:3])}")
                prompt_additions.append(f"Good follow-up questions: {', '.join(sample_responses[:2])}")
                prompt_additions.append(f"Success rate: {pattern.success_rate:.1%} ({pattern.times_seen} times)")
        
        return "\n".join(prompt_additions)
    
    async def get_conversation_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get conversation analytics for the last N days"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get sessions
        sessions = self.db.query(ConversationSession).filter(
            ConversationSession.started_at >= cutoff_date
        ).all()
        
        # Get messages
        messages = self.db.query(ConversationMessage).filter(
            ConversationMessage.created_at >= cutoff_date
        ).all()
        
        # Calculate metrics
        total_conversations = len(sessions)
        total_messages = len(messages)
        ai_powered_messages = len([m for m in messages if m.ai_powered])
        registrations = len([s for s in sessions if s.led_to_registration])
        
        # Project type distribution
        project_types = Counter([m.project_type_detected for m in messages if m.project_type_detected])
        
        # Most common user queries
        user_queries = [m.user_message for m in messages if m.user_message]
        
        return {
            "period_days": days,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "ai_powered_percentage": (ai_powered_messages / total_messages * 100) if total_messages > 0 else 0,
            "registration_conversion_rate": (registrations / total_conversations * 100) if total_conversations > 0 else 0,
            "project_type_distribution": dict(project_types.most_common(10)),
            "most_common_queries": [q[:50] for q in user_queries[:10]],
            "learned_patterns_count": self.db.query(ConversationPattern).count()
        }
    
    def close(self):
        """Close database connection"""
        if self.db:
            self.db.close()