#!/usr/bin/env python3
"""
Test sparkling pricing from database
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService

def test_sparkling_pricing():
    """Test sparkling pricing and combined calculation"""
    
    try:
        db = SessionLocal()
        pricing_service = PricingService(db)
        
        area = 150
        
        print(f"🧪 Testing sparkling + painting for {area} m²")
        print("=" * 50)
        
        # Test sparkling pricing
        print("1. Sparkling pricing:")
        sparkling_result = pricing_service.get_service_price("sparkling", area=area)
        if "error" in sparkling_result:
            print(f"   ❌ Sparkling error: {sparkling_result['error']}")
        else:
            sparkling_cost = sparkling_result.get("total_cost", {}).get("recommended", 0)
            sparkling_unit = sparkling_result.get("unit_price", {}).get("recommended_price", 0)
            print(f"   ✅ Sparkling: {sparkling_cost:,.0f} NOK ({sparkling_unit:.0f} NOK/m²)")
        
        # Test painting pricing  
        print("\n2. Painting pricing:")
        painting_result = pricing_service.get_service_price("maling", area=area)
        if "error" in painting_result:
            print(f"   ❌ Painting error: {painting_result['error']}")
        else:
            painting_cost = painting_result.get("total_cost", {}).get("recommended", 0)
            painting_unit = painting_result.get("unit_price", {}).get("recommended_price", 0)
            print(f"   ✅ Painting: {painting_cost:,.0f} NOK ({painting_unit:.0f} NOK/m²)")
        
        # Calculate combined cost
        if "error" not in sparkling_result and "error" not in painting_result:
            base_cost = sparkling_cost + painting_cost
            
            # Estimate rigg og drift for combined job (larger job = more efficient)
            # For combined jobs, rigg costs are shared
            combined_rigg_base = 4000  # Higher base for combined job
            area_factor = max(1.0, area / 50)
            rigg_cost = combined_rigg_base * area_factor
            
            total_cost = base_cost + rigg_cost
            
            print(f"\n3. Combined calculation:")
            print(f"   Sparkling: {sparkling_cost:,.0f} NOK")
            print(f"   Painting: {painting_cost:,.0f} NOK")
            print(f"   Rigg og drift: {rigg_cost:,.0f} NOK")
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"   TOTAL: {total_cost:,.0f} NOK")
            
            print(f"\n💡 Project details:")
            print(f"   - Area: {area} m²")
            print(f"   - Sparkling rate: {sparkling_unit:.0f} NOK/m²")
            print(f"   - Painting rate: {painting_unit:.0f} NOK/m²")
            print(f"   - Combined rate: {total_cost/area:.0f} NOK/m²")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sparkling_pricing()