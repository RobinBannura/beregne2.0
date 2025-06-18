#!/usr/bin/env python3
"""
Test the painting inquiry handler specifically
"""

import asyncio
from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

async def test_painting_handler():
    """Test painting inquiry handler"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        # Mock analysis that would be passed to the handler
        analysis = {
            "type": "painting_specific",
            "area": 100.0,
            "specific_details": {
                "ceiling_painting": False, 
                "wall_painting": False, 
                "many_windows": False, 
                "old_wallpaper": False, 
                "rough_surface": False, 
                "quality_level": False
            }
        }
        
        query = "maling av 100 kvm"
        
        print(f"🧪 Testing _handle_painting_inquiry directly")
        result = await agent._handle_painting_inquiry(analysis, query)
        
        print(f"📊 Result:")
        for key, value in result.items():
            if key == "response":
                print(f"  {key}: {value[:200]}...")  # Truncate long response
            else:
                print(f"  {key}: {value}")
        
        # Also test the calculation details
        calc_details = result.get("calculation_details", {})
        print(f"\n🔍 Calculation details:")
        for key, value in calc_details.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_painting_handler())