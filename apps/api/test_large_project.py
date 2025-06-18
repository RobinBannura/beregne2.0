#!/usr/bin/env python3
"""
Test large project query with sparkling and painting
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_large_project():
    """Test large sparkling and painting project"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        query = "hva vil det koste å sparkle og male et nytt hus på 150 kvm?"
        print(f"🧪 Testing large project: '{query}'")
        print("=" * 70)
        
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
        
        # Check if it's a material and labor calculation
        if 'breakdown' in result:
            print(f"\n🔍 Breakdown:")
            breakdown = result['breakdown']
            for material, calc in breakdown.items():
                print(f"   {material.title()}:")
                print(f"     - Material: {calc.get('material_cost', 0):,.0f} NOK")
                print(f"     - Labor: {calc.get('labor_cost', 0):,.0f} NOK")
                print(f"     - Hours: {calc.get('hours', 0):.1f}")
                print(f"     - Total: {calc.get('total', 0):,.0f} NOK")
        
        if 'calculation_details' in result:
            calc = result['calculation_details']
            print(f"\n🎨 Paint calculation details:")
            print(f"   Paint needed: {calc.get('liters_needed', 0):.1f} liters")
            print(f"   Work hours: {calc.get('work_hours', 0):.1f} hours")
            print(f"   Pricing source: {calc.get('pricing_source', 'unknown')}")
            
            if 'rigg_og_drift' in calc:
                rigg = calc['rigg_og_drift']
                print(f"   Rigg og drift: {rigg.get('total_rigg_cost', 0):,.0f} NOK")
        
        print(f"\n📝 Response preview:")
        response = result.get('response', '')
        if len(response) > 800:
            print(response[:800] + "...")
        else:
            print(response)
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_large_project())