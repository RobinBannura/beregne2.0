#!/usr/bin/env python3
"""
Test the pricing service directly
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService

def test_pricing_service():
    """Test pricing service directly"""
    
    print("🧪 Testing PricingService directly")
    print("=" * 40)
    
    try:
        # Initialize database session
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        # Test basic service pricing
        services = ["maling", "flislegging_vegg", "laminat_legging"]
        
        for service in services:
            print(f"\n📋 Testing service: {service}")
            result = pricing_service.get_service_price(service, area=100)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Service found: {service}")
                print(f"💰 Unit price: {result.get('unit_price', {})}")
                print(f"📊 Total cost: {result.get('total_cost', {})}")
        
        # Test with specific area
        print(f"\n🎯 Testing maling with 100 m² area")
        result = pricing_service.get_service_price("maling", area=100)
        print(f"Result: {result}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pricing_service()