#!/usr/bin/env python3
"""
Adjust pricing to match real market experience
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import PricingData

def adjust_house_pricing():
    """Adjust pricing based on real market experience"""
    
    try:
        db = SessionLocal()
        
        print("🔧 Adjusting pricing to match market reality...")
        print("=" * 50)
        
        # Current result: 69k eks mva = 86k inkl mva
        # Target: 130-200k inkl mva = 104-160k eks mva
        # Need to increase by ~50-80%
        
        # Update maling pricing to be more realistic for whole house projects
        # Find the maling service
        maling_pricing = db.query(PricingData).filter(
            PricingData.service_type_id == 1,  # Assuming maling is service type 1
            PricingData.source == "market_research"
        ).first()
        
        if maling_pricing:
            # Increase pricing to reflect whole house complexity
            # From 80-150 to 140-220 NOK/m² 
            maling_pricing.min_price = 140
            maling_pricing.max_price = 220
            maling_pricing.avg_price = 180
            
            print("✅ Updated maling pricing:")
            print(f"   From: 80-150 NOK/m²")
            print(f"   To: 140-220 NOK/m²")
            
        db.commit()
        
        # Recalculate market rates
        pricing_service = PricingService(db)
        pricing_service.update_market_rates("Oslo")
        
        print("\n📊 Testing updated pricing:")
        
        # Test the new pricing
        result = pricing_service.get_service_price("maling", area=420)  # 150m² house = 420m² paintable
        
        if "error" not in result:
            total = result.get("total_cost", {}).get("recommended", 0)
            unit_price = result.get("unit_price", {}).get("recommended_price", 0)
            
            # Add rigg og drift estimate
            rigg_cost = 15000  # Estimated for large house
            total_with_rigg = total + rigg_cost
            total_inc_vat = total_with_rigg * 1.25
            
            print(f"   420 m² malerflate: {total:,.0f} NOK")
            print(f"   Unit price: {unit_price:.0f} NOK/m²")
            print(f"   + Rigg og drift: {rigg_cost:,.0f} NOK")
            print(f"   = Total eks. mva: {total_with_rigg:,.0f} NOK")
            print(f"   = Total inkl. mva: {total_inc_vat:,.0f} NOK")
            
            if 130000 <= total_inc_vat <= 200000:
                print(f"   ✅ Perfect match with experience!")
            else:
                print(f"   ⚠️  Still need adjustment")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Adjustment failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    adjust_house_pricing()