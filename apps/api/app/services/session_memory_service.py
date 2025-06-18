from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re
import json
import hashlib

from ..models.session import SessionMemory
from ..database import SessionLocal

class SessionMemoryService:
    """
    Intelligent session memory management for renovation conversations
    Optimized for token efficiency while maintaining rich context
    """
    
    def __init__(self, db: Session = None):
        self.db = db or SessionLocal()
    
    def get_or_create_session(self, session_id: str, partner_id: str = None) -> SessionMemory:
        """Get existing session or create new one"""
        session = self.db.query(SessionMemory).filter(
            SessionMemory.session_id == session_id
        ).first()
        
        if not session:
            session = SessionMemory(
                session_id=session_id,
                partner_id=partner_id
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
        else:
            # Update activity
            session.update_activity()
            self.db.commit()
        
        return session
    
    def extract_and_store_context(self, session_id: str, query: str, 
                                analysis: Dict[str, Any] = None) -> SessionMemory:
        """
        Extract relevant context from user query and store efficiently
        Uses pattern matching and AI analysis to identify key information
        """
        session = self.get_or_create_session(session_id)
        
        # Extract property information
        property_info = self._extract_property_info(query)
        if property_info:
            if property_info.get('type'):
                session.property_type = property_info['type']
            if property_info.get('total_area'):
                session.total_area = property_info['total_area']
        
        # Extract room information
        room_info = self._extract_room_info(query)
        if room_info:
            existing_rooms = session.get_rooms_data()
            existing_rooms.update(room_info)
            session.set_rooms_data(existing_rooms)
        
        # Extract project type and preferences
        project_info = self._extract_project_info(query, analysis)
        if project_info:
            if project_info.get('type'):
                session.current_project_type = project_info['type']
            
            preferences = session.get_project_preferences()
            if project_info.get('preferences'):
                preferences.update(project_info['preferences'])
                session.set_project_preferences(preferences)
        
        # Extract budget information
        budget_info = self._extract_budget_info(query)
        if budget_info:
            session.budget_range = budget_info
        
        # Extract quality preferences
        quality_pref = self._extract_quality_preference(query)
        if quality_pref:
            session.preferred_quality_level = quality_pref
        
        # Store last question for context
        session.last_question = query[:500]  # Truncate to save space
        
        self.db.commit()
        return session
    
    def _extract_property_info(self, query: str) -> Dict[str, Any]:
        """Extract property type and total area"""
        query_lower = query.lower()
        result = {}
        
        # Property type
        if any(word in query_lower for word in ['leilighet', 'leiligheta']):
            result['type'] = 'leilighet'
        elif any(word in query_lower for word in ['enebolig', 'hus', 'villa']):
            result['type'] = 'enebolig'
        elif any(word in query_lower for word in ['rekkehus', 'tomannsbolig']):
            result['type'] = 'rekkehus'
        
        # Total area
        area_patterns = [
            r'(\d+)\s*kvm?\s*leilighet',
            r'(\d+)\s*kvadrat',
            r'leilighet.*?(\d+)\s*kvm?',
            r'hus.*?(\d+)\s*kvm?',
            r'(\d+)\s*kvm?\s*stor'
        ]
        
        for pattern in area_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    result['total_area'] = float(match.group(1))
                    break
                except:
                    continue
        
        return result
    
    def _extract_room_info(self, query: str) -> Dict[str, Any]:
        """Extract specific room information"""
        query_lower = query.lower()
        rooms = {}
        
        # Room area patterns
        room_patterns = [
            (r'bad\w*.*?(\d+)\s*(?:kvm?|m²)', 'bad'),
            (r'kjøkken.*?(\d+)\s*(?:kvm?|m²)', 'kjøkken'),
            (r'stue.*?(\d+)\s*(?:kvm?|m²)', 'stue'),
            (r'soverom.*?(\d+)\s*(?:kvm?|m²)', 'soverom'),
            (r'gang.*?(\d+)\s*(?:kvm?|m²)', 'gang'),
            (r'(\d+)\s*(?:kvm?|m²).*?bad', 'bad'),
            (r'(\d+)\s*(?:kvm?|m²).*?kjøkken', 'kjøkken'),
            (r'(\d+)\s*(?:kvm?|m²).*?stue', 'stue')
        ]
        
        for pattern, room_name in room_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    area = float(match.group(1))
                    rooms[room_name] = {'area': area}
                except:
                    continue
        
        # Extract room count
        room_count_patterns = [
            (r'(\d+)\s*soverom', 'soverom_count'),
            (r'(\d+)\s*bad', 'bad_count'),
            (r'(\d+)\s*roms?', 'total_rooms')
        ]
        
        for pattern, count_type in room_count_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    count = int(match.group(1))
                    if count_type not in rooms:
                        rooms['counts'] = rooms.get('counts', {})
                    rooms['counts'][count_type] = count
                except:
                    continue
        
        return rooms
    
    def _extract_project_info(self, query: str, analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Extract project type and specific preferences"""
        query_lower = query.lower()
        result = {}
        
        # Project type from analysis or patterns
        if analysis and analysis.get('project_type'):
            result['type'] = analysis['project_type']
        else:
            # Pattern-based extraction
            project_patterns = [
                (r'bad|baderom', 'bad'),
                (r'kjøkken', 'kjøkken'),
                (r'mal\w+|maling', 'maling'),
                (r'gulv|parkett|laminat|fliser', 'gulv'),
                (r'elektriker|elektrisk', 'elektriker'),
                (r'vinduer?|dører?', 'vinduer_dorer'),
                (r'tak|takarbeid', 'tak'),
                (r'isolering|isolasjon', 'isolasjon')
            ]
            
            for pattern, project_type in project_patterns:
                if re.search(pattern, query_lower):
                    result['type'] = project_type
                    break
        
        # Extract specific preferences
        preferences = {}
        
        # Quality indicators
        if any(word in query_lower for word in ['ikea', 'rimelig', 'billig', 'enkel']):
            preferences['quality_level'] = 'budget'
        elif any(word in query_lower for word in ['premium', 'luksus', 'high-end', 'dyr']):
            preferences['quality_level'] = 'premium'
        elif any(word in query_lower for word in ['sigdal', 'hth', 'midt', 'middels']):
            preferences['quality_level'] = 'mid'
        
        # Brand preferences
        brands = []
        brand_patterns = [
            r'ikea', r'sigdal', r'hth', r'kvik', r'norema',
            r'miele', r'siemens', r'electrolux', r'asko'
        ]
        for brand in brand_patterns:
            if re.search(brand, query_lower):
                brands.append(brand.upper())
        
        if brands:
            preferences['preferred_brands'] = brands
        
        # Material preferences
        if any(word in query_lower for word in ['laminat', 'kompaktlaminat']):
            preferences['benkeplate_material'] = 'laminat'
        elif any(word in query_lower for word in ['stein', 'granitt', 'kvarts']):
            preferences['benkeplate_material'] = 'stein'
        
        if preferences:
            result['preferences'] = preferences
        
        return result
    
    def _extract_budget_info(self, query: str) -> Optional[str]:
        """Extract budget range from query"""
        query_lower = query.lower()
        
        # Direct budget mentions
        budget_patterns = [
            r'budsjett.*?(\d+)(?:k|000)',
            r'maks.*?(\d+)(?:k|000)',
            r'under.*?(\d+)(?:k|000)',
            r'(\d+)(?:k|000).*?budsjett',
            r'(\d+)(?:k|000).*?maks'
        ]
        
        for pattern in budget_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    amount = int(match.group(1))
                    if amount < 1000:  # Assume it's in thousands
                        amount *= 1000
                    
                    # Categorize budget
                    if amount < 50000:
                        return "under-50k"
                    elif amount < 100000:
                        return "50k-100k"
                    elif amount < 200000:
                        return "100k-200k"
                    elif amount < 300000:
                        return "200k-300k"
                    else:
                        return "300k+"
                except:
                    continue
        
        return None
    
    def _extract_quality_preference(self, query: str) -> Optional[str]:
        """Extract quality level preference"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['rimelig', 'billig', 'ikea', 'budget']):
            return 'budget'
        elif any(word in query_lower for word in ['premium', 'luksus', 'kvalitet', 'skreddersydd']):
            return 'premium'
        elif any(word in query_lower for word in ['middels', 'midt', 'sigdal', 'hth']):
            return 'mid'
        
        return None
    
    def get_context_for_ai(self, session_id: str, max_tokens: int = 200) -> str:
        """
        Get token-optimized context summary for AI
        Prioritizes most relevant information for current conversation
        """
        session = self.db.query(SessionMemory).filter(
            SessionMemory.session_id == session_id
        ).first()
        
        if not session:
            return ""
        
        context = session.get_context_summary()
        
        # If context is too long, prioritize most important parts
        if len(context.split()) > max_tokens:
            # Keep only essential info: property, current project, budget
            essential_parts = []
            
            if session.property_type and session.total_area:
                essential_parts.append(f"{session.property_type} {session.total_area}kvm")
            
            if session.current_project_type:
                essential_parts.append(f"Project: {session.current_project_type}")
            
            if session.budget_range:
                essential_parts.append(f"Budget: {session.budget_range}")
            
            context = " | ".join(essential_parts)
        
        return context
    
    def update_followup_needs(self, session_id: str, missing_info: List[str]):
        """Mark what information we still need for better followup"""
        session = self.get_or_create_session(session_id)
        session.needs_followup = len(missing_info) > 0
        session.set_followup_context({"missing_info": missing_info})
        self.db.commit()
    
    def cleanup_stale_sessions(self, hours: int = 24):
        """Clean up old session data to save database space"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        stale_sessions = self.db.query(SessionMemory).filter(
            SessionMemory.last_activity < cutoff
        ).all()
        
        for session in stale_sessions:
            self.db.delete(session)
        
        self.db.commit()
        return len(stale_sessions)
    
    def close(self):
        """Close database connection"""
        self.db.close()