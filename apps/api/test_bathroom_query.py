#!/usr/bin/env python3
"""
Test bathroom renovation queries with new pricing data
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_bathroom_queries():
    """Test various bathroom renovation queries"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        bathroom_queries = [
            "Hva koster det å renovere et bad på 5 m²?",
            "Pris på komplett badrenovering 8 kvadratmeter", 
            "Jeg vil renovere badet mitt på 6 m²",
            "Hva koster flislegging i bad på 10 m²?"
        ]
        
        print("🛁 TESTING BATHROOM RENOVATION QUERIES")
        print("=" * 50)
        
        for i, query in enumerate(bathroom_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 40)
            
            # Process query
            result = await agent.process(query)
            analysis = agent._analyze_renovation_query(query)
            
            print(f"📋 Analysis:")
            print(f"   Type: {analysis['type']}")
            print(f"   Area: {analysis.get('area', 'Not detected')} m²")
            print(f"   Project type: {analysis.get('project_type', 'Unknown')}")
            
            print(f"\n💰 Result:")
            print(f"   Agent: {result.get('agent_used')}")
            print(f"   Total cost: {result.get('total_cost', 0):,.0f} NOK")
            
            # Show response preview
            response = result.get('response', '')
            if len(response) > 300:
                print(f"   Response: {response[:300]}...")
            else:
                print(f"   Response: {response}")
            
            print()
        
        # Test a specific bathroom calculation
        print("\n🎯 DETAILED BATHROOM TEST:")
        print("Testing: 'Komplett badrenovering 6 m²'")
        
        result = await agent.process("Komplett badrenovering 6 m²")
        total_cost = result.get('total_cost', 0)
        
        # Expected range for 6m² bathroom (between 4m² and 8m² packages)
        # 4m²: 440k inkl mva, 8m²: 536k inkl mva
        # 6m² should be around 480-500k inkl mva
        expected_min = 380000  # eks mva
        expected_max = 450000  # eks mva
        
        print(f"Total cost: {total_cost:,.0f} NOK eks. mva")
        print(f"Inkl. mva: {total_cost * 1.25:,.0f} NOK")
        print(f"Per m²: {total_cost / 6:,.0f} NOK/m²")
        
        if expected_min <= total_cost <= expected_max:
            print("✅ Cost within expected range for 6m² bathroom")
        else:
            print(f"⚠️  Cost outside expected range ({expected_min:,.0f} - {expected_max:,.0f})")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_bathroom_queries())