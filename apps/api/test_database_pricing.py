#!/usr/bin/env python3
"""
Test script for new database-based pricing system
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_agent_with_database():
    """Test the agent with new database pricing"""
    
    print("🧪 Testing Enhanced Renovation Agent with Database Pricing")
    print("=" * 60)
    
    try:
        # Initialize agent
        agent = EnhancedRenovationAgent()
        
        # Test painting query (the problematic one mentioned)
        test_queries = [
            "Pris på maling av 100 kvm",
            "Hva koster det å male 50 m²?",
            "Jeg vil vite kostnad for flislegging på 20 m²",
            "Komplett badrom renovering på 8 m²"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            print("-" * 40)
            
            result = await agent.process(query)
            
            total_cost = result.get("total_cost", 0)
            agent_used = result.get("agent_used", "unknown")
            
            print(f"✅ Agent: {agent_used}")
            print(f"💰 Total cost: {total_cost:,.0f} NOK")
            
            # Check if database pricing was used
            if "pricing_data" in str(result):
                print("📊 Database pricing: ✅ ACTIVE")
            else:
                print("📊 Database pricing: ❌ FALLBACK")
            
            print(f"📝 Response length: {len(result.get('response', ''))}")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_with_database())