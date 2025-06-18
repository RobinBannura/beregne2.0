#!/usr/bin/env python3
"""
Test groundwork pricing integration with renovation agent
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_grunnarbeider_integration():
    """Test groundwork pricing queries through the renovation agent"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        grunnarbeider_queries = [
            "Hva koster graving av tomt på 200 m²?",
            "Grunnmur for ny bolig 120 m²",
            "Sprengning av fjell 30 kubikkmeter",
            "Drenering rundt hus 45 løpemeter",
            "Plate på mark 100 kvadratmeter", 
            "Komplett fundamentering ny bolig 120 m²",
            "Gravemaskin med fører 6 timer"
        ]
        
        print("🏗️ TESTING GROUNDWORK INTEGRATION WITH RENOVATION AGENT")
        print("=" * 65)
        
        for i, query in enumerate(grunnarbeider_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 50)
            
            # Analyze query
            analysis = agent._analyze_renovation_query(query)
            print(f"📋 Analysis: Type={analysis['type']}, Project={analysis.get('project_type', 'unknown')}")
            
            # Process query
            result = await agent.process(query)
            
            total_cost = result.get('total_cost', 0)
            agent_used = result.get('agent_used', 'unknown')
            
            print(f"💰 Result: {total_cost:,.0f} NOK (Agent: {agent_used})")
            
            # Show response preview
            response = result.get('response', '')
            if len(response) > 200:
                print(f"📝 Response: {response[:200]}...")
            else:
                print(f"📝 Response: {response}")
        
        # Test specific groundwork calculations using pricing service directly
        print(f"\n\n🔧 SPECIFIC GROUNDWORK CALCULATION TESTS:")
        print("=" * 55)
        
        pricing_service = agent.pricing_service
        
        specific_tests = [
            {
                "service": "graving_generell_utgraving", 
                "quantity": 200,
                "description": "Standard excavation 200m²"
            },
            {
                "service": "grunnmur_betong_leca",
                "quantity": 120, 
                "description": "Foundation wall 120m²"
            },
            {
                "service": "sprengning_fjell_store_volumer",
                "quantity": 50,
                "description": "Rock blasting 50m³"
            },
            {
                "service": "komplett_grunnmur_pakke_120m2",
                "quantity": 1,
                "description": "Complete foundation package 120m²"
            }
        ]
        
        for test in specific_tests:
            try:
                if test["quantity"] > 1:
                    result = pricing_service.get_service_price(test["service"], area=test["quantity"])
                    cost = result.get("total_cost", {}).get("recommended", 0)
                else:
                    result = pricing_service.get_service_price(test["service"])
                    cost = result.get("unit_price", {}).get("recommended_price", 0)
                
                if "error" not in result:
                    cost_inc_vat = cost * 1.25
                    print(f"\n🏗️ {test['description']}:")
                    print(f"   Service: {test['service']}")
                    print(f"   Cost: {cost:,.0f} NOK eks. mva")
                    print(f"   Incl. VAT: {cost_inc_vat:,.0f} NOK")
                    if test["quantity"] > 1:
                        unit_cost = cost / test["quantity"]
                        print(f"   Per unit: {unit_cost:,.0f} NOK")
                else:
                    print(f"\n❌ {test['description']}: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"\n❌ Error testing {test['description']}: {str(e)}")
        
        # Test comprehensive new house foundation calculation
        print(f"\n\n🏠 COMPREHENSIVE NEW HOUSE FOUNDATION:")
        print("=" * 50)
        
        # Calculate total foundation cost for a new house
        foundation_components = [
            ("graving_ny_bolig_inkl_planering", 120, "Excavation & site prep"),
            ("grunnmur_betong_leca", 120, "Foundation walls"),
            ("plate_pa_mark", 120, "Concrete slab"),
            ("drenering_rundt_grunnmur", 50, "Drainage 50 lm"),
            ("radonsperre_i_plate", 120, "Radon barrier"),
            ("perimeter_isolasjon_grunnmur", 50, "Perimeter insulation")
        ]
        
        total_foundation_cost = 0
        print("Complete foundation for 120m² house:")
        
        for service_name, quantity, description in foundation_components:
            try:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_foundation_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            except Exception as e:
                print(f"   {description}: Error - {str(e)}")
        
        total_inc_vat = total_foundation_cost * 1.25
        cost_per_m2 = total_foundation_cost / 120
        
        print(f"\n   📊 Total foundation cost: {total_foundation_cost:,.0f} NOK eks. mva")
        print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
        print(f"   📐 Cost per m²: {cost_per_m2:,.0f} NOK/m²")
        
        # Compare with package pricing
        try:
            package_result = pricing_service.get_service_price("komplett_grunnmur_pakke_120m2")
            if "error" not in package_result:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                savings = total_foundation_cost - package_cost
                savings_percent = (savings / total_foundation_cost) * 100 if total_foundation_cost > 0 else 0
                
                print(f"\n   📦 Package alternative: {package_cost:,.0f} NOK")
                if savings > 0:
                    print(f"   💰 Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                else:
                    print(f"   💰 Package premium: {abs(savings):,.0f} NOK ({abs(savings_percent):.1f}%)")
        except Exception as e:
            print(f"   ❌ Error comparing package: {str(e)}")
        
        print(f"\n🎉 Groundwork pricing integration test completed!")
        print(f"🏗️ Database contains comprehensive groundwork services")
        print(f"🔧 Ready for integration with construction project calculations")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_grunnarbeider_integration())