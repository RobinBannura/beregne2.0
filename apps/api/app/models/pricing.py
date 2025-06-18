from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ServiceType(Base):
    """Definerer tjenestekategorier (maling, flislegging, etc.)"""
    __tablename__ = "service_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)  # maling, sparkling, flislegging
    description = Column(Text)
    unit = Column(String(20))  # m², timer, stk
    category = Column(String(50))  # overflatebehandling, gulv, bad, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pricing_data = relationship("PricingData", back_populates="service_type")

class Contractor(Base):
    """Håndverkere og firmaer med deres spesialiteter"""
    __tablename__ = "contractors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), index=True)
    company_type = Column(String(100))  # malerfirma, flislegger, etc.
    location = Column(String(100))  # Oslo, Bærum, etc.
    website = Column(String(500))
    phone = Column(String(20))
    specialties = Column(Text)  # JSON array av service_types
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    pricing_data = relationship("PricingData", back_populates="contractor")

class PricingData(Base):
    """Faktiske priser fra markedet"""
    __tablename__ = "pricing_data"
    
    id = Column(Integer, primary_key=True, index=True)
    service_type_id = Column(Integer, ForeignKey("service_types.id"))
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=True)
    
    # Prising
    min_price = Column(Float)  # kr per enhet (m², time, etc.)
    max_price = Column(Float)
    avg_price = Column(Float)
    minimum_charge = Column(Float)  # Minimum totalkostnad
    
    # Metadata
    region = Column(String(100))  # Oslo, Norge, etc.
    source = Column(String(200))  # Nettside, API, manuell
    source_url = Column(String(500))
    confidence = Column(Float)  # 0-1, hvor sikre er vi på prisen
    last_updated = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    service_type = relationship("ServiceType", back_populates="pricing_data")
    contractor = relationship("Contractor", back_populates="pricing_data")

class MarketRate(Base):
    """Beregnede markedsrater basert på alle kilder"""
    __tablename__ = "market_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    service_type_id = Column(Integer, ForeignKey("service_types.id"))
    
    # Beregnede verdier
    market_min = Column(Float)
    market_max = Column(Float)
    market_avg = Column(Float)
    recommended_price = Column(Float)  # Vår anbefaling til kunder
    
    # Kvalitet
    sample_size = Column(Integer)  # Antall datapunkter
    confidence_score = Column(Float)  # 0-1
    last_calculated = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    region = Column(String(100))
    
    # Relationships
    service_type = relationship("ServiceType")