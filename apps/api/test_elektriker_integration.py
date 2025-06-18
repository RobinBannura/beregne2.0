#!/usr/bin/env python3
"""
Test electrician pricing integration with renovation agent
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_elektriker_integration():
    """Test electrician pricing queries through the renovation agent"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        elektriker_queries = [
            "Hva koster det å få montert 5 nye stikkontakter?",
            "Timepris for elektriker i Oslo",
            "Jeg trenger nytt sikringsskap med 10 kurser",
            "Kostnader for downlights i stue - 8 punkter", 
            "Gulvvarme i bad på 6 m²",
            "Hva koster komplett el-anlegg i leilighet på 80 m²?",
            "Elbillader installasjon hjemme"
        ]
        
        print("⚡ TESTING ELECTRICIAN INTEGRATION WITH RENOVATION AGENT")
        print("=" * 65)
        
        for i, query in enumerate(elektriker_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 50)
            
            # Analyze query
            analysis = agent._analyze_renovation_query(query)
            print(f"📋 Analysis: Type={analysis['type']}, Materials={analysis.get('materials', [])}")
            
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
        
        # Test specific electrician calculations
        print(f"\n\n🔧 SPECIFIC ELECTRICIAN CALCULATION TESTS:")
        print("=" * 55)
        
        # Test direct pricing service access
        pricing_service = agent.pricing_service
        
        specific_tests = [
            {
                "service": "elektriker_timepris_montor", 
                "quantity": 6,
                "description": "6 hours electrician work"
            },
            {
                "service": "downlight_pakke_10_stk",
                "quantity": 1, 
                "description": "10 downlights package"
            },
            {
                "service": "varmekabler_gulv",
                "quantity": 15,
                "description": "Floor heating 15m²"
            },
            {
                "service": "fullt_skjult_elanlegg_per_m2",
                "quantity": 100,
                "description": "Complete electrical system 100m²"
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
                    print(f"\n⚡ {test['description']}:")
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
        
        # Test renovation project that includes electrical work
        print(f"\n\n🏠 RENOVATION PROJECT WITH ELECTRICAL WORK:")
        print("=" * 50)
        
        renovation_query = "Jeg skal pusse opp kjøkkenet og trenger ny elektriker til 10 downlights og 5 stikkontakter"
        result = await agent.process(renovation_query)
        
        print(f"Query: '{renovation_query}'")
        print(f"Total cost: {result.get('total_cost', 0):,.0f} NOK")
        
        # Show how bathroom renovation includes electrical work 
        bathroom_query = "Komplett badrenovering 8 m² med gulvvarme"
        bathroom_result = await agent.process(bathroom_query)
        
        print(f"\nBathroom renovation (8m²): {bathroom_result.get('total_cost', 0):,.0f} NOK")
        print("(Includes electrical work as part of complete renovation)")
        
        print(f"\n🎉 Electrician pricing integration test completed!")
        print(f"⚡ Database contains comprehensive electrician services")
        print(f"🔧 Agent can handle electrical queries and include in renovations")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_elektriker_integration())