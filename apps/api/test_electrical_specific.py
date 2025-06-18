#!/usr/bin/env python3
"""
Test specific electrical queries that were problematic
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_electrical_specific():
    """Test specific electrical queries"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        test_queries = [
            "Hva koster komplett el-anlegg i leilighet på 80 m²?",
            "Timepris for elektriker i Oslo",
            "5 nye stikkontakter montert",
            "10 downlights i stue", 
            "Gulvvarme bad 8 m²",
            "Nytt sikringsskap med kurser"
        ]
        
        print("⚡ TESTING SPECIFIC ELECTRICAL QUERIES")
        print("=" * 50)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: '{query}'")
            print("-" * 40)
            
            try:
                # Analyze query
                analysis = agent._analyze_renovation_query(query)
                print(f"📋 Analysis: Type={analysis['type']}, Project={analysis['project_type']}")
                
                # Process query
                result = await agent.process(query)
                
                total_cost = result.get('total_cost', 0)
                agent_used = result.get('agent_used', 'unknown')
                
                print(f"💰 Result: {total_cost:,.0f} NOK (Agent: {agent_used})")
                
                # Check for errors
                if 'error' in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"✅ Success")
                    
            except Exception as e:
                print(f"❌ Test failed for '{query}': {str(e)}")
        
        print(f"\n🎉 Electrical query tests completed!")
        
    except Exception as e:
        print(f"❌ Overall test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_electrical_specific())