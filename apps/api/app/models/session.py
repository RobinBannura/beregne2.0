from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json
from typing import Dict, Any, Optional

from .partner import Base

class SessionMemory(Base):
    """
    Token-efficient session memory for renovation conversations
    Stores structured context data instead of full conversation history
    """
    __tablename__ = "session_memory"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    partner_id = Column(String, index=True)
    
    # Property context (structured data)
    property_type = Column(String)  # "leilighet", "enebolig", "rekkehus"
    total_area = Column(Float)  # Total kvm
    rooms_data = Column(Text)  # JSON: {"stue": {"area": 25, "ceiling_height": 2.7}, "bad": {"area": 6}}
    
    # Current project context
    current_project_type = Column(String)  # "bad", "kjøkken", "maling", etc
    project_preferences = Column(Text)  # JSON: preferences and requirements
    budget_range = Column(String)  # "50k-100k", "100k-200k", etc
    
    # Conversation state
    last_question = Column(Text)  # Last thing user asked about
    needs_followup = Column(Boolean, default=False)
    followup_context = Column(Text)  # JSON: what info we still need
    
    # Quality preferences learned over time
    preferred_quality_level = Column(String)  # "budget", "mid", "premium"
    preferred_brands = Column(Text)  # JSON: ["IKEA", "HTH"] etc
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    
    def get_rooms_data(self) -> Dict[str, Any]:
        """Get rooms data as dict"""
        if self.rooms_data:
            try:
                return json.loads(self.rooms_data)
            except:
                return {}
        return {}
    
    def set_rooms_data(self, data: Dict[str, Any]):
        """Set rooms data from dict"""
        self.rooms_data = json.dumps(data)
    
    def get_project_preferences(self) -> Dict[str, Any]:
        """Get project preferences as dict"""
        if self.project_preferences:
            try:
                return json.loads(self.project_preferences)
            except:
                return {}
        return {}
    
    def set_project_preferences(self, data: Dict[str, Any]):
        """Set project preferences from dict"""
        self.project_preferences = json.dumps(data)
    
    def get_followup_context(self) -> Dict[str, Any]:
        """Get followup context as dict"""
        if self.followup_context:
            try:
                return json.loads(self.followup_context)
            except:
                return {}
        return {}
    
    def set_followup_context(self, data: Dict[str, Any]):
        """Set followup context from dict"""
        self.followup_context = json.dumps(data)
    
    def get_preferred_brands(self) -> list:
        """Get preferred brands as list"""
        if self.preferred_brands:
            try:
                return json.loads(self.preferred_brands)
            except:
                return []
        return []
    
    def set_preferred_brands(self, brands: list):
        """Set preferred brands from list"""
        self.preferred_brands = json.dumps(brands)
    
    def get_context_summary(self) -> str:
        """
        Generate a token-efficient context summary for AI
        Only includes relevant information for current conversation
        """
        context_parts = []
        
        # Property info
        if self.property_type and self.total_area:
            context_parts.append(f"Property: {self.property_type} {self.total_area}kvm")
        
        # Room details if relevant to current project
        rooms = self.get_rooms_data()
        if rooms and self.current_project_type:
            relevant_rooms = []
            for room, data in rooms.items():
                if self.current_project_type in ["bad", "kjøkken"] and room in ["bad", "kjøkken"]:
                    relevant_rooms.append(f"{room}: {data.get('area', 'unknown')}kvm")
                elif self.current_project_type == "maling" and "area" in data:
                    relevant_rooms.append(f"{room}: {data.get('area', 'unknown')}kvm")
            if relevant_rooms:
                context_parts.append(f"Rooms: {', '.join(relevant_rooms)}")
        
        # Current project and preferences
        if self.current_project_type:
            context_parts.append(f"Current project: {self.current_project_type}")
        
        preferences = self.get_project_preferences()
        if preferences:
            pref_items = []
            for key, value in preferences.items():
                if value:
                    pref_items.append(f"{key}: {value}")
            if pref_items:
                context_parts.append(f"Preferences: {', '.join(pref_items)}")
        
        # Budget if specified
        if self.budget_range:
            context_parts.append(f"Budget: {self.budget_range}")
        
        # Quality level preference
        if self.preferred_quality_level:
            context_parts.append(f"Quality level: {self.preferred_quality_level}")
        
        return " | ".join(context_parts) if context_parts else ""
    
    def is_stale(self, hours: int = 24) -> bool:
        """Check if session memory is stale and should be cleaned up"""
        if not self.last_activity:
            return True
        
        from datetime import timedelta
        return datetime.utcnow() - self.last_activity > timedelta(hours=hours)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()
        self.updated_at = datetime.utcnow()