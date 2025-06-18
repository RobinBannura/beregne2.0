#!/usr/bin/env python3
"""
Initialize production database with all required tables
"""

def init_production_database():
    """Initialize all database tables for production"""
    try:
        print("🔄 Initializing production database...")
        
        from app.database import engine, create_tables
        from app.models.partner import Base as PartnerBase
        from app.models.pricing import Base as PricingBase  
        from app.models.session import Base as SessionBase
        from app.models.conversation import Base as ConversationBase
        
        # Create all tables
        PartnerBase.metadata.create_all(bind=engine)
        PricingBase.metadata.create_all(bind=engine) 
        SessionBase.metadata.create_all(bind=engine)
        ConversationBase.metadata.create_all(bind=engine)
        
        print("✅ All database tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import text
        with engine.connect() as conn:
            # Check for key tables
            tables_to_check = [
                'partners', 'session_memory', 
                'conversation_sessions', 'conversation_messages', 'conversation_patterns'
            ]
            
            existing_tables = []
            for table in tables_to_check:
                try:
                    # Try PostgreSQL first, then SQLite
                    try:
                        result = conn.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                        existing_tables.append(table)
                    except:
                        # Table might not exist or might be empty
                        pass
                except Exception:
                    pass
            
            print(f"✅ Verified tables: {existing_tables}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    init_production_database()