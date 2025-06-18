#!/usr/bin/env python3
"""
Fix agent configuration in production
Updates househacker partner to use conversational_renovation agent
"""

def fix_agent_config():
    """Update partner configuration to use new agent name"""
    try:
        from app.database import SessionLocal
        from app.models.partner import Partner
        
        db = SessionLocal()
        
        print("🔄 Updating partner configuration...")
        
        partner = db.query(Partner).filter(Partner.partner_id == 'househacker').first()
        if partner:
            old_agents = partner.enabled_agents
            partner.enabled_agents = ['conversational_renovation']
            db.commit()
            print(f"✅ Updated househacker agent configuration")
            print(f"   Old: {old_agents}")
            print(f"   New: {partner.enabled_agents}")
        else:
            print("❌ househacker partner not found")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Failed to update agent configuration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_agent_config()