from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json
from typing import Dict, Any, List

from .partner import Base

class ConversationSession(Base):
    """
    Tracks complete conversation sessions for learning and improvement
    """
    __tablename__ = "conversation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    partner_id = Column(String, index=True)
    agent_used = Column(String, index=True)  # "conversational_renovation", "loan", etc.
    
    # Session metadata
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    total_messages = Column(Integer, default=0)
    
    # Outcome tracking
    led_to_registration = Column(Boolean, default=False)
    registration_completed = Column(Boolean, default=False)
    estimated_project_value = Column(Float, nullable=True)
    
    # Quality metrics
    user_satisfaction_score = Column(Float, nullable=True)  # If we add feedback
    ai_success_rate = Column(Float, default=0.0)  # % of AI responses that led to useful follow-up
    
    # Relationships
    messages = relationship("ConversationMessage", back_populates="session")

class ConversationMessage(Base):
    """
    Individual messages in conversations for pattern analysis
    """
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("conversation_sessions.session_id"))
    message_order = Column(Integer)  # Order within conversation
    
    # Message content
    user_message = Column(Text)
    agent_response = Column(Text)
    
    # AI analysis data
    ai_powered = Column(Boolean, default=False)
    ai_reasoning = Column(Text, nullable=True)
    project_type_detected = Column(String, nullable=True)
    missing_info_identified = Column(Text, nullable=True)  # JSON array
    
    # User behavior tracking
    user_responded = Column(Boolean, default=False)
    user_response_time_seconds = Column(Float, nullable=True)
    led_to_clarification = Column(Boolean, default=False)
    led_to_pricing = Column(Boolean, default=False)
    led_to_registration = Column(Boolean, default=False)
    
    # Quality assessment
    response_quality_score = Column(Float, nullable=True)  # Algorithm-based scoring
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("ConversationSession", back_populates="messages")
    
    def get_missing_info_list(self) -> List[str]:
        """Get missing info as list"""
        if self.missing_info_identified:
            try:
                return json.loads(self.missing_info_identified)
            except:
                return []
        return []
    
    def set_missing_info_list(self, info_list: List[str]):
        """Set missing info from list"""
        self.missing_info_identified = json.dumps(info_list)

class ConversationPattern(Base):
    """
    Learned patterns from conversation analysis for AI improvement
    """
    __tablename__ = "conversation_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Pattern identification
    pattern_name = Column(String, index=True)  # "maling_innvendig_initial", "bad_size_question"
    user_query_pattern = Column(Text)  # Regex or keyword pattern
    project_type = Column(String, index=True)
    
    # Learned insights
    most_successful_followup = Column(Text)  # The follow-up question that works best
    success_rate = Column(Float)  # How often this follow-up leads to useful response
    average_response_time = Column(Float)  # How quickly users respond
    
    # Supporting data
    sample_user_queries = Column(Text)  # JSON: Examples that match this pattern
    sample_good_responses = Column(Text)  # JSON: Examples of good follow-ups
    times_seen = Column(Integer, default=1)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Confidence metrics
    confidence_score = Column(Float, default=0.5)  # How confident we are in this pattern
    
    def get_sample_queries(self) -> List[str]:
        """Get sample queries as list"""
        if self.sample_user_queries:
            try:
                return json.loads(self.sample_user_queries)
            except:
                return []
        return []
    
    def add_sample_query(self, query: str):
        """Add a new sample query"""
        samples = self.get_sample_queries()
        if query not in samples:
            samples.append(query)
            # Keep only last 10 samples
            if len(samples) > 10:
                samples = samples[-10:]
            self.sample_user_queries = json.dumps(samples)
    
    def get_sample_responses(self) -> List[str]:
        """Get sample responses as list"""
        if self.sample_good_responses:
            try:
                return json.loads(self.sample_good_responses)
            except:
                return []
        return []
    
    def add_sample_response(self, response: str):
        """Add a new sample response"""
        samples = self.get_sample_responses()
        if response not in samples:
            samples.append(response)
            if len(samples) > 5:
                samples = samples[-5:]
            self.sample_good_responses = json.dumps(samples)