#!/usr/bin/env python3
"""
Comprehensive test of all new construction categories integration
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_comprehensive_integration():
    """Test all new construction categories through the renovation agent"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        # Test queries for all new categories
        test_queries = [
            # Carpentry/Building work
            ("Lettvegg 10 m² med dør", "tomrer_bygg"),
            ("Nedforet himling 20 m²", "tomrer_bygg"),
            ("Tømrer timepris", "tomrer_bygg"),
            ("Montering 3 innerdører", "tomrer_bygg"),
            ("Listverk 15 løpemeter", "tomrer_bygg"),
            
            # Roofing and cladding
            ("Takomlegging 100 m²", "tak_ytterkledning"),
            ("Takrenner 40 meter", "tak_ytterkledning"),
            ("Etterisolering 80 m² vegg", "tak_ytterkledning"),
            ("Ny kledning 60 m²", "tak_ytterkledning"),
            ("Takvindu 2 stk", "tak_ytterkledning"),
            
            # Insulation and sealing
            ("Blåseisolasjon loft 90 m²", "isolasjon_tetting"),
            ("Dampsperre 70 m²", "isolasjon_tetting"),
            ("Lufttetting komplett hus", "isolasjon_tetting"),
            ("Energioppgradering 150 m²", "isolasjon_tetting"),
            ("Veggisolasjon 40 m²", "isolasjon_tetting"),
            
            # Windows and doors
            ("Vinduer 8 stk standard", "vinduer_dorer"),
            ("Ytterdør ny", "vinduer_dorer"),
            ("Innerdører 5 stk", "vinduer_dorer"),
            ("Takvindu 1 stk", "vinduer_dorer"),
            ("Vindusutskifting hus", "vinduer_dorer"),
            
            # Existing categories should still work
            ("Bad 5 m² oppussing", "bad_komplett"),
            ("Kjøkken komplett", "kjøkken_detaljert"),
            ("Elektriker 8 timer", "elektriker_arbeid"),
            ("Graving tomt 200 m²", "grunnarbeider"),
            ("Parkett 25 m²", "gulvarbeider"),
        ]
        
        print("🏗️ COMPREHENSIVE CONSTRUCTION CATEGORIES TEST")
        print("=" * 60)
        print("Testing all construction categories for proper recognition and cost calculation")
        print("=" * 60)
        
        successful_tests = 0
        failed_tests = []
        category_results = {}
        
        for i, (query, expected_category) in enumerate(test_queries, 1):
            print(f"\n{i:2d}. Testing: '{query}'")
            print("-" * 50)
            
            try:
                # Analyze query
                analysis = agent._analyze_renovation_query(query)
                detected_category = analysis.get('project_type', 'unknown')
                analysis_type = analysis.get('type', 'unknown')
                
                print(f"    📋 Detected category: {detected_category}")
                print(f"    📋 Analysis type: {analysis_type}")
                
                # Process query
                result = await agent.process(query)
                
                total_cost = result.get('total_cost', 0)
                agent_used = result.get('agent_used', 'unknown')
                
                print(f"    💰 Cost: {total_cost:,.0f} NOK")
                print(f"    🤖 Agent: {agent_used}")
                
                # Check if categorization is correct
                if detected_category == expected_category or detected_category in expected_category:
                    print(f"    ✅ Category match: {detected_category}")
                    successful_tests += 1
                    
                    # Track results by category
                    if expected_category not in category_results:
                        category_results[expected_category] = []
                    category_results[expected_category].append({
                        'query': query,
                        'cost': total_cost,
                        'analysis_type': analysis_type
                    })
                else:
                    print(f"    ❌ Category mismatch: expected {expected_category}, got {detected_category}")
                    failed_tests.append((query, expected_category, detected_category))
                
                # Check for errors
                if 'error' in result:
                    print(f"    ⚠️  Error: {result['error']}")
                    
            except Exception as e:
                print(f"    💥 Test failed: {str(e)}")
                failed_tests.append((query, expected_category, f"Exception: {str(e)}"))
        
        # Summary by category
        print(f"\n{'='*60}")
        print(f"📊 RESULTS BY CATEGORY")
        print(f"{'='*60}")
        
        for category, results in category_results.items():
            avg_cost = sum(r['cost'] for r in results) / len(results) if results else 0
            print(f"\n🏗️ {category.upper()}:")
            print(f"   Tests: {len(results)}")
            print(f"   Avg cost: {avg_cost:,.0f} NOK")
            for result in results:
                print(f"   • {result['query']}: {result['cost']:,.0f} NOK ({result['analysis_type']})")
        
        # Overall summary
        print(f"\n{'='*60}")
        print(f"📈 OVERALL SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successful: {successful_tests}/{len(test_queries)} tests")
        print(f"⏱️  Categories tested: {len(category_results)} different types")
        
        if failed_tests:
            print(f"\n❌ Failed tests:")
            for query, expected, actual in failed_tests:
                print(f"   • '{query}': expected {expected}, got {actual}")
        else:
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"🏗️ Construction calculator now supports:")
            print(f"   🔨 Tømrer/bygg: {len(category_results.get('tomrer_bygg', []))} test cases")
            print(f"   🏠 Tak/ytterkledning: {len(category_results.get('tak_ytterkledning', []))} test cases")
            print(f"   🏠 Isolasjon/tetting: {len(category_results.get('isolasjon_tetting', []))} test cases")
            print(f"   🚪 Vinduer/dører: {len(category_results.get('vinduer_dorer', []))} test cases")
            print(f"   🛁 Bad: {len(category_results.get('bad_komplett', []))} test cases")
            print(f"   🍳 Kjøkken: {len(category_results.get('kjøkken_detaljert', []))} test cases")
            print(f"   ⚡ Elektriker: {len(category_results.get('elektriker_arbeid', []))} test cases")
            print(f"   🏗️ Grunnarbeider: {len(category_results.get('grunnarbeider', []))} test cases")
            print(f"   🏠 Gulvarbeider: {len(category_results.get('gulvarbeider', []))} test cases")
        
        # Show cost ranges by category
        print(f"\n💰 COST RANGES BY CATEGORY:")
        print(f"=" * 40)
        for category, results in category_results.items():
            if results:
                costs = [r['cost'] for r in results]
                min_cost = min(costs)
                max_cost = max(costs)
                print(f"   {category}: {min_cost:,.0f} - {max_cost:,.0f} NOK")
        
        # Key insights
        print(f"\n💡 KEY INSIGHTS:")
        print(f"=" * 20)
        print(f"🏗️ Database now contains comprehensive Oslo/Viken 2025 pricing")
        print(f"📊 Cost estimates range from small repairs to major renovations")
        print(f"🔧 Professional installation pricing with material costs included")
        print(f"💰 Transparent pricing enables informed decision-making")
        print(f"📦 Package deals often provide better value than individual services")
        
        return len(failed_tests) == 0
        
    except Exception as e:
        print(f"❌ Comprehensive test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_comprehensive_integration())