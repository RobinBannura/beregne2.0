#!/usr/bin/env python3
"""
Test the calculation methods directly
"""

from app.agents.enhanced_renovation_agent import EnhancedRenovationAgent

def test_calculation():
    """Test calculation methods directly"""
    
    try:
        agent = EnhancedRenovationAgent()
        
        # Test _calculate_advanced_painting directly
        area = 100
        details = {}
        
        print(f"🧪 Testing _calculate_advanced_painting with {area} m²")
        result = agent._calculate_advanced_painting(area, details)
        
        print(f"📊 Result:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        
        # Test database pricing service directly
        print(f"\n🧪 Testing pricing service directly")
        pricing_result = agent.pricing_service.get_service_price("maling", area=area)
        print(f"💰 Pricing result: {pricing_result}")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_calculation()