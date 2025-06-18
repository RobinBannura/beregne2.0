#!/usr/bin/env python3
"""
Debug the agent responses
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def debug_agent():
    """Debug agent responses"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        query = "Pris på maling av 100 kvm"
        print(f"🧪 Debug query: '{query}'")
        
        result = await agent.process(query)
        
        print(f"📊 Full result:")
        for key, value in result.items():
            if key == "response":
                print(f"  {key}: {value[:200]}...")  # Truncate long response
            else:
                print(f"  {key}: {value}")
        
        # Also test the analysis step
        analysis = agent._analyze_renovation_query(query)
        print(f"\n🔍 Query analysis:")
        for key, value in analysis.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_agent())