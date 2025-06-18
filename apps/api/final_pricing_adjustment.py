#!/usr/bin/env python3
"""
Final pricing adjustment to match 130-200k experience
"""

from app.database import SessionLocal
from app.services.pricing_service import PricingService
from app.models.pricing import PricingData

def final_pricing_adjustment():
    """Final adjustment to match real market experience"""
    
    try:
        db = SessionLocal()
        
        print("🎯 Final pricing adjustment for house projects...")
        print("=" * 50)
        
        # Update maling pricing to match your experience
        # Target: 130-200k inkl mva for 150m² house
        # That's 104-160k eks mva
        # For 420m² paintable area = 248-381 NOK/m²
        
        maling_pricing = db.query(PricingData).filter(
            PricingData.service_type_id == 1,
            PricingData.source == "market_research"
        ).first()
        
        if maling_pricing:
            # Set pricing to match your experience
            maling_pricing.min_price = 180  # Lower end
            maling_pricing.max_price = 280  # Higher end
            maling_pricing.avg_price = 230  # Average
            
            print("✅ Final maling pricing update:")
            print(f"   Range: 180-280 NOK/m² malerflate")
            print(f"   Average: 230 NOK/m²")
            
        db.commit()
        
        # Recalculate market rates
        pricing_service = PricingService(db)
        pricing_service.update_market_rates("Oslo")
        
        print("\n📊 Testing final pricing:")
        
        # Test scenarios
        house_area = 150  # m² gulvflate
        paintable_area = house_area * 2.8  # 420 m²
        
        result = pricing_service.get_service_price("maling", area=paintable_area)
        
        if "error" not in result:
            base_cost = result.get("total_cost", {}).get("recommended", 0)
            unit_price = result.get("unit_price", {}).get("recommended_price", 0)
            
            # Realistic rigg og drift for whole house
            rigg_cost = 20000  # Higher for whole house project
            
            total_ex_vat = base_cost + rigg_cost
            total_inc_vat = total_ex_vat * 1.25
            
            print(f"🏠 150 m² hus (420 m² malerflate):")
            print(f"   Maling og sparkling: {base_cost:,.0f} NOK ({unit_price:.0f} NOK/m²)")
            print(f"   Rigg og drift: {rigg_cost:,.0f} NOK")
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"   Total eks. mva: {total_ex_vat:,.0f} NOK")
            print(f"   Total inkl. mva: {total_inc_vat:,.0f} NOK")
            
            if 130000 <= total_inc_vat <= 200000:
                print(f"   ✅ PERFECT MATCH! Within experience range!")
            elif total_inc_vat < 130000:
                print(f"   ⬇️  Below experience range")
            else:
                print(f"   ⬆️  Above experience range")
            
            # Show price breakdown
            print(f"\n💡 Price breakdown:")
            print(f"   {unit_price:.0f} NOK/m² × {paintable_area:.0f} m² = base work")
            print(f"   + {rigg_cost:,.0f} NOK comprehensive rigg/drift")
            print(f"   + 25% MVA")
            print(f"   = {total_inc_vat:,.0f} NOK total")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Adjustment failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_pricing_adjustment()