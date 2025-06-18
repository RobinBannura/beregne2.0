#!/usr/bin/env python3
"""
Create session memory tables in production database
This script should be run when deploying the AI-powered features
"""

def create_session_tables():
    """Create session memory tables"""
    try:
        from app.database import create_tables, engine
        from app.models.session import SessionMemory
        
        print("🔄 Creating session memory tables...")
        
        # Create all tables including the new session memory table
        create_tables()
        
        print("✅ Session memory tables created successfully!")
        
        # Test table creation
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='session_memory'"))
            tables = result.fetchall()
            if tables:
                print(f"✅ Confirmed session_memory table exists")
            else:
                print("⚠️  session_memory table not found - checking if we're using PostgreSQL")
                # Try PostgreSQL query
                try:
                    result = conn.execute(text("SELECT tablename FROM pg_tables WHERE tablename='session_memory'"))
                    tables = result.fetchall()
                    if tables:
                        print(f"✅ Confirmed session_memory table exists in PostgreSQL")
                    else:
                        print("❌ session_memory table not found in PostgreSQL either")
                except:
                    print("ℹ️  Could not check PostgreSQL tables (probably using SQLite)")
        
    except Exception as e:
        print(f"❌ Failed to create session tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_session_tables()