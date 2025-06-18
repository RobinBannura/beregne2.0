#!/usr/bin/env python3
"""
Test the specific painting query that was problematic
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_painting_query():
    """Test painting query specifically"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        # Test the specific query mentioned
        query = "maling av 100 kvm"
        print(f"🧪 Testing: '{query}'")
        
        result = await agent.process(query)
        
        print(f"✅ Agent: {result.get('agent_used')}")
        print(f"💰 Total cost: {result.get('total_cost', 0):,.0f} NOK")
        print(f"📋 Query type: {agent._analyze_renovation_query(query)['type']}")
        
        # Also test variations
        queries = [
            "Hva koster det å male 100 m²",
            "Jeg trenger hjelp med malerarbeid på 100 kvadratmeter", 
            "Kostnadsestimering for maling av 100m2"
        ]
        
        for test_query in queries:
            print(f"\n🧪 Testing: '{test_query}'")
            result = await agent.process(test_query)
            analysis = agent._analyze_renovation_query(test_query)
            
            print(f"📋 Type: {analysis['type']}")
            print(f"📐 Area: {analysis.get('area', 'Not detected')}")
            print(f"💰 Cost: {result.get('total_cost', 0):,.0f} NOK")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_painting_query())