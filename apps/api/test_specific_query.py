#!/usr/bin/env python3
"""
Test the specific query from user
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_user_query():
    """Test the user's specific query"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        query = "hva koster det å male et rom på 50 kvm kun vegger?"
        print(f"🧪 Testing user query: '{query}'")
        print("=" * 60)
        
        # Process the query
        result = await agent.process(query)
        analysis = agent._analyze_renovation_query(query)
        
        print(f"📋 Query analysis:")
        print(f"   Type: {analysis['type']}")
        print(f"   Area: {analysis.get('area', 'Not detected')} m²")
        print(f"   Materials: {analysis.get('materials', [])}")
        print(f"   Details: {analysis.get('specific_details', {})}")
        
        print(f"\n📊 Result:")
        print(f"   Agent: {result.get('agent_used')}")
        print(f"   Total cost: {result.get('total_cost', 0):,.0f} NOK")
        
        if 'calculation_details' in result:
            calc = result['calculation_details']
            print(f"   Paint needed: {calc.get('liters_needed', 0):.1f} liters")
            print(f"   Work hours: {calc.get('work_hours', 0):.1f} hours")
            print(f"   Pricing source: {calc.get('pricing_source', 'unknown')}")
        
        print(f"\n📝 Response preview:")
        response = result.get('response', '')
        if len(response) > 500:
            print(response[:500] + "...")
        else:
            print(response)
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_user_query())