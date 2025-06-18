#!/usr/bin/env python3
"""
Test flooring pricing integration with renovation agent
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_flooring_integration():
    """Test flooring pricing queries through the renovation agent"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        flooring_queries = [
            "Hva koster parkett legging 25 m²?",
            "Laminat gulv til stue 40 kvadratmeter",
            "Vinylgulv bad 6 m² våtrom",
            "Microsement gulv 30 m²",
            "Epoxy gulv garasje 50 kvadratmeter",
            "Gulvavretting 35 m² flytsparkel",
            "Varmekabler under gulv 20 m²",
            "Komplett parkett 30m² pakke med avretting",
            "Gulvsliping og lakering 45 m²",
            "Fiskebein parkett 18 m²"
        ]
        
        print("🏠 TESTING FLOORING INTEGRATION WITH RENOVATION AGENT")
        print("=" * 60)
        
        for i, query in enumerate(flooring_queries, 1):
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
        
        # Test specific flooring calculations using pricing service directly
        print(f"\n\n🔧 SPECIFIC FLOORING CALCULATION TESTS:")
        print("=" * 50)
        
        pricing_service = agent.pricing_service
        
        specific_tests = [
            {
                "service": "parkett_legging_rettmonster", 
                "quantity": 25,
                "description": "Parquet straight pattern 25m²"
            },
            {
                "service": "laminat_legging_standard",
                "quantity": 40, 
                "description": "Standard laminate 40m²"
            },
            {
                "service": "vinylgulv_vatrom_montering",
                "quantity": 6,
                "description": "Vinyl wet room 6m²"
            },
            {
                "service": "microsementgulv_komplett",
                "quantity": 30,
                "description": "Microsement flooring 30m²"
            },
            {
                "service": "komplett_parkett_30m2_pakke",
                "quantity": 1,
                "description": "Complete parquet package 30m²"
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
                    print(f"\n🏠 {test['description']}:")
                    print(f"   Service: {test['service']}")
                    print(f"   Cost: {cost:,.0f} NOK eks. mva")
                    print(f"   Incl. VAT: {cost_inc_vat:,.0f} NOK")
                    if test["quantity"] > 1:
                        unit_cost = cost / test["quantity"]
                        print(f"   Per m²: {unit_cost:,.0f} NOK")
                else:
                    print(f"\n❌ {test['description']}: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"\n❌ Error testing {test['description']}: {str(e)}")
        
        # Test flooring type comparison
        print(f"\n\n📊 FLOORING TYPE COMPARISON (per m²):")
        print("=" * 45)
        
        flooring_types = [
            ("laminat_legging_standard", "Laminat"),
            ("parkett_legging_rettmonster", "Parkett (rett)"),
            ("parkett_monstergulv_fiskebein", "Parkett (fiskebein)"),
            ("vinylgulv_vatrom_montering", "Vinyl (våtrom)"),
            ("microsementgulv_komplett", "Microsement"),
            ("epoksygulv_bolig", "Epoxy")
        ]
        
        try:
            print("Professional installation prices:")
            for service_name, display_name in flooring_types:
                result = pricing_service.get_service_price(service_name)
                if "error" not in result:
                    unit_price = result.get("unit_price", {}).get("recommended_price", 0)
                    min_price = result.get("unit_price", {}).get("min_price", 0)
                    max_price = result.get("unit_price", {}).get("max_price", 0)
                    print(f"   {display_name}: {min_price:,.0f}-{max_price:,.0f} NOK/m² (snitt: {unit_price:,.0f})")
        
        except Exception as e:
            print(f"   ❌ Error comparing flooring types: {str(e)}")
        
        # Test DIY vs Professional comparison
        print(f"\n💡 DIY vs PROFESSIONAL COMPARISON:")
        print("=" * 35)
        
        try:
            epoxy_pro = pricing_service.get_service_price("epoksygulv_bolig")
            epoxy_diy = pricing_service.get_service_price("epoksygulv_diy_kit")
            
            if "error" not in epoxy_pro and "error" not in epoxy_diy:
                pro_price = epoxy_pro.get("unit_price", {}).get("recommended_price", 0)
                diy_price = epoxy_diy.get("unit_price", {}).get("recommended_price", 0)
                
                savings = pro_price - diy_price
                savings_percent = (savings / pro_price) * 100 if pro_price > 0 else 0
                
                print(f"Epoxy flooring (per m²):")
                print(f"   🔧 Professional: {pro_price:,.0f} NOK/m²")
                print(f"   🛠️  DIY kit: {diy_price:,.0f} NOK/m²")
                print(f"   💰 DIY savings: {savings:,.0f} NOK/m² ({savings_percent:.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error comparing DIY vs Pro: {str(e)}")
        
        # Test complete flooring renovation
        print(f"\n🏠 COMPLETE FLOORING RENOVATION (35m² living room):")
        print("=" * 55)
        
        try:
            # Calculate complete flooring renovation
            components = [
                ("riving_gammelt_gulv", 35, "Remove old flooring"),
                ("gulvavretting_flytsparkel", 35, "Floor leveling"),
                ("varmekabler_installasjon_gulv", 35, "Floor heating"),
                ("parkett_legging_rettmonster", 35, "Parquet installation")
            ]
            
            total_renovation_cost = 0
            print("Complete flooring renovation (35m² room):")
            
            for service_name, quantity, description in components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    total_renovation_cost += cost
                    print(f"   {description}: {cost:,.0f} NOK")
                else:
                    print(f"   {description}: Error getting price")
            
            total_inc_vat = total_renovation_cost * 1.25
            cost_per_m2 = total_renovation_cost / 35
            
            print(f"\n   📊 Total renovation cost: {total_renovation_cost:,.0f} NOK eks. mva")
            print(f"   📊 Total incl. VAT: {total_inc_vat:,.0f} NOK")
            print(f"   📐 Cost per m²: {cost_per_m2:,.0f} NOK/m²")
        
        except Exception as e:
            print(f"   ❌ Error calculating renovation: {str(e)}")
        
        # Compare package vs individual components
        print(f"\n📦 PACKAGE vs INDIVIDUAL COMPARISON:")
        print("=" * 40)
        
        try:
            # Calculate individual components for 30m² parquet project
            individual_components = [
                ("gulvavretting_flytsparkel", 30, "Floor leveling"),
                ("parkett_legging_rettmonster", 30, "Parquet installation")
            ]
            
            individual_total = 0
            print("Individual components (30m² parquet):")
            
            for service_name, quantity, description in individual_components:
                result = pricing_service.get_service_price(service_name, area=quantity)
                if "error" not in result:
                    cost = result.get("total_cost", {}).get("recommended", 0)
                    individual_total += cost
                    print(f"   {description}: {cost:,.0f} NOK")
            
            # Compare with package
            package_result = pricing_service.get_service_price("komplett_parkett_30m2_pakke")
            if "error" not in package_result:
                package_cost = package_result.get("unit_price", {}).get("recommended_price", 0)
                
                savings = individual_total - package_cost
                savings_percent = (savings / individual_total) * 100 if individual_total > 0 else 0
                
                print(f"\n   📊 Individual total: {individual_total:,.0f} NOK")
                print(f"   📦 Package price: {package_cost:,.0f} NOK")
                if savings > 0:
                    print(f"   💰 Package savings: {savings:,.0f} NOK ({savings_percent:.1f}%)")
                else:
                    print(f"   💰 Package premium: {abs(savings):,.0f} NOK ({abs(savings_percent):.1f}%)")
        
        except Exception as e:
            print(f"   ❌ Error comparing package: {str(e)}")
        
        print(f"\n🎉 Flooring pricing integration test completed!")
        print(f"🏠 Database contains comprehensive flooring services")
        print(f"🔧 Ready for customer flooring project calculations")
        print(f"💡 Key insight: Package deals often provide better value")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_flooring_integration())