"""
Initialize database with default partners
Run this script after database setup to create initial data
"""
import asyncio
from app.database import create_tables, SessionLocal
from app.models.partner import Partner

def init_database():
    """Initialize database with tables and default partners"""
    print("🗄️ Creating database tables...")
    create_tables()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if househacker already exists
        existing = db.query(Partner).filter(Partner.partner_id == "househacker").first()
        if existing:
            print("✅ househacker partner already exists")
            return
        
        # Create househacker partner
        househacker = Partner(
            partner_id="househacker",
            name="househacker AS",
            domain="househacker.no",
            brand_name="househacker",
            brand_color="#e11d48",
            logo_url="https://househacker.no/logo.png",
            enabled_agents=["renovation"],
            agent_display_name="Oppussingsrådgiver",
            welcome_message="Hei! Jeg er househacker sin oppussingsrådgiver. Jeg kan hjelpe deg beregne materialer og kostnader for ditt oppussingsprosjekt.",
            widget_position="bottom-right",
            widget_theme="light",
            show_branding=True
        )
        
        db.add(househacker)
        db.commit()
        print("✅ Created househacker partner")
        
    except Exception as e:
        print(f"❌ Error creating partner: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
    print("🚀 Database initialization complete!")