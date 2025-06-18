#!/usr/bin/env python3
"""
Script for å initialisere pricing database med grunnleggende tjenester og markedspriser.
Basert på research fra Oslo-markedet.
"""

from app.database import SessionLocal, engine
from app.models.pricing import ServiceType, Contractor, PricingData, MarketRate, Base
from app.services.pricing_service import PricingService

def create_tables():
    """Opprett database-tabeller"""
    Base.metadata.create_all(bind=engine)
    print("✅ Pricing tables created")

def init_service_types(db):
    """Opprett grunnleggende tjenestekategorier"""
    
    services = [
        # Overflatebehandling
        {"name": "maling", "description": "Maling av vegger og tak", "unit": "m²", "category": "overflatebehandling"},
        {"name": "sparkling", "description": "Sparkling av vegger", "unit": "m²", "category": "overflatebehandling"},
        {"name": "helsparkling", "description": "Helsparkling av vegger", "unit": "m²", "category": "overflatebehandling"},
        {"name": "tapetsering", "description": "Tapetsering av vegger", "unit": "m²", "category": "overflatebehandling"},
        {"name": "tapet_fjerning", "description": "Fjerning av gammelt tapet", "unit": "m²", "category": "overflatebehandling"},
        
        # Gulv
        {"name": "laminat_legging", "description": "Legging av laminatgulv", "unit": "m²", "category": "gulv"},
        {"name": "parkett_legging", "description": "Legging av parkett", "unit": "m²", "category": "gulv"},
        {"name": "flislegging_gulv", "description": "Legging av fliser på gulv", "unit": "m²", "category": "gulv"},
        {"name": "vinyl_legging", "description": "Legging av vinylgulv", "unit": "m²", "category": "gulv"},
        
        # Fliser
        {"name": "flislegging_vegg", "description": "Flislegging på vegger", "unit": "m²", "category": "bad"},
        {"name": "flisfuging", "description": "Fuging av fliser", "unit": "m²", "category": "bad"},
        
        # Rør og elektro
        {"name": "rørlegger_time", "description": "Rørleggerarbeid per time", "unit": "timer", "category": "rør"},
        {"name": "elektriker_time", "description": "Elektrikerarbeid per time", "unit": "timer", "category": "elektro"},
        
        # Rigg og drift
        {"name": "rigg_og_drift", "description": "Rigg og drift for malerjobber", "unit": "dag", "category": "overhead"},
        {"name": "avfallshåndtering", "description": "Avfallshåndtering", "unit": "m³", "category": "overhead"},
    ]
    
    for service_data in services:
        existing = db.query(ServiceType).filter(ServiceType.name == service_data["name"]).first()
        if not existing:
            service = ServiceType(**service_data)
            db.add(service)
    
    db.commit()
    print(f"✅ Added {len(services)} service types")

def init_contractors(db):
    """Legg til noen eksempel kontraktører (data fra research)"""
    
    contractors = [
        {
            "name": "Oslo Malerfirma AS",
            "company_type": "malerfirma",
            "location": "Oslo",
            "website": "https://oslo-maler.no",
            "phone": "22 12 34 56",
            "specialties": "maling,sparkling,helsparkling,tapetsering",
            "verified": True
        },
        {
            "name": "Profi Flislegger",
            "company_type": "flislegger",
            "location": "Oslo",
            "website": "https://profi-fliser.no",
            "phone": "22 23 45 67",
            "specialties": "flislegging_gulv,flislegging_vegg,flisfuging",
            "verified": True
        },
        {
            "name": "Gulveksperten AS",
            "company_type": "gulvlegger",
            "location": "Oslo",
            "website": "https://gulveksperten.no",
            "phone": "22 34 56 78",
            "specialties": "laminat_legging,parkett_legging,vinyl_legging",
            "verified": True
        }
    ]
    
    for contractor_data in contractors:
        existing = db.query(Contractor).filter(Contractor.name == contractor_data["name"]).first()
        if not existing:
            contractor = Contractor(**contractor_data)
            db.add(contractor)
    
    db.commit()
    print(f"✅ Added {len(contractors)} contractors")

def init_pricing_data(db):
    """Legg til markedspriser basert på research fra Oslo"""
    
    # Research fra forskjellige nettsider og tilbud
    pricing_data = [
        # Maling (per m²)
        {"service": "maling", "min_price": 80, "max_price": 150, "source": "market_research"},
        {"service": "sparkling", "min_price": 150, "max_price": 300, "source": "market_research"},
        {"service": "helsparkling", "min_price": 200, "max_price": 400, "source": "market_research"},
        {"service": "tapetsering", "min_price": 200, "max_price": 350, "source": "market_research"},
        {"service": "tapet_fjerning", "min_price": 50, "max_price": 120, "source": "market_research"},
        
        # Gulv (per m²)
        {"service": "laminat_legging", "min_price": 200, "max_price": 350, "source": "market_research"},
        {"service": "parkett_legging", "min_price": 300, "max_price": 500, "source": "market_research"},
        {"service": "flislegging_gulv", "min_price": 400, "max_price": 800, "source": "market_research"},
        {"service": "vinyl_legging", "min_price": 150, "max_price": 280, "source": "market_research"},
        
        # Fliser (per m²)
        {"service": "flislegging_vegg", "min_price": 500, "max_price": 900, "source": "market_research"},
        {"service": "flisfuging", "min_price": 100, "max_price": 200, "source": "market_research"},
        
        # Timepriser
        {"service": "rørlegger_time", "min_price": 1200, "max_price": 1500, "source": "market_research"},
        {"service": "elektriker_time", "min_price": 1300, "max_price": 1600, "source": "market_research"},
        
        # Overhead
        {"service": "rigg_og_drift", "min_price": 2000, "max_price": 5000, "source": "market_research"},
        {"service": "avfallshåndtering", "min_price": 1500, "max_price": 3000, "source": "market_research"},
    ]
    
    for price_data in pricing_data:
        service = db.query(ServiceType).filter(ServiceType.name == price_data["service"]).first()
        if service:
            existing = db.query(PricingData).filter(
                PricingData.service_type_id == service.id,
                PricingData.source == price_data["source"]
            ).first()
            
            if not existing:
                pricing = PricingData(
                    service_type_id=service.id,
                    min_price=price_data["min_price"],
                    max_price=price_data["max_price"],
                    avg_price=(price_data["min_price"] + price_data["max_price"]) / 2,
                    region="Oslo",
                    source=price_data["source"],
                    confidence=0.8
                )
                db.add(pricing)
    
    db.commit()
    print(f"✅ Added {len(pricing_data)} pricing entries")

def main():
    """Initialiser hele pricing-systemet"""
    
    print("🚀 Initializing pricing database...")
    
    # Opprett tabeller
    create_tables()
    
    # Initialiser database
    db = SessionLocal()
    
    try:
        # Legg til grunndata
        init_service_types(db)
        init_contractors(db)
        init_pricing_data(db)
        
        # Beregn markedsrater
        pricing_service = PricingService(db)
        pricing_service.update_market_rates("Oslo")
        print("✅ Market rates calculated")
        
        print("\n🎉 Pricing database initialized successfully!")
        print("\nExample usage:")
        print("from app.services.pricing_service import PricingService")
        print("pricing = PricingService(db)")
        print("result = pricing.get_service_price('maling', area=100)")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()