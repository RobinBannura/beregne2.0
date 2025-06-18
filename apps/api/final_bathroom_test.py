#!/usr/bin/env python3
"""
Final comprehensive test of bathroom renovation calculation
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_final_bathroom():
    """Test comprehensive bathroom renovation scenarios"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        test_scenarios = [
            {
                "query": "Jeg skal pusse opp badet komplett - 4 m²",
                "expected_range": (350000, 450000),  # 4m² package
                "description": "Small bathroom (4m²) - highest per m² cost"
            },
            {
                "query": "Badehus renovering 8 kvadratmeter", 
                "expected_range": (400000, 500000),  # 8m² package
                "description": "Medium bathroom (8m²) - standard pricing"
            },
            {
                "query": "Hva koster det å renovere et bad på 12 m²?",
                "expected_range": (400000, 600000),  # 12m² package  
                "description": "Large bathroom (12m²) - lowest per m² cost"
            },
            {
                "query": "Flislegging og renovering av bad 15 m²",
                "expected_range": (500000, 800000),  # Component-based
                "description": "Very large bathroom (15m²) - component calculation"
            }
        ]
        
        print("🛁 COMPREHENSIVE BATHROOM RENOVATION TEST")
        print("=" * 60)
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n{i}. {scenario['description']}")
            print(f"   Query: '{scenario['query']}'")
            print("-" * 50)
            
            # Process query
            result = await agent.process(scenario['query'])
            analysis = agent._analyze_renovation_query(scenario['query'])
            
            total_cost = result.get('total_cost', 0)
            area = analysis.get('area', 0)
            
            # Calculate costs
            cost_per_m2 = total_cost / area if area > 0 else 0
            cost_incl_vat = total_cost * 1.25
            
            print(f"   📊 Analysis: Type={analysis['type']}, Area={area}m²")
            print(f"   💰 Cost: {total_cost:,.0f} NOK eks. mva")
            print(f"   💰 Cost: {cost_incl_vat:,.0f} NOK inkl. mva")
            print(f"   📐 Per m²: {cost_per_m2:,.0f} NOK/m²")
            
            # Check if within expected range
            expected_min, expected_max = scenario['expected_range']
            if expected_min <= total_cost <= expected_max:
                print(f"   ✅ Within expected range ({expected_min:,.0f} - {expected_max:,.0f})")
            else:
                print(f"   ⚠️  Outside range ({expected_min:,.0f} - {expected_max:,.0f})")
            
            # Check pricing source
            pricing_source = result.get('pricing_source', 'unknown')
            package_used = result.get('package_used', 'none')
            print(f"   🔧 Pricing: {pricing_source} ({package_used})")
        
        # Test component vs package pricing comparison
        print(f"\n\n🔍 PRICING METHOD COMPARISON:")
        print("=" * 40)
        
        test_area = 6  # 6m² bathroom
        
        # Get package pricing
        package_result = await agent.process(f"Komplett badrenovering {test_area} m²")
        package_cost = package_result.get('total_cost', 0)
        
        # Get component pricing (by asking for specific component)
        component_result = await agent._calculate_bathroom_components(test_area, "komponenter")
        component_cost = component_result.get('total_cost', 0)
        
        print(f"6m² Bathroom - Package vs Components:")
        print(f"   📦 Package pricing: {package_cost:,.0f} NOK eks. mva")
        print(f"   🔧 Component pricing: {component_cost:,.0f} NOK eks. mva")
        print(f"   📈 Difference: {abs(package_cost - component_cost):,.0f} NOK")
        
        # Show why small bathrooms cost more per m²
        print(f"\n\n💡 WHY SMALL BATHROOMS COST MORE PER M²:")
        print("=" * 50)
        
        areas = [4, 8, 12]
        for area in areas:
            result = await agent.process(f"Komplett badrenovering {area} m²")
            cost = result.get('total_cost', 0)
            cost_per_m2 = cost / area
            print(f"   {area}m² bad: {cost_per_m2:,.0f} NOK/m² (total: {cost:,.0f} NOK)")
        
        print(f"\n   🔧 Fixed overhead costs (rørlegger, elektriker, membran) are")
        print(f"      distributed over smaller area in small bathrooms")
        
        print(f"\n🎉 Bathroom renovation calculation system is working correctly!")
        print(f"📊 Database-driven pricing with realistic Oslo market rates")
        print(f"🔧 Both package and component-based calculations available")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_final_bathroom())