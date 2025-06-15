from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from typing import Dict, List, Optional
from pydantic import BaseModel

Base = declarative_base()

class Partner(Base):
    """Partner/entreprenør modell for konfigurasjon av agenter og branding"""
    __tablename__ = "partners"
    
    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=True)  # Tillatte domener
    
    # Branding
    brand_name = Column(String(100), nullable=False)  # "HouseHacker", "Byggmester AS"
    brand_color = Column(String(7), default="#2563eb")  # Hex color
    logo_url = Column(String(255), nullable=True)
    
    # Agent-konfigurasjon
    enabled_agents = Column(JSON, default=["renovation"])  # Liste over tilgjengelige agenter
    agent_display_name = Column(String(100), default="Oppussingsrådgiver")
    welcome_message = Column(Text, default="Hei! Jeg kan hjelpe deg med oppussingsberegninger.")
    
    # Widget-konfigurasjon
    widget_position = Column(String(20), default="bottom-right")  # bottom-right, bottom-left, etc.
    widget_theme = Column(String(20), default="light")  # light, dark
    show_branding = Column(Boolean, default=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Pydantic models for API
class PartnerCreate(BaseModel):
    partner_id: str
    name: str
    domain: Optional[str] = None
    brand_name: str
    brand_color: str = "#2563eb"
    logo_url: Optional[str] = None
    enabled_agents: List[str] = ["renovation"]
    agent_display_name: str = "Oppussingsrådgiver"
    welcome_message: str = "Hei! Jeg kan hjelpe deg med oppussingsberegninger."
    widget_position: str = "bottom-right"
    widget_theme: str = "light"
    show_branding: bool = True

class PartnerResponse(BaseModel):
    id: int
    partner_id: str
    name: str
    brand_name: str
    brand_color: str
    logo_url: Optional[str]
    enabled_agents: List[str]
    agent_display_name: str
    welcome_message: str
    widget_position: str
    widget_theme: str
    show_branding: bool
    is_active: bool
    
    class Config:
        from_attributes = True

class PartnerConfig(BaseModel):
    """Konfigurasjon som sendes til widget"""
    partner_id: str
    brand_name: str
    brand_color: str
    logo_url: Optional[str]
    agent_display_name: str
    welcome_message: str
    widget_position: str
    widget_theme: str
    show_branding: bool
    enabled_agents: List[str]